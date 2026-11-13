"""
BrewBean Coffee Analytics System — Sales Service Layer
Handles server-side calculations, price lookups, and atomic database transactions.
"""

from decimal import Decimal
from datetime import datetime
from app.db import get_db_connection
from app.models.sale import generate_next_invoice_number

def process_and_save_sale(shop_id, customer_id, order_type, payment_method, line_items, discount_amount=0.0, tax_percentage=5.0, campaign_id=None, sale_date=None):
    """
    Validates POS form data, fetches product prices from database, recalculates all totals,
    and saves the transaction atomically within a MySQL transaction block.
    
    Returns the newly created sale_id on success.
    Raises ValueError on validation failures or PyMySQL errors on DB issues.
    """
    if not shop_id or not str(shop_id).isdigit():
        raise ValueError("A valid active store branch must be selected.")

    if not line_items or not isinstance(line_items, list) or len(line_items) == 0:
        raise ValueError("At least one product item must be added to the invoice.")

    if order_type not in ['Dine-in', 'Takeaway', 'Delivery']:
        raise ValueError("Invalid order type selected.")

    if payment_method not in ['Cash', 'UPI', 'Credit Card', 'Debit Card', 'Wallet']:
        raise ValueError("Invalid payment method selected.")

    # Parse customer_id and campaign_id (None if not provided)
    parsed_customer_id = None
    if customer_id and str(customer_id).isdigit() and int(customer_id) > 0:
        parsed_customer_id = int(customer_id)

    parsed_campaign_id = None
    if campaign_id and str(campaign_id).isdigit() and int(campaign_id) > 0:
        parsed_campaign_id = int(campaign_id)

    # Parse discount and tax
    discount = Decimal(str(discount_amount or 0))
    if discount < Decimal('0'):
        raise ValueError("Discount amount cannot be negative.")

    tax_pct = Decimal(str(tax_percentage if tax_percentage is not None else 5.0))
    if tax_pct < Decimal('0'):
        raise ValueError("Tax percentage cannot be negative.")

    # Transaction date
    if not sale_date:
        formatted_sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        formatted_sale_date = sale_date

    connection = get_db_connection()
    try:
        # Step 1: Fetch and validate product prices & active status from DB
        product_ids = [item['product_id'] for item in line_items if 'product_id' in item and str(item['product_id']).isdigit()]
        if not product_ids:
            raise ValueError("No valid product IDs provided in line items.")

        with connection.cursor() as cursor:
            # Query products
            format_strings = ','.join(['%s'] * len(product_ids))
            cursor.execute(f"SELECT product_id, product_name, cost_price, selling_price, status FROM products WHERE product_id IN ({format_strings})", tuple(product_ids))
            db_products = {p['product_id']: p for p in cursor.fetchall()}

        processed_items = []
        subtotal = Decimal('0.00')
        total_cost = Decimal('0.00')

        for item in line_items:
            pid = int(item['product_id'])
            qty = int(item.get('quantity', 1))

            if qty <= 0:
                raise ValueError("Product quantity must be greater than zero.")

            if pid not in db_products:
                raise ValueError(f"Product ID {pid} not found in database.")

            db_prod = db_products[pid]
            if db_prod['status'] != 'Active':
                raise ValueError(f"Product '{db_prod['product_name']}' is inactive and cannot be ordered.")

            unit_price = Decimal(str(db_prod['selling_price']))
            unit_cost = Decimal(str(db_prod['cost_price']))
            item_discount = Decimal(str(item.get('item_discount', 0)))

            item_revenue = (Decimal(qty) * unit_price) - item_discount
            item_cost_total = Decimal(qty) * unit_cost
            item_profit = item_revenue - item_cost_total

            subtotal += item_revenue
            total_cost += item_cost_total

            processed_items.append({
                "product_id": pid,
                "quantity": qty,
                "unit_price": unit_price,
                "item_discount": item_discount,
                "item_revenue": item_revenue,
                "item_cost": item_cost_total,
                "item_profit": item_profit
            })

        if discount > subtotal:
            raise ValueError(f"Discount (₹{discount}) cannot exceed subtotal (₹{subtotal}).")

        # Step 2: Calculate invoice-level tax & totals
        taxable_amount = subtotal - discount
        tax_amount = round((taxable_amount * tax_pct / Decimal('100.0')), 2)
        total_amount = taxable_amount + tax_amount
        total_profit = total_amount - total_cost

        # Generate unique invoice number
        invoice_number = generate_next_invoice_number()

        # Step 3: Atomic MySQL Transaction
        connection.begin()
        with connection.cursor() as cursor:
            # 3a. Insert sales header
            sql_sale = """
                INSERT INTO sales (invoice_number, shop_id, customer_id, campaign_id, sale_date, 
                                   order_type, payment_method, subtotal, discount, tax, 
                                   total_amount, total_cost, total_profit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_sale, (
                invoice_number,
                int(shop_id),
                parsed_customer_id,
                parsed_campaign_id,
                formatted_sale_date,
                order_type,
                payment_method,
                subtotal,
                discount,
                tax_amount,
                total_amount,
                total_cost,
                total_profit
            ))
            sale_id = cursor.lastrowid

            # 3b. Insert sale items
            sql_item = """
                INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, item_discount, 
                                       item_revenue, item_cost, item_profit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            for pi in processed_items:
                cursor.execute(sql_item, (
                    sale_id,
                    pi['product_id'],
                    pi['quantity'],
                    pi['unit_price'],
                    pi['item_discount'],
                    pi['item_revenue'],
                    pi['item_cost'],
                    pi['item_profit']
                ))

        connection.commit()
        return sale_id

    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()
