"""
BrewBean Coffee Analytics System — Product & Category Data Access Model
Provides parameterized SQL repository functions for Product Management.
Calculates dynamic profit per unit (selling_price - cost_price) in Python memory.
"""

from decimal import Decimal
from app.db import get_db_connection

def get_all_categories():
    """
    Retrieves all product categories.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT category_id, category_name, description FROM product_categories ORDER BY category_name ASC"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()

def attach_profit_per_unit(product):
    """
    Calculates profit_per_unit dynamically (selling_price - cost_price).
    Does NOT store profit in database.
    """
    if not product:
        return None
    cost = Decimal(str(product.get('cost_price', 0)))
    selling = Decimal(str(product.get('selling_price', 0)))
    product['profit_per_unit'] = selling - cost
    return product

def get_all_products(search_query=None, category_id=None, status_filter=None):
    """
    Retrieves all products with optional category filtering and search query.
    Calculates profit_per_unit dynamically for each product record.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT p.product_id, p.category_id, p.product_name, p.description, 
                       p.cost_price, p.selling_price, p.status, p.created_at, 
                       c.category_name
                FROM products p
                JOIN product_categories c ON p.category_id = c.category_id
                WHERE 1=1
            """
            params = []

            if search_query:
                sql += " AND (p.product_name LIKE %s OR c.category_name LIKE %s OR p.description LIKE %s)"
                term = f"%{search_query.strip()}%"
                params.extend([term, term, term])

            if category_id and str(category_id).isdigit():
                sql += " AND p.category_id = %s"
                params.append(int(category_id))

            if status_filter in ['Active', 'Inactive']:
                sql += " AND p.status = %s"
                params.append(status_filter)

            sql += " ORDER BY c.category_name ASC, p.product_name ASC"
            cursor.execute(sql, params)
            products = cursor.fetchall()
            
            for prod in products:
                attach_profit_per_unit(prod)
            return products
    finally:
        connection.close()

def get_product_by_id(product_id):
    """
    Retrieves a single product record by product_id with dynamic profit calculation.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT p.product_id, p.category_id, p.product_name, p.description, 
                       p.cost_price, p.selling_price, p.status, p.created_at, 
                       c.category_name
                FROM products p
                JOIN product_categories c ON p.category_id = c.category_id
                WHERE p.product_id = %s
            """
            cursor.execute(sql, (product_id,))
            prod = cursor.fetchone()
            return attach_profit_per_unit(prod)
    finally:
        connection.close()

def create_product(category_id, product_name, description, cost_price, selling_price, status='Active'):
    """
    Inserts a new product record using parameterized SQL.
    Validates non-negative cost and selling prices.
    """
    cost = Decimal(str(cost_price))
    selling = Decimal(str(selling_price))

    if cost < 0 or selling < 0:
        raise ValueError("Cost price and selling price cannot be negative.")

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO products (category_id, product_name, description, cost_price, selling_price, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                category_id,
                product_name.strip(),
                description.strip() if description else None,
                cost,
                selling,
                status if status in ['Active', 'Inactive'] else 'Active'
            ))
            connection.commit()
            return cursor.lastrowid
    finally:
        connection.close()

def update_product(product_id, category_id, product_name, description, cost_price, selling_price, status):
    """
    Updates an existing product record.
    Validates non-negative cost and selling prices.
    """
    cost = Decimal(str(cost_price))
    selling = Decimal(str(selling_price))

    if cost < 0 or selling < 0:
        raise ValueError("Cost price and selling price cannot be negative.")

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE products
                SET category_id = %s, product_name = %s, description = %s, 
                    cost_price = %s, selling_price = %s, status = %s
                WHERE product_id = %s
            """
            cursor.execute(sql, (
                category_id,
                product_name.strip(),
                description.strip() if description else None,
                cost,
                selling,
                status if status in ['Active', 'Inactive'] else 'Active',
                product_id
            ))
            connection.commit()
            return cursor.rowcount > 0
    finally:
        connection.close()

def toggle_product_status(product_id):
    """
    Flips a product's status between 'Active' and 'Inactive'.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE products
                SET status = CASE WHEN status = 'Active' THEN 'Inactive' ELSE 'Active' END
                WHERE product_id = %s
            """
            cursor.execute(sql, (product_id,))
            connection.commit()
            return cursor.rowcount > 0
    finally:
        connection.close()
