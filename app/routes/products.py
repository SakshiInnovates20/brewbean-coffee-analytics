"""
BrewBean Coffee Analytics System — Product Management Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.product import (
    get_all_products, get_product_by_id, get_all_categories,
    create_product, update_product, toggle_product_status
)

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def list_products():
    """
    Renders the Product Management dashboard page.
    """
    search_query = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', '').strip()
    status_filter = request.args.get('status', '').strip()

    try:
        categories = get_all_categories()
        products = get_all_products(
            search_query=search_query, 
            category_id=category_id, 
            status_filter=status_filter
        )
        return render_template(
            'products.html', 
            products=products, 
            categories=categories,
            search_query=search_query, 
            selected_category=category_id,
            status_filter=status_filter
        )
    except Exception as e:
        flash(f"Error loading products: {str(e)}", "danger")
        return render_template('products.html', products=[], categories=[], search_query='', selected_category='', status_filter='')

@products_bp.route('/products/add', methods=['POST'])
def add_product():
    """
    Handles addition of a new menu product.
    """
    category_id = request.form.get('category_id', '').strip()
    product_name = request.form.get('product_name', '').strip()
    description = request.form.get('description', '').strip()
    cost_price = request.form.get('cost_price', '0').strip()
    selling_price = request.form.get('selling_price', '0').strip()
    status = request.form.get('status', 'Active').strip()

    if not product_name or not category_id:
        flash("Product Name and Category are required.", "warning")
        return redirect(url_for('products.list_products'))

    try:
        cost = float(cost_price)
        selling = float(selling_price)
        if cost < 0 or selling < 0:
            flash("Cost price and selling price cannot be negative.", "warning")
            return redirect(url_for('products.list_products'))
    except ValueError:
        flash("Invalid price values entered. Please enter valid numeric prices.", "danger")
        return redirect(url_for('products.list_products'))

    try:
        create_product(int(category_id), product_name, description, cost, selling, status)
        flash(f"Product '{product_name}' created successfully!", "success")
    except Exception as e:
        flash(f"Failed to create product: {str(e)}", "danger")

    return redirect(url_for('products.list_products'))

@products_bp.route('/products/edit/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    """
    Handles updates to an existing menu product.
    """
    category_id = request.form.get('category_id', '').strip()
    product_name = request.form.get('product_name', '').strip()
    description = request.form.get('description', '').strip()
    cost_price = request.form.get('cost_price', '0').strip()
    selling_price = request.form.get('selling_price', '0').strip()
    status = request.form.get('status', 'Active').strip()

    if not product_name or not category_id:
        flash("Product Name and Category cannot be empty.", "warning")
        return redirect(url_for('products.list_products'))

    try:
        cost = float(cost_price)
        selling = float(selling_price)
        if cost < 0 or selling < 0:
            flash("Cost price and selling price cannot be negative.", "warning")
            return redirect(url_for('products.list_products'))
    except ValueError:
        flash("Invalid price values entered.", "danger")
        return redirect(url_for('products.list_products'))

    try:
        updated = update_product(product_id, int(category_id), product_name, description, cost, selling, status)
        if updated:
            flash(f"Product updated successfully!", "success")
        else:
            flash("Product record not found.", "warning")
    except Exception as e:
        flash(f"Failed to update product: {str(e)}", "danger")

    return redirect(url_for('products.list_products'))

@products_bp.route('/products/toggle-status/<int:product_id>', methods=['POST'])
def toggle_status(product_id):
    """
    Toggles product status between Active and Inactive.
    """
    try:
        toggle_product_status(product_id)
        flash("Product status updated successfully.", "info")
    except Exception as e:
        flash(f"Failed to update status: {str(e)}", "danger")

    return redirect(url_for('products.list_products'))
