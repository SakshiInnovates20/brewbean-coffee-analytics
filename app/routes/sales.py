"""
BrewBean Coffee Analytics System — Sales Management Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.sale import (
    get_all_sales, get_sale_by_id, get_sale_items_by_sale_id,
    get_sales_summary_kpis, generate_next_invoice_number
)
from app.models.shop import get_all_shops
from app.models.product import get_all_products
from app.models.customer import get_all_customers
from app.models.campaign import get_active_campaigns
from app.services.sales_service import process_and_save_sale

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/sales', methods=['GET'])
def list_sales():
    """
    Renders the Sales History & Operational Summary Dashboard.
    """
    search_query = request.args.get('search', '').strip()
    shop_id = request.args.get('shop_id', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    order_type = request.args.get('order_type', '').strip()
    payment_method = request.args.get('payment_method', '').strip()

    try:
        kpis = get_sales_summary_kpis()
        shops = get_all_shops(status_filter='Active')
        sales = get_all_sales(
            search=search_query,
            shop_id=shop_id,
            start_date=start_date,
            end_date=end_date,
            order_type=order_type,
            payment_method=payment_method
        )
        return render_template(
            'sales.html',
            sales=sales,
            kpis=kpis,
            shops=shops,
            search_query=search_query,
            selected_shop=shop_id,
            start_date=start_date,
            end_date=end_date,
            order_type=order_type,
            payment_method=payment_method
        )
    except Exception as e:
        flash(f"Error loading sales: {str(e)}", "danger")
        return render_template('sales.html', sales=[], kpis={}, shops=[], search_query='')

@sales_bp.route('/sales/new', methods=['GET', 'POST'])
def new_sale():
    """
    Renders POS Sales Entry form (GET) and processes sale submission (POST).
    """
    if request.method == 'POST':
        shop_id = request.form.get('shop_id')
        customer_id = request.form.get('customer_id')
        campaign_id = request.form.get('campaign_id')
        order_type = request.form.get('order_type')
        payment_method = request.form.get('payment_method')
        discount_amount = request.form.get('discount', '0')
        tax_percentage = request.form.get('tax_percentage', '5.0')
        sale_date = request.form.get('sale_date')

        # Collect line items dynamically from form fields (product_ids[] and quantities[])
        product_ids = request.form.getlist('product_ids[]')
        quantities = request.form.getlist('quantities[]')

        line_items = []
        for pid, qty in zip(product_ids, quantities):
            if pid and pid.isdigit() and qty and qty.isdigit():
                line_items.append({
                    "product_id": int(pid),
                    "quantity": int(qty)
                })

        try:
            sale_id = process_and_save_sale(
                shop_id=shop_id,
                customer_id=customer_id,
                order_type=order_type,
                payment_method=payment_method,
                line_items=line_items,
                discount_amount=discount_amount,
                tax_percentage=tax_percentage,
                campaign_id=campaign_id,
                sale_date=sale_date
            )
            flash("Sale transaction completed successfully!", "success")
            return redirect(url_for('sales.view_invoice', sale_id=sale_id))
        except ValueError as ve:
            flash(f"Validation Error: {str(ve)}", "warning")
        except Exception as e:
            flash(f"Transaction Error: {str(e)}", "danger")

        return redirect(url_for('sales.new_sale'))

    # GET Request: Load POS active shops, products, customers, and active marketing campaigns
    try:
        shops = get_all_shops(status_filter='Active')
        products = get_all_products(status_filter='Active')
        customers = get_all_customers()
        campaigns = get_active_campaigns()
        next_invoice = generate_next_invoice_number()

        return render_template(
            'sales_entry.html',
            shops=shops,
            products=products,
            customers=customers,
            campaigns=campaigns,
            next_invoice=next_invoice
        )
    except Exception as e:
        flash(f"Error initializing sales entry: {str(e)}", "danger")
        return redirect(url_for('sales.list_sales'))

@sales_bp.route('/sales/<int:sale_id>', methods=['GET'])
def view_invoice(sale_id):
    """
    Renders detailed invoice / receipt view for a single sale transaction.
    """
    try:
        sale = get_sale_by_id(sale_id)
        if not sale:
            flash("Invoice record not found.", "warning")
            return redirect(url_for('sales.list_sales'))

        sale_items = get_sale_items_by_sale_id(sale_id)
        return render_template('invoice_detail.html', sale=sale, sale_items=sale_items)
    except Exception as e:
        flash(f"Error loading invoice: {str(e)}", "danger")
        return redirect(url_for('sales.list_sales'))
