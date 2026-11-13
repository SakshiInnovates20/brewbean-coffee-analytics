"""
BrewBean Coffee Analytics System — Complete Interactive Analytics Service Layer
Provides SQL aggregation functions for store branches, products, customer segments, 
marketing ROI, date trends, and automated rule-based business insights.
"""

from decimal import Decimal
from app.db import get_db_connection

def build_filter_clause(filters, table_alias='s', include_category=False):
    """
    Constructs parameterized SQL WHERE clause conditions based on dashboard filters dict.
    Supports: start_date, end_date, shop_id, category_id, order_type.
    """
    where_sql = " WHERE 1=1"
    params = []

    if not filters or not isinstance(filters, dict):
        return where_sql, params

    start_date = filters.get('start_date')
    if start_date:
        where_sql += f" AND DATE({table_alias}.sale_date) >= %s"
        params.append(start_date)

    end_date = filters.get('end_date')
    if end_date:
        where_sql += f" AND DATE({table_alias}.sale_date) <= %s"
        params.append(end_date)

    shop_id = filters.get('shop_id')
    if shop_id and str(shop_id).isdigit():
        where_sql += f" AND {table_alias}.shop_id = %s"
        params.append(int(shop_id))

    order_type = filters.get('order_type')
    if order_type in ['Dine-in', 'Takeaway', 'Delivery']:
        where_sql += f" AND {table_alias}.order_type = %s"
        params.append(order_type)

    category_id = filters.get('category_id')
    if include_category and category_id and str(category_id).isdigit():
        where_sql += " AND p.category_id = %s"
        params.append(int(category_id))

    return where_sql, params

def get_dashboard_dataset_date_range():
    """
    Retrieves min and max sales transaction dates available in MySQL.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT MIN(DATE(sale_date)) AS min_date, MAX(DATE(sale_date)) AS max_date FROM sales"
            cursor.execute(sql)
            res = cursor.fetchone()
            return {
                "min_date": str(res['min_date']) if res and res['min_date'] else None,
                "max_date": str(res['max_date']) if res and res['max_date'] else None
            }
    finally:
        connection.close()

# ==================================================
# 1. MAIN DASHBOARD KPIS
# ==================================================

def get_dashboard_kpis(filters=None):
    """
    Calculates overall filtered KPI metrics: Total Revenue, Total Profit, Orders, AOV, Margin %, Customers.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            category_id = filters.get('category_id') if filters else None
            if category_id and str(category_id).isdigit():
                # Join with sale_items and products for category filtering while grouping by sale_id
                where_sql, params = build_filter_clause(filters, table_alias='s', include_category=True)
                sql = f"""
                    SELECT 
                        COALESCE(SUM(distinct_sales.total_amount), 0) AS total_revenue,
                        COALESCE(SUM(distinct_sales.total_profit), 0) AS total_profit,
                        COUNT(distinct_sales.sale_id) AS total_orders,
                        COUNT(DISTINCT distinct_sales.customer_id) AS total_customers
                    FROM (
                        SELECT s.sale_id, s.total_amount, s.total_profit, s.customer_id
                        FROM sales s
                        JOIN sale_items si ON s.sale_id = si.sale_id
                        JOIN products p ON si.product_id = p.product_id
                        {where_sql}
                        GROUP BY s.sale_id
                    ) AS distinct_sales
                """
            else:
                where_sql, params = build_filter_clause(filters, table_alias='s')
                sql = f"""
                    SELECT 
                        COALESCE(SUM(s.total_amount), 0) AS total_revenue,
                        COALESCE(SUM(s.total_profit), 0) AS total_profit,
                        COUNT(s.sale_id) AS total_orders,
                        COUNT(DISTINCT s.customer_id) AS total_customers
                    FROM sales s
                    {where_sql}
                """

            cursor.execute(sql, params)
            res = cursor.fetchone()

            revenue = Decimal(str(res['total_revenue']))
            profit = Decimal(str(res['total_profit']))
            orders = int(res['total_orders'])
            customers = int(res['total_customers'])

            aov = (revenue / Decimal(orders)) if orders > 0 else Decimal('0.00')
            margin_pct = round((profit / revenue) * Decimal('100.0'), 2) if revenue > Decimal('0.00') else Decimal('0.00')

            return {
                "total_revenue": revenue,
                "total_profit": profit,
                "total_orders": orders,
                "avg_order_value": aov,
                "profit_margin_pct": margin_pct,
                "total_customers": customers
            }
    finally:
        connection.close()

# ==================================================
# 2. TREND & BRANCH PERFORMANCE
# ==================================================

def get_sales_trend(filters=None):
    """
    Returns daily revenue & profit trend line data.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            category_id = filters.get('category_id') if filters else None
            if category_id and str(category_id).isdigit():
                where_sql, params = build_filter_clause(filters, table_alias='s', include_category=True)
                sql = f"""
                    SELECT DATE(distinct_sales.sale_date) AS sale_day,
                           SUM(distinct_sales.total_amount) AS daily_revenue,
                           SUM(distinct_sales.total_profit) AS daily_profit,
                           COUNT(distinct_sales.sale_id) AS total_invoices
                    FROM (
                        SELECT s.sale_id, s.sale_date, s.total_amount, s.total_profit
                        FROM sales s
                        JOIN sale_items si ON s.sale_id = si.sale_id
                        JOIN products p ON si.product_id = p.product_id
                        {where_sql}
                        GROUP BY s.sale_id
                    ) AS distinct_sales
                    GROUP BY sale_day
                    ORDER BY sale_day ASC
                """
            else:
                where_sql, params = build_filter_clause(filters, table_alias='s')
                sql = f"""
                    SELECT DATE(s.sale_date) AS sale_day,
                           SUM(s.total_amount) AS daily_revenue,
                           SUM(s.total_profit) AS daily_profit,
                           COUNT(s.sale_id) AS total_invoices
                    FROM sales s
                    {where_sql}
                    GROUP BY sale_day
                    ORDER BY sale_day ASC
                """

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            for r in rows:
                r['sale_day'] = str(r['sale_day'])
                r['daily_revenue'] = Decimal(str(r['daily_revenue']))
                r['daily_profit'] = Decimal(str(r['daily_profit']))
            return rows
    finally:
        connection.close()

def get_branch_performance(filters=None):
    """
    Returns performance metrics breakdown for all store branches sorted by revenue.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            category_id = filters.get('category_id') if filters else None
            if category_id and str(category_id).isdigit():
                where_sql, params = build_filter_clause(filters, table_alias='s', include_category=True)
                sql = f"""
                    SELECT sh.shop_id, sh.shop_code, sh.shop_name, sh.city,
                           COALESCE(SUM(distinct_sales.total_amount), 0) AS total_revenue,
                           COALESCE(SUM(distinct_sales.total_profit), 0) AS total_profit,
                           COUNT(distinct_sales.sale_id) AS total_invoices
                    FROM shops sh
                    LEFT JOIN (
                        SELECT s.sale_id, s.shop_id, s.total_amount, s.total_profit
                        FROM sales s
                        JOIN sale_items si ON s.sale_id = si.sale_id
                        JOIN products p ON si.product_id = p.product_id
                        {where_sql}
                        GROUP BY s.sale_id
                    ) AS distinct_sales ON sh.shop_id = distinct_sales.shop_id
                    GROUP BY sh.shop_id
                    ORDER BY total_revenue DESC
                """
            else:
                where_sql, params = build_filter_clause(filters, table_alias='s')
                sql = f"""
                    SELECT sh.shop_id, sh.shop_code, sh.shop_name, sh.city,
                           COALESCE(SUM(s.total_amount), 0) AS total_revenue,
                           COALESCE(SUM(s.total_profit), 0) AS total_profit,
                           COUNT(s.sale_id) AS total_invoices
                    FROM shops sh
                    LEFT JOIN sales s ON sh.shop_id = s.shop_id {where_sql.replace('WHERE 1=1', '')}
                    GROUP BY sh.shop_id
                    ORDER BY total_revenue DESC
                """

            cursor.execute(sql, params)
            branches = cursor.fetchall()

            for b in branches:
                rev = Decimal(str(b['total_revenue']))
                prof = Decimal(str(b['total_profit']))
                inv = int(b['total_invoices'])
                b['avg_order_value'] = (rev / Decimal(inv)) if inv > 0 else Decimal('0.00')
                b['profit_margin_pct'] = round((prof / rev) * Decimal('100.0'), 2) if rev > Decimal('0.00') else Decimal('0.00')

            return branches
    finally:
        connection.close()

# ==================================================
# 3. PRODUCT & CATEGORY ANALYTICS
# ==================================================

def get_top_products(filters=None, limit=10):
    """
    Returns top performing products based on actual sale_items data.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            where_sql, params = build_filter_clause(filters, table_alias='s', include_category=True)
            sql = f"""
                SELECT p.product_id, p.product_name, pc.category_name,
                       COALESCE(SUM(si.quantity), 0) AS total_qty_sold,
                       COALESCE(SUM(si.item_revenue), 0) AS total_revenue,
                       COALESCE(SUM(si.item_profit), 0) AS total_profit
                FROM products p
                JOIN product_categories pc ON p.category_id = pc.category_id
                JOIN sale_items si ON p.product_id = si.product_id
                JOIN sales s ON si.sale_id = s.sale_id
                {where_sql}
                GROUP BY p.product_id
                ORDER BY total_revenue DESC
                LIMIT %s
            """
            params.append(limit)
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()

def get_category_performance(filters=None):
    """
    Returns product category sales and revenue contributions.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            where_sql, params = build_filter_clause(filters, table_alias='s', include_category=True)
            sql = f"""
                SELECT pc.category_id, pc.category_name,
                       COALESCE(SUM(si.quantity), 0) AS total_quantity,
                       COALESCE(SUM(si.item_revenue), 0) AS total_revenue,
                       COALESCE(SUM(si.item_profit), 0) AS total_profit
                FROM product_categories pc
                JOIN products p ON pc.category_id = p.category_id
                JOIN sale_items si ON p.product_id = si.product_id
                JOIN sales s ON si.sale_id = s.sale_id
                {where_sql}
                GROUP BY pc.category_id
                ORDER BY total_revenue DESC
            """
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()

# ==================================================
# 4. ORDER TYPE & PAYMENT METHOD ANALYTICS
# ==================================================

def get_order_type_distribution(filters=None):
    """
    Returns invoice counts breakdown by Order Type (Dine-in, Takeaway, Delivery).
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            category_id = filters.get('category_id') if filters else None
            if category_id and str(category_id).isdigit():
                where_sql, params = build_filter_clause(filters, table_alias='s', include_category=True)
                sql = f"""
                    SELECT distinct_sales.order_type, COUNT(*) AS order_count
                    FROM (
                        SELECT s.sale_id, s.order_type
                        FROM sales s
                        JOIN sale_items si ON s.sale_id = si.sale_id
                        JOIN products p ON si.product_id = p.product_id
                        {where_sql}
                        GROUP BY s.sale_id
                    ) AS distinct_sales
                    GROUP BY distinct_sales.order_type
                """
            else:
                where_sql, params = build_filter_clause(filters, table_alias='s')
                sql = f"""
                    SELECT s.order_type, COUNT(s.sale_id) AS order_count
                    FROM sales s
                    {where_sql}
                    GROUP BY s.order_type
                """

            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()

def get_payment_distribution(filters=None):
    """
    Returns order count breakdown by Payment Method (UPI, Cash, Credit Card, etc.).
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            category_id = filters.get('category_id') if filters else None
            if category_id and str(category_id).isdigit():
                where_sql, params = build_filter_clause(filters, table_alias='s', include_category=True)
                sql = f"""
                    SELECT distinct_sales.payment_method, COUNT(*) AS order_count
                    FROM (
                        SELECT s.sale_id, s.payment_method
                        FROM sales s
                        JOIN sale_items si ON s.sale_id = si.sale_id
                        JOIN products p ON si.product_id = p.product_id
                        {where_sql}
                        GROUP BY s.sale_id
                    ) AS distinct_sales
                    GROUP BY distinct_sales.payment_method
                """
            else:
                where_sql, params = build_filter_clause(filters, table_alias='s')
                sql = f"""
                    SELECT s.payment_method, COUNT(s.sale_id) AS order_count
                    FROM sales s
                    {where_sql}
                    GROUP BY s.payment_method
                """

            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()

# ==================================================
# 5. CUSTOMER SEGMENTS & TOP CUSTOMERS
# ==================================================

def get_customer_insights(filters=None):
    """
    Returns revenue breakdown by customer_type (New, Returning, Regular, VIP, Walk-in).
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            category_id = filters.get('category_id') if filters else None
            if category_id and str(category_id).isdigit():
                where_sql, params = build_filter_clause(filters, table_alias='s', include_category=True)
                sql = f"""
                    SELECT COALESCE(c.customer_type, 'Walk-in') AS customer_type,
                           COUNT(distinct_sales.sale_id) AS total_invoices,
                           COALESCE(SUM(distinct_sales.total_amount), 0) AS total_revenue
                    FROM (
                        SELECT s.sale_id, s.customer_id, s.total_amount
                        FROM sales s
                        JOIN sale_items si ON s.sale_id = si.sale_id
                        JOIN products p ON si.product_id = p.product_id
                        {where_sql}
                        GROUP BY s.sale_id
                    ) AS distinct_sales
                    LEFT JOIN customers c ON distinct_sales.customer_id = c.customer_id
                    GROUP BY customer_type
                    ORDER BY total_revenue DESC
                """
            else:
                where_sql, params = build_filter_clause(filters, table_alias='s')
                sql = f"""
                    SELECT COALESCE(c.customer_type, 'Walk-in') AS customer_type,
                           COUNT(s.sale_id) AS total_invoices,
                           COALESCE(SUM(s.total_amount), 0) AS total_revenue
                    FROM sales s
                    LEFT JOIN customers c ON s.customer_id = c.customer_id
                    {where_sql}
                    GROUP BY customer_type
                    ORDER BY total_revenue DESC
                """

            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()

def get_top_customers(filters=None, limit=5):
    """
    Returns top registered customers by revenue (excluding Walk-in).
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            category_id = filters.get('category_id') if filters else None
            if category_id and str(category_id).isdigit():
                where_sql, params = build_filter_clause(filters, table_alias='s', include_category=True)
                sql = f"""
                    SELECT c.customer_id, c.customer_code, c.name, c.customer_type,
                           COUNT(distinct_sales.sale_id) AS total_orders,
                           COALESCE(SUM(distinct_sales.total_amount), 0) AS total_revenue
                    FROM (
                        SELECT s.sale_id, s.customer_id, s.total_amount
                        FROM sales s
                        JOIN sale_items si ON s.sale_id = si.sale_id
                        JOIN products p ON si.product_id = p.product_id
                        {where_sql}
                        GROUP BY s.sale_id
                    ) AS distinct_sales
                    JOIN customers c ON distinct_sales.customer_id = c.customer_id
                    GROUP BY c.customer_id
                    ORDER BY total_revenue DESC
                    LIMIT %s
                """
            else:
                where_sql, params = build_filter_clause(filters, table_alias='s')
                sql = f"""
                    SELECT c.customer_id, c.customer_code, c.name, c.customer_type,
                           COUNT(s.sale_id) AS total_orders,
                           COALESCE(SUM(s.total_amount), 0) AS total_revenue
                    FROM sales s
                    JOIN customers c ON s.customer_id = c.customer_id
                    {where_sql}
                    GROUP BY c.customer_id
                    ORDER BY total_revenue DESC
                    LIMIT %s
                """

            params.append(limit)
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()

# ==================================================
# 6. MARKETING PERFORMANCE
# ==================================================

def get_marketing_performance(filters=None):
    """
    Returns campaign attributed performance and ROI breakdown.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            where_sql, params = build_filter_clause(filters, table_alias='s')
            sql = f"""
                SELECT mc.campaign_id, mc.campaign_name, mc.channel, mc.actual_spend, mc.status,
                       COALESCE(SUM(s.total_amount), 0) AS attributed_revenue,
                       COALESCE(SUM(s.total_profit), 0) AS attributed_profit,
                       COUNT(s.sale_id) AS attributed_orders
                FROM marketing_campaigns mc
                LEFT JOIN sales s ON mc.campaign_id = s.campaign_id {where_sql.replace('WHERE 1=1', '')}
                GROUP BY mc.campaign_id
                ORDER BY attributed_revenue DESC
            """
            cursor.execute(sql, params)
            campaigns = cursor.fetchall()

            for c in campaigns:
                spend = Decimal(str(c['actual_spend']))
                profit = Decimal(str(c['attributed_profit']))
                if spend > Decimal('0.00'):
                    c['roi_percentage'] = round(((profit - spend) / spend) * Decimal('100.0'), 2)
                else:
                    c['roi_percentage'] = None

            return campaigns
    finally:
        connection.close()

# ==================================================
# 7. MONTHLY BUSINESS PERFORMANCE
# ==================================================

def get_monthly_performance(filters=None):
    """
    Returns chronological monthly sales performance breakdown.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            category_id = filters.get('category_id') if filters else None
            if category_id and str(category_id).isdigit():
                where_sql, params = build_filter_clause(filters, table_alias='s', include_category=True)
                sql = f"""
                    SELECT DATE_FORMAT(distinct_sales.sale_date, '%%Y-%%m') AS month_key,
                           DATE_FORMAT(distinct_sales.sale_date, '%%b %%Y') AS month_name,
                           COUNT(distinct_sales.sale_id) AS total_orders,
                           SUM(distinct_sales.total_amount) AS total_revenue,
                           SUM(distinct_sales.total_profit) AS total_profit
                    FROM (
                        SELECT s.sale_id, s.sale_date, s.total_amount, s.total_profit
                        FROM sales s
                        JOIN sale_items si ON s.sale_id = si.sale_id
                        JOIN products p ON si.product_id = p.product_id
                        {where_sql}
                        GROUP BY s.sale_id
                    ) AS distinct_sales
                    GROUP BY month_key, month_name
                    ORDER BY month_key ASC
                """
            else:
                where_sql, params = build_filter_clause(filters, table_alias='s')
                sql = f"""
                    SELECT DATE_FORMAT(s.sale_date, '%%Y-%%m') AS month_key,
                           DATE_FORMAT(s.sale_date, '%%b %%Y') AS month_name,
                           COUNT(s.sale_id) AS total_orders,
                           SUM(s.total_amount) AS total_revenue,
                           SUM(s.total_profit) AS total_profit
                    FROM sales s
                    {where_sql}
                    GROUP BY month_key, month_name
                    ORDER BY month_key ASC
                """

            cursor.execute(sql, params)
            months = cursor.fetchall()

            for m in months:
                rev = Decimal(str(m['total_revenue']))
                prof = Decimal(str(m['total_profit']))
                orders = int(m['total_orders'])
                m['avg_order_value'] = (rev / Decimal(orders)) if orders > 0 else Decimal('0.00')
                m['profit_margin_pct'] = round((prof / rev) * Decimal('100.0'), 2) if rev > Decimal('0.00') else Decimal('0.00')

            return months
    finally:
        connection.close()

# ==================================================
# 8. RULE-BASED AUTOMATED BUSINESS INSIGHTS
# ==================================================

def get_business_insights(filters=None):
    """
    Generates 4-6 deterministic rule-based business insights strictly from MySQL dataset query results.
    """
    insights = []
    
    # Insight 1: Top Branch
    branches = get_branch_performance(filters)
    if branches and len(branches) > 0 and Decimal(str(branches[0]['total_revenue'])) > Decimal('0'):
        top_b = branches[0]
        insights.append(f"👑 <strong>Top Branch:</strong> <strong>{top_b['shop_name']} ({top_b['city']})</strong> is the highest revenue-generating store branch, achieving <strong>₹{top_b['total_revenue']:,.2f}</strong> in sales.")

    # Insight 2: Top Product
    products = get_top_products(filters, limit=1)
    if products and len(products) > 0 and Decimal(str(products[0]['total_revenue'])) > Decimal('0'):
        top_p = products[0]
        insights.append(f"☕ <strong>Best Selling Product:</strong> <strong>{top_p['product_name']}</strong> leads menu sales, generating <strong>₹{top_p['total_revenue']:,.2f}</strong> from <strong>{top_p['total_qty_sold']}</strong> units ordered.")

    # Insight 3: Popular Payment Method
    payments = get_payment_distribution(filters)
    if payments and len(payments) > 0:
        top_pay = sorted(payments, key=lambda x: x['order_count'], reverse=True)[0]
        insights.append(f"💳 <strong>Preferred Payment Channel:</strong> <strong>{top_pay['payment_method']}</strong> is the most popular payment method with <strong>{top_pay['order_count']}</strong> completed transactions.")

    # Insight 4: Best Marketing Campaign
    campaigns = get_marketing_performance(filters)
    valid_rois = [c for c in campaigns if c['roi_percentage'] is not None]
    if valid_rois:
        best_camp = sorted(valid_rois, key=lambda x: x['roi_percentage'], reverse=True)[0]
        insights.append(f"🎯 <strong>Top Marketing Campaign:</strong> <strong>{best_camp['campaign_name']}</strong> ({best_camp['channel']}) delivered the highest return on investment with a <strong>+{best_camp['roi_percentage']}% ROI</strong>.")

    # Insight 5: Category Dominance
    categories = get_category_performance(filters)
    if categories and len(categories) > 0:
        top_cat = categories[0]
        insights.append(f"📊 <strong>Category Leader:</strong> The <strong>{top_cat['category_name']}</strong> category generates the highest total sales revenue at <strong>₹{top_cat['total_revenue']:,.2f}</strong>.")

    # Insight 6: Customer Segment Contribution
    customers = get_customer_insights(filters)
    vip_seg = [c for c in customers if c['customer_type'] == 'VIP']
    if vip_seg:
        insights.append(f"⭐ <strong>VIP Loyalty Impact:</strong> Registered <strong>VIP Members</strong> contributed <strong>₹{vip_seg[0]['total_revenue']:,.2f}</strong> across <strong>{vip_seg[0]['total_invoices']}</strong> orders.")

    return insights
