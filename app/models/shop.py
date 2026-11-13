"""
BrewBean Coffee Analytics System — Shop Data Access Model
Provides parameterized SQL repository functions for Shop Management.
"""

from app.db import get_db_connection

def get_all_shops(search_query=None, status_filter=None):
    """
    Retrieves all shops with optional search by shop name/code/city and status filtering.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT s.shop_id, s.franchise_id, s.shop_code, s.shop_name, 
                       s.city, s.area, s.manager_name, s.opening_date, 
                       s.status, s.created_at, f.franchise_name
                FROM shops s
                JOIN franchises f ON s.franchise_id = f.franchise_id
                WHERE 1=1
            """
            params = []

            if search_query:
                sql += " AND (s.shop_name LIKE %s OR s.shop_code LIKE %s OR s.city LIKE %s OR s.area LIKE %s)"
                term = f"%{search_query.strip()}%"
                params.extend([term, term, term, term])

            if status_filter in ['Active', 'Inactive']:
                sql += " AND s.status = %s"
                params.append(status_filter)

            sql += " ORDER BY s.shop_code ASC"
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()

def get_shop_by_id(shop_id):
    """
    Retrieves a single shop record by shop_id.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT s.shop_id, s.franchise_id, s.shop_code, s.shop_name, 
                       s.city, s.area, s.manager_name, s.opening_date, 
                       s.status, s.created_at, f.franchise_name
                FROM shops s
                JOIN franchises f ON s.franchise_id = f.franchise_id
                WHERE s.shop_id = %s
            """
            cursor.execute(sql, (shop_id,))
            return cursor.fetchone()
    finally:
        connection.close()

def is_shop_code_taken(shop_code, exclude_shop_id=None):
    """
    Checks if a shop_code already exists in the database.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT shop_id FROM shops WHERE LOWER(shop_code) = LOWER(%s)"
            params = [shop_code.strip()]
            if exclude_shop_id:
                sql += " AND shop_id != %s"
                params.append(exclude_shop_id)
            cursor.execute(sql, params)
            return cursor.fetchone() is not None
    finally:
        connection.close()

def create_shop(franchise_id, shop_code, shop_name, city, area, manager_name, opening_date, status='Active'):
    """
    Inserts a new shop record using parameterized SQL.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO shops (franchise_id, shop_code, shop_name, city, area, manager_name, opening_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                franchise_id,
                shop_code.strip().upper(),
                shop_name.strip(),
                city.strip(),
                area.strip() if area else None,
                manager_name.strip() if manager_name else None,
                opening_date if opening_date else None,
                status if status in ['Active', 'Inactive'] else 'Active'
            ))
            connection.commit()
            return cursor.lastrowid
    finally:
        connection.close()

def update_shop(shop_id, shop_name, city, area, manager_name, opening_date, status):
    """
    Updates an existing shop record.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE shops
                SET shop_name = %s, city = %s, area = %s, manager_name = %s, opening_date = %s, status = %s
                WHERE shop_id = %s
            """
            cursor.execute(sql, (
                shop_name.strip(),
                city.strip(),
                area.strip() if area else None,
                manager_name.strip() if manager_name else None,
                opening_date if opening_date else None,
                status if status in ['Active', 'Inactive'] else 'Active',
                shop_id
            ))
            connection.commit()
            return cursor.rowcount > 0
    finally:
        connection.close()

def toggle_shop_status(shop_id):
    """
    Flips a shop's status between 'Active' and 'Inactive'.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE shops
                SET status = CASE WHEN status = 'Active' THEN 'Inactive' ELSE 'Active' END
                WHERE shop_id = %s
            """
            cursor.execute(sql, (shop_id,))
            connection.commit()
            return cursor.rowcount > 0
    finally:
        connection.close()
