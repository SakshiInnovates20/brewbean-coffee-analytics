"""
BrewBean Coffee Analytics System — Marketing Campaign Data Access Model
Provides repository functions for Marketing Campaigns, performance tracking, and ROI calculations.
"""

from decimal import Decimal
from app.db import get_db_connection

def get_all_campaigns(search_query=None, channel_filter=None, status_filter=None):
    """
    Retrieves all marketing campaigns with calculated performance & ROI metrics.
    Sorted latest start_date first.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT mc.campaign_id, mc.campaign_name, mc.channel, mc.start_date, 
                       mc.end_date, mc.budget, mc.actual_spend, mc.target_audience, 
                       mc.status, mc.created_at,
                       COALESCE(SUM(s.total_amount), 0) AS attributed_revenue,
                       COALESCE(SUM(s.total_cost), 0) AS attributed_cost,
                       COALESCE(SUM(s.total_profit), 0) AS attributed_profit,
                       COUNT(s.sale_id) AS total_orders
                FROM marketing_campaigns mc
                LEFT JOIN sales s ON mc.campaign_id = s.campaign_id
                WHERE 1=1
            """
            params = []

            if search_query:
                sql += " AND (mc.campaign_name LIKE %s OR mc.target_audience LIKE %s)"
                term = f"%{search_query.strip()}%"
                params.extend([term, term])

            if channel_filter:
                sql += " AND mc.channel = %s"
                params.append(channel_filter.strip())

            if status_filter in ['Planned', 'Active', 'Completed', 'Cancelled']:
                sql += " AND mc.status = %s"
                params.append(status_filter)

            sql += " GROUP BY mc.campaign_id ORDER BY mc.start_date DESC, mc.campaign_id DESC"
            cursor.execute(sql, params)
            campaigns = cursor.fetchall()

            # Process ROI for each campaign
            for c in campaigns:
                spend = Decimal(str(c['actual_spend']))
                profit = Decimal(str(c['attributed_profit']))
                revenue = Decimal(str(c['attributed_revenue']))
                orders = int(c['total_orders'])

                c['avg_order_value'] = (revenue / Decimal(orders)) if orders > 0 else Decimal('0.00')

                if spend > Decimal('0.00'):
                    c['roi_percentage'] = round(((profit - spend) / spend) * Decimal('100.0'), 2)
                else:
                    c['roi_percentage'] = None

            return campaigns
    finally:
        connection.close()

def get_active_campaigns():
    """
    Retrieves active or currently running marketing campaigns for the POS dropdown selection.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT campaign_id, campaign_name, channel, start_date, end_date
                FROM marketing_campaigns
                WHERE status = 'Active' OR (status = 'Completed' AND start_date <= CURDATE() AND end_date >= DATE_SUB(CURDATE(), INTERVAL 60 DAY))
                ORDER BY campaign_name ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()

def get_campaign_by_id(campaign_id):
    """
    Retrieves a single campaign details by ID.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT campaign_id, campaign_name, channel, start_date, end_date, 
                       budget, actual_spend, target_audience, status, created_at
                FROM marketing_campaigns
                WHERE campaign_id = %s
            """
            cursor.execute(sql, (campaign_id,))
            return cursor.fetchone()
    finally:
        connection.close()

def get_campaign_performance_metrics(campaign_id):
    """
    Calculates detailed attributed financial & ROI performance for a campaign.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT 
                    COALESCE(SUM(s.total_amount), 0) AS attributed_revenue,
                    COALESCE(SUM(s.total_cost), 0) AS attributed_cost,
                    COALESCE(SUM(s.total_profit), 0) AS attributed_profit,
                    COUNT(s.sale_id) AS total_orders
                FROM sales s
                WHERE s.campaign_id = %s
            """
            cursor.execute(sql, (campaign_id,))
            res = cursor.fetchone()

            revenue = Decimal(str(res['attributed_revenue']))
            cost = Decimal(str(res['attributed_cost']))
            profit = Decimal(str(res['attributed_profit']))
            orders = int(res['total_orders'])
            aov = (revenue / Decimal(orders)) if orders > 0 else Decimal('0.00')

            cursor.execute("SELECT actual_spend FROM marketing_campaigns WHERE campaign_id = %s", (campaign_id,))
            camp = cursor.fetchone()
            spend = Decimal(str(camp['actual_spend'])) if camp else Decimal('0.00')

            roi_pct = round(((profit - spend) / spend) * Decimal('100.0'), 2) if spend > Decimal('0.00') else None

            return {
                "attributed_revenue": revenue,
                "attributed_cost": cost,
                "attributed_profit": profit,
                "total_orders": orders,
                "avg_order_value": aov,
                "roi_percentage": roi_pct
            }
    finally:
        connection.close()

def get_marketing_summary_kpis():
    """
    Calculates overall summary cards for the marketing dashboard page.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Total Spend across campaigns
            cursor.execute("SELECT COALESCE(SUM(actual_spend), 0) AS total_spend FROM marketing_campaigns")
            spend_res = cursor.fetchone()
            total_spend = Decimal(str(spend_res['total_spend']))

            # Attributed revenue & profit for sales linked to campaigns
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(s.total_amount), 0) AS attr_rev,
                    COALESCE(SUM(s.total_profit), 0) AS attr_profit
                FROM sales s
                WHERE s.campaign_id IS NOT NULL
            """)
            sales_res = cursor.fetchone()
            total_attr_rev = Decimal(str(sales_res['attr_rev']))
            total_attr_profit = Decimal(str(sales_res['attr_profit']))

            overall_roi = round(((total_attr_profit - total_spend) / total_spend) * Decimal('100.0'), 2) if total_spend > Decimal('0.00') else None

            return {
                "total_spend": total_spend,
                "total_attributed_revenue": total_attr_rev,
                "total_attributed_profit": total_attr_profit,
                "overall_roi": overall_roi
            }
    finally:
        connection.close()

def create_campaign(campaign_name, channel, start_date, end_date, budget=0.0, actual_spend=0.0, target_audience=None, status='Planned'):
    """
    Creates a new marketing campaign record.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO marketing_campaigns (campaign_name, channel, start_date, end_date, budget, actual_spend, target_audience, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                campaign_name.strip(),
                channel.strip() if channel else 'Other',
                start_date,
                end_date,
                Decimal(str(budget or 0)),
                Decimal(str(actual_spend or 0)),
                target_audience.strip() if target_audience else None,
                status if status in ['Planned', 'Active', 'Completed', 'Cancelled'] else 'Planned'
            ))
            connection.commit()
            return cursor.lastrowid
    finally:
        connection.close()

def update_campaign(campaign_id, campaign_name, channel, start_date, end_date, budget, actual_spend, target_audience, status):
    """
    Updates an existing marketing campaign.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE marketing_campaigns
                SET campaign_name = %s, channel = %s, start_date = %s, end_date = %s, 
                    budget = %s, actual_spend = %s, target_audience = %s, status = %s
                WHERE campaign_id = %s
            """
            cursor.execute(sql, (
                campaign_name.strip(),
                channel.strip() if channel else 'Other',
                start_date,
                end_date,
                Decimal(str(budget or 0)),
                Decimal(str(actual_spend or 0)),
                target_audience.strip() if target_audience else None,
                status if status in ['Planned', 'Active', 'Completed', 'Cancelled'] else 'Planned',
                campaign_id
            ))
            connection.commit()
            return cursor.rowcount > 0
    finally:
        connection.close()
