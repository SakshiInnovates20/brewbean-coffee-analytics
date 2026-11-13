"""
BrewBean Coffee Analytics System — Customer Management Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.customer import (
    get_all_customers, get_customer_by_id, generate_next_customer_code,
    is_customer_code_taken, create_customer, update_customer
)

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers', methods=['GET'])
def list_customers():
    """
    Renders the Customer Management directory page.
    """
    search_query = request.args.get('search', '').strip()
    type_filter = request.args.get('type', '').strip()

    try:
        customers = get_all_customers(search_query=search_query, type_filter=type_filter)
        next_code = generate_next_customer_code()
        return render_template(
            'customers.html', 
            customers=customers, 
            next_code=next_code,
            search_query=search_query, 
            type_filter=type_filter
        )
    except Exception as e:
        flash(f"Error loading customers: {str(e)}", "danger")
        return render_template('customers.html', customers=[], next_code="CUS0001", search_query='', type_filter='')

@customers_bp.route('/customers/add', methods=['POST'])
def add_customer():
    """
    Handles addition of a new customer record.
    """
    customer_code = request.form.get('customer_code', '').strip().upper()
    name = request.form.get('name', '').strip()
    age_group = request.form.get('age_group', '').strip()
    gender = request.form.get('gender', '').strip()
    city = request.form.get('city', '').strip()
    customer_type = request.form.get('customer_type', 'New').strip()
    loyalty_member = request.form.get('loyalty_member') == '1'
    registration_date = request.form.get('registration_date', '').strip()

    if not name:
        flash("Customer name is required.", "warning")
        return redirect(url_for('customers.list_customers'))

    if not customer_code:
        customer_code = generate_next_customer_code()

    if is_customer_code_taken(customer_code):
        flash(f"Customer code '{customer_code}' already exists.", "danger")
        return redirect(url_for('customers.list_customers'))

    try:
        create_customer(customer_code, name, age_group, gender, city, customer_type, loyalty_member, registration_date)
        flash(f"Customer '{name}' ({customer_code}) created successfully!", "success")
    except Exception as e:
        flash(f"Failed to create customer: {str(e)}", "danger")

    return redirect(url_for('customers.list_customers'))

@customers_bp.route('/customers/edit/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    """
    Handles updates to an existing customer record.
    """
    name = request.form.get('name', '').strip()
    age_group = request.form.get('age_group', '').strip()
    gender = request.form.get('gender', '').strip()
    city = request.form.get('city', '').strip()
    customer_type = request.form.get('customer_type', 'New').strip()
    loyalty_member = request.form.get('loyalty_member') == '1'
    registration_date = request.form.get('registration_date', '').strip()

    if not name:
        flash("Customer name cannot be empty.", "warning")
        return redirect(url_for('customers.list_customers'))

    try:
        updated = update_customer(customer_id, name, age_group, gender, city, customer_type, loyalty_member, registration_date)
        if updated:
            flash(f"Customer profile updated successfully!", "success")
        else:
            flash("Customer record not found.", "warning")
    except Exception as e:
        flash(f"Failed to update customer: {str(e)}", "danger")

    return redirect(url_for('customers.list_customers'))
