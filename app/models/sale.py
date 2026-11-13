"""
BrewBean Coffee Analytics System — Sales & Invoices Data Access Model
Provides repository functions for Sales records, Line Items, and Operational KPIs.
"""

from datetime import datetime
from decimal import Decimal
from app.db import get_db_connection

def generate_next_invoice_number():
    """
    Generates a sequential invoice number in format BB-YYYYMMDD-XXXX.
    """
    today_str = datetime.now().strftime('%Y%m%d')
    prefix = f"BB-{today_str}-"
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT invoice_number FROM sales WHERE invoice_number LIKE %s ORDER BY sale_id DESC LIMIT 1"
            cursor.execute(sql, (f"{prefix}%",))
            last = cursor.fetchone()
            
            if last and last['invoice_number']:
                parts = last['invoice_number'].split('-')
                if len(parts) == 3 and parts[2].isdigit():
                    num = int(parts[2]) + 1
                    return f"{prefix}{num:04d}"
            
            # Fallback overall sequential count for today
            cursor.execute("SELECT COUNT(*) AS today_count FROM sales WHERE DATE(sale_date) = CURDATE()")
            count = cursor.fetchone()['today_count'] + 1
            return f"{prefix}{count:04d}"
    finally:
        connection.close()

def get_sales_summary_kpis():
    """
    Calculates operational summary metrics for the sales dashboard cards.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT 
                    COALESCE(SUM(total_amount), 0) AS total_revenue,
                    COALESCE(SUM(total_profit), 0) AS total_profit,
                    COUNT(*) AS total_invoices,
                    COALESCE(AVG(total_amount), 0) AS avg_order_value
                FROM sales
            """
            cursor.execute(sql)
            res = cursor.fetchone()
            return {
                "total_revenue": Decimal(str(res['total_revenue'])),
                "total_profit": Decimal(str(res['total_profit'])),
                "total_invoices": int(res['total_invoices']),
                "avg_order_value": Decimal(str(res['avg_order_value']))
            }
    finally:
        connection.close()

def get_all_sales(search=None, shop_id=None, start_date=None, end_date=None, order_type=None, payment_method=None):
    """
    Retrieves all sales invoices with multi-field search and filter criteria.
    Ordered latest sales first.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT s.sale_id, s.invoice_number, s.shop_id, s.customer_id, 
                       s.campaign_id, s.sale_date, s.order_type, s.payment_method, 
                       s.subtotal, s.discount, s.tax, s.total_amount, s.total_cost, 
                       s.total_profit, s.created_at,
                       sh.shop_name, sh.shop_code, sh.city,
                       COALESCE(c.name, 'Walk-in Customer') AS customer_name,
                       (SELECT COUNT(*) FROM sale_items si WHERE si.sale_id = s.sale_id) AS total_items_count
                FROM sales s
                JOIN shops sh ON s.shop_id = sh.shop_id
                LEFT JOIN customers c ON s.customer_id = c.customer_id
                WHERE 1=1
            """
            params = []

            if search:
                sql += " AND (s.invoice_number LIKE %s OR c.name LIKE %s OR sh.shop_name LIKE %s)"
                term = f"%{search.strip()}%"
                params.extend([term, term, term])

            if shop_id and str(shop_id).isdigit():
                sql += " AND s.shop_id = %s"
                params.append(int(shop_id))

            if start_date:
                sql += " AND DATE(s.sale_date) >= %s"
                params.append(start_date)

            if end_date:
                sql += " AND DATE(s.sale_date) <= %s"
                params.append(end_date)

            if order_type in ['Dine-in', 'Takeaway', 'Delivery']:
                sql += " AND s.order_type = %s"
                params.append(order_type)

            if payment_method in ['Cash', 'UPI', 'Credit Card', 'Debit Card', 'Wallet']:
                sql += " AND s.payment_method = %s"
                params.append(payment_method)

            sql += " ORDER BY s.sale_date DESC, s.sale_id DESC"
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()

def get_sale_by_id(sale_id):
    """
    Retrieves a single sales transaction header by sale_id.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT s.sale_id, s.invoice_number, s.shop_id, s.customer_id, 
                       s.campaign_id, s.sale_date, s.order_type, s.payment_method, 
                       s.subtotal, s.discount, s.tax, s.total_amount, s.total_cost, 
                       s.total_profit, s.created_at,
                       sh.shop_name, sh.shop_code, sh.city, sh.area, sh.manager_name,
                       COALESCE(c.name, 'Walk-in Customer') AS customer_name,
                       c.customer_code, c.city AS customer_city
                FROM sales s
                JOIN shops sh ON s.shop_id = sh.shop_id
                LEFT JOIN customers c ON s.customer_id = c.customer_id
                WHERE s.sale_id = %s
            """
            cursor.execute(sql, (sale_id,))
            return cursor.fetchone()
    finally:
        connection.close()

def get_sale_items_by_sale_id(sale_id):
    """
    Retrieves all order line items for a given sale.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT si.sale_item_id, si.sale_id, si.product_id, si.quantity, 
                       si.unit_price, si.item_discount, si.item_revenue, 
                       si.item_cost, si.item_profit,
                       p.product_name, p.cost_price, pc.category_name
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                JOIN product_categories pc ON p.category_id = pc.category_id
                WHERE si.sale_id = %s
                ORDER BY si.sale_item_id ASC
            """
            cursor.execute(sql, (sale_id,))
            return cursor.fetchall()
    finally:
        connection.close()
