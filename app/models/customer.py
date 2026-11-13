"""
BrewBean Coffee Analytics System — Customer Data Access Model
Provides repository functions for managing Customer records.
"""

from app.db import get_db_connection

def get_all_customers(search_query=None, type_filter=None):
    """
    Retrieves all customer records with optional search and type filtering.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT customer_id, customer_code, name, age_group, gender, 
                       city, customer_type, loyalty_member, registration_date, created_at
                FROM customers
                WHERE 1=1
            """
            params = []

            if search_query:
                sql += " AND (name LIKE %s OR customer_code LIKE %s OR city LIKE %s)"
                term = f"%{search_query.strip()}%"
                params.extend([term, term, term])

            if type_filter in ['New', 'Returning', 'Regular', 'VIP']:
                sql += " AND customer_type = %s"
                params.append(type_filter)

            sql += " ORDER BY customer_id DESC"
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()

def get_customer_by_id(customer_id):
    """
    Retrieves a single customer record by customer_id.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT customer_id, customer_code, name, age_group, gender, 
                       city, customer_type, loyalty_member, registration_date, created_at
                FROM customers
                WHERE customer_id = %s
            """
            cursor.execute(sql, (customer_id,))
            return cursor.fetchone()
    finally:
        connection.close()

def generate_next_customer_code():
    """
    Generates the next sequential customer code (e.g. CUS0011).
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT customer_code FROM customers WHERE customer_code LIKE 'CUS%%' ORDER BY customer_id DESC LIMIT 1"
            cursor.execute(sql)
            last = cursor.fetchone()
            if last and last['customer_code'].startswith('CUS'):
                try:
                    num = int(last['customer_code'].replace('CUS', '')) + 1
                    return f"CUS{num:04d}"
                except ValueError:
                    pass
            
            cursor.execute("SELECT COUNT(*) AS total FROM customers")
            count = cursor.fetchone()['total'] + 1
            return f"CUS{count:04d}"
    finally:
        connection.close()

def is_customer_code_taken(customer_code, exclude_id=None):
    """
    Checks if a customer_code already exists.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT customer_id FROM customers WHERE LOWER(customer_code) = LOWER(%s)"
            params = [customer_code.strip()]
            if exclude_id:
                sql += " AND customer_id != %s"
                params.append(exclude_id)
            cursor.execute(sql, params)
            return cursor.fetchone() is not None
    finally:
        connection.close()

def create_customer(customer_code, name, age_group, gender, city, customer_type='New', loyalty_member=False, registration_date=None):
    """
    Inserts a new customer record using parameterized SQL.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO customers (customer_code, name, age_group, gender, city, customer_type, loyalty_member, registration_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                customer_code.strip().upper(),
                name.strip() if name else 'Walk-in Customer',
                age_group.strip() if age_group else None,
                gender.strip() if gender else None,
                city.strip() if city else None,
                customer_type if customer_type in ['New', 'Returning', 'Regular', 'VIP'] else 'New',
                bool(loyalty_member),
                registration_date if registration_date else None
            ))
            connection.commit()
            return cursor.lastrowid
    finally:
        connection.close()

def update_customer(customer_id, name, age_group, gender, city, customer_type, loyalty_member, registration_date):
    """
    Updates an existing customer profile.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE customers
                SET name = %s, age_group = %s, gender = %s, city = %s, 
                    customer_type = %s, loyalty_member = %s, registration_date = %s
                WHERE customer_id = %s
            """
            cursor.execute(sql, (
                name.strip(),
                age_group.strip() if age_group else None,
                gender.strip() if gender else None,
                city.strip() if city else None,
                customer_type if customer_type in ['New', 'Returning', 'Regular', 'VIP'] else 'New',
                bool(loyalty_member),
                registration_date if registration_date else None,
                customer_id
            ))
            connection.commit()
            return cursor.rowcount > 0
    finally:
        connection.close()
