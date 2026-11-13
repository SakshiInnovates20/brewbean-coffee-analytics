"""
BrewBean Coffee Analytics System — Synthetic Sales Data Generator (Phase 4)
Generates realistic demo sales transactions for multi-branch analytics testing.
"""

import sys
import os
import random
import argparse
from datetime import datetime, timedelta
from decimal import Decimal

# Add parent directory to path so app modules import cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.db import get_db_connection
from app.models.shop import get_all_shops
from app.models.product import get_all_products
from app.models.customer import get_all_customers
from app.models.campaign import get_all_campaigns
from app.services.sales_service import process_and_save_sale

def generate_demo_transactions(count=600, reset_existing=False, confirmed=False):
    """
    Generates synthetic sales invoices with realistic patterns (weekend spikes, morning coffee preference, 
    store branch variations, and campaign attributions) over a 6-month historical period.
    """
    app = create_app()
    with app.app_context():
        connection = get_db_connection()
        try:
            if reset_existing:
                if not confirmed:
                    print("ERROR: Safety Warning! --reset-demo-sales requires explicit '--confirm' flag.")
                    sys.exit(1)
                
                print("WARNING: Deleting existing demo sales and sale_items...")
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM sale_items")
                    cursor.execute("DELETE FROM sales")
                connection.commit()
                print(" -> Existing sales cleared successfully.")

            # Load active lookup entities
            shops = get_all_shops(status_filter='Active')
            products = get_all_products(status_filter='Active')
            customers = get_all_customers()
            campaigns = get_all_campaigns()

            if not shops or not products:
                print("ERROR: Shops or products missing in database. Please run python scripts/init_db.py first.")
                sys.exit(1)

            print(f"Generating {count} synthetic sales invoices...")

            # Date Range: Past 180 days up to today
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)

            # Store weights for realistic performance variation (e.g. Alkapuri and Andheri higher)
            shop_weights = [0.22, 0.15, 0.20, 0.14, 0.16, 0.13]

            payment_methods = ['UPI', 'UPI', 'Cash', 'Credit Card', 'Debit Card', 'Wallet']
            order_types = ['Dine-in', 'Dine-in', 'Takeaway', 'Delivery']

            # Separate products by category for time-of-day weighting
            coffee_products = [p for p in products if p['category_name'] in ['Coffee', 'Cold Beverages', 'Tea']]
            food_products = [p for p in products if p['category_name'] in ['Food', 'Desserts', 'Snacks']]

            created_count = 0
            sale_items_count = 0

            for i in range(count):
                # Random date within past 180 days with weekend weighting
                random_days = random.randint(0, 180)
                dt = start_date + timedelta(days=random_days)

                # Weekend boost: if Saturday or Sunday, higher chance of evening sales
                is_weekend = dt.weekday() >= 5
                
                # Realistic time of day
                if random.random() < 0.45: # 45% Morning coffee (8 AM - 11 AM)
                    hour = random.randint(8, 11)
                elif random.random() < 0.75: # 30% Evening snack (4 PM - 8 PM)
                    hour = random.randint(16, 20)
                else: # 25% Afternoon (12 PM - 3 PM)
                    hour = random.randint(12, 15)

                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                sale_datetime = dt.replace(hour=hour, minute=minute, second=second).strftime('%Y-%m-%d %H:%M:%S')

                # Select shop branch based on weights
                shop = random.choices(shops, weights=shop_weights[:len(shops)], k=1)[0]
                shop_id = shop['shop_id']

                # Customer selection: 65% registered customer, 35% Walk-in
                customer_id = None
                if customers and random.random() < 0.65:
                    cus = random.choice(customers)
                    customer_id = cus['customer_id']

                # Campaign attribution: ~35% sales tied to an active/completed campaign covering sale date
                campaign_id = None
                valid_campaigns = [
                    c for c in campaigns 
                    if str(c['start_date']) <= sale_datetime[:10] <= str(c['end_date'])
                ]
                if valid_campaigns and random.random() < 0.35:
                    campaign_id = random.choice(valid_campaigns)['campaign_id']

                # Select order type & payment method
                order_type = random.choice(order_types)
                payment_method = random.choice(payment_methods)

                # Generate 1 to 4 items per invoice
                num_items = random.choices([1, 2, 3, 4], weights=[0.40, 0.35, 0.18, 0.07], k=1)[0]
                
                selected_products = set()
                line_items = []
                for _ in range(num_items):
                    if hour <= 11 and coffee_products and random.random() < 0.8:
                        prod = random.choice(coffee_products)
                    else:
                        prod = random.choice(products)

                    if prod['product_id'] in selected_products:
                        continue

                    selected_products.add(prod['product_id'])
                    qty = random.choices([1, 2, 3], weights=[0.70, 0.22, 0.08], k=1)[0]
                    line_items.append({
                        "product_id": prod['product_id'],
                        "quantity": qty
                    })

                if not line_items:
                    prod = random.choice(products)
                    line_items.append({"product_id": prod['product_id'], "quantity": 1})

                # Subtotal estimate for discount calculation
                est_subtotal = sum(Decimal(str(p['selling_price'])) * item['quantity'] for item in line_items for p in products if p['product_id'] == item['product_id'])

                # Optional discount (20% chance of small discount)
                discount = Decimal('0.00')
                if random.random() < 0.20 and est_subtotal > Decimal('200.00'):
                    discount = Decimal(str(random.choice([10, 20, 30, 50])))

                # Process transaction
                sale_id = process_and_save_sale(
                    shop_id=shop_id,
                    customer_id=customer_id,
                    order_type=order_type,
                    payment_method=payment_method,
                    line_items=line_items,
                    discount_amount=discount,
                    tax_percentage=5.0,
                    campaign_id=campaign_id,
                    sale_date=sale_datetime
                )

                created_count += 1
                sale_items_count += len(line_items)

            print("==================================================")
            print(f"  [SUCCESS] Generated {created_count} Sales Invoices with {sale_items_count} Line Items!")
            print("==================================================")

        finally:
            connection.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="BrewBean Synthetic Sales Data Generator")
    parser.add_argument('--count', type=int, default=600, help="Number of sales invoices to generate (default: 600)")
    parser.add_argument('--reset-demo-sales', action='store_true', help="Clear existing sales before generating")
    parser.add_argument('--confirm', action='store_true', help="Required safety confirmation flag for --reset-demo-sales")
    
    args = parser.parse_args()
    generate_demo_transactions(count=args.count, reset_existing=args.reset_demo_sales, confirmed=args.confirm)
