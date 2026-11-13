"""
BrewBean Coffee Analytics System — Shop Management Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.shop import (
    get_all_shops, get_shop_by_id, is_shop_code_taken,
    create_shop, update_shop, toggle_shop_status
)

shops_bp = Blueprint('shops', __name__)

@shops_bp.route('/shops', methods=['GET'])
def list_shops():
    """
    Renders the Shop Management dashboard page.
    """
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    try:
        shops = get_all_shops(search_query=search_query, status_filter=status_filter)
        return render_template('shops.html', shops=shops, search_query=search_query, status_filter=status_filter)
    except Exception as e:
        flash(f"Error loading shops: {str(e)}", "danger")
        return render_template('shops.html', shops=[], search_query=search_query, status_filter=status_filter)

@shops_bp.route('/shops/add', methods=['POST'])
def add_shop():
    """
    Handles addition of a new store branch.
    """
    shop_code = request.form.get('shop_code', '').strip().upper()
    shop_name = request.form.get('shop_name', '').strip()
    city = request.form.get('city', '').strip()
    area = request.form.get('area', '').strip()
    manager_name = request.form.get('manager_name', '').strip()
    opening_date = request.form.get('opening_date', '').strip()
    status = request.form.get('status', 'Active').strip()

    # Validations
    if not shop_code or not shop_name or not city:
        flash("Shop Code, Shop Name, and City are required fields.", "warning")
        return redirect(url_for('shops.list_shops'))

    if is_shop_code_taken(shop_code):
        flash(f"Shop Code '{shop_code}' already exists. Please use a unique Shop Code.", "danger")
        return redirect(url_for('shops.list_shops'))

    try:
        # Franchise ID defaults to 1 (BrewBean Coffee)
        create_shop(1, shop_code, shop_name, city, area, manager_name, opening_date, status)
        flash(f"Shop '{shop_name}' ({shop_code}) created successfully!", "success")
    except Exception as e:
        flash(f"Failed to create shop: {str(e)}", "danger")

    return redirect(url_for('shops.list_shops'))

@shops_bp.route('/shops/edit/<int:shop_id>', methods=['POST'])
def edit_shop(shop_id):
    """
    Handles updates to an existing store branch.
    """
    shop_name = request.form.get('shop_name', '').strip()
    city = request.form.get('city', '').strip()
    area = request.form.get('area', '').strip()
    manager_name = request.form.get('manager_name', '').strip()
    opening_date = request.form.get('opening_date', '').strip()
    status = request.form.get('status', 'Active').strip()

    if not shop_name or not city:
        flash("Shop Name and City cannot be empty.", "warning")
        return redirect(url_for('shops.list_shops'))

    try:
        updated = update_shop(shop_id, shop_name, city, area, manager_name, opening_date, status)
        if updated:
            flash(f"Shop details updated successfully!", "success")
        else:
            flash("Shop record not found.", "warning")
    except Exception as e:
        flash(f"Failed to update shop: {str(e)}", "danger")

    return redirect(url_for('shops.list_shops'))

@shops_bp.route('/shops/toggle-status/<int:shop_id>', methods=['POST'])
def toggle_status(shop_id):
    """
    Toggles shop status between Active and Inactive.
    """
    try:
        toggle_shop_status(shop_id)
        flash("Shop status updated successfully.", "info")
    except Exception as e:
        flash(f"Failed to update status: {str(e)}", "danger")

    return redirect(url_for('shops.list_shops'))
