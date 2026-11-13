"""
BrewBean Coffee Analytics System — Interactive Dashboard Routes
"""

from flask import Blueprint, render_template, request, flash
from app.models.shop import get_all_shops
from app.models.product import get_all_categories
from app.services.analytics_service import (
    get_dashboard_dataset_date_range, get_dashboard_kpis, get_sales_trend,
    get_branch_performance, get_top_products, get_category_performance,
    get_order_type_distribution, get_payment_distribution, get_customer_insights,
    get_top_customers, get_marketing_performance, get_monthly_performance,
    get_business_insights
)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
def render_dashboard():
    """
    Renders the interactive multi-branch sales & marketing analytics dashboard.
    Supports real-time filtering by start_date, end_date, shop_id, category_id, order_type.
    """
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    shop_id = request.args.get('shop_id', '').strip()
    category_id = request.args.get('category_id', '').strip()
    order_type = request.args.get('order_type', '').strip()

    filters = {
        "start_date": start_date if start_date else None,
        "end_date": end_date if end_date else None,
        "shop_id": shop_id if shop_id else None,
        "category_id": category_id if category_id else None,
        "order_type": order_type if order_type else None
    }

    try:
        date_range_info = get_dashboard_dataset_date_range()
        shops = get_all_shops()
        categories = get_all_categories()
        kpis = get_dashboard_kpis(filters)

        trend_data = get_sales_trend(filters)
        branch_perf = get_branch_performance(filters)
        top_products = get_top_products(filters, limit=10)
        category_perf = get_category_performance(filters)
        order_types = get_order_type_distribution(filters)
        payments = get_payment_distribution(filters)
        customer_segments = get_customer_insights(filters)
        top_customers = get_top_customers(filters, limit=5)
        marketing_perf = get_marketing_performance(filters)
        monthly_perf = get_monthly_performance(filters)
        insights = get_business_insights(filters)

        # Prepare Chart.js dataset JSON objects safely
        chart_trend_labels = [row['sale_day'] for row in trend_data]
        chart_trend_revenue = [float(row['daily_revenue']) for row in trend_data]
        chart_trend_profit = [float(row['daily_profit']) for row in trend_data]

        chart_branch_labels = [row['shop_name'] for row in branch_perf]
        chart_branch_revenue = [float(row['total_revenue']) for row in branch_perf]

        chart_prod_labels = [row['product_name'] for row in top_products]
        chart_prod_revenue = [float(row['total_revenue']) for row in top_products]

        chart_cat_labels = [row['category_name'] for row in category_perf]
        chart_cat_revenue = [float(row['total_revenue']) for row in category_perf]

        chart_order_type_labels = [row['order_type'] for row in order_types]
        chart_order_type_counts = [row['order_count'] for row in order_types]

        chart_payment_labels = [row['payment_method'] for row in payments]
        chart_payment_counts = [row['order_count'] for row in payments]

        chart_customer_labels = [row['customer_type'] for row in customer_segments]
        chart_customer_revenue = [float(row['total_revenue']) for row in customer_segments]

        # Top 5 marketing campaigns for chart visualization
        top_camps = sorted([c for c in marketing_perf if float(c['attributed_revenue']) > 0], key=lambda x: float(x['attributed_revenue']), reverse=True)[:5]
        chart_camp_labels = [c['campaign_name'] for c in top_camps]
        chart_camp_revenue = [float(c['attributed_revenue']) for c in top_camps]
        chart_camp_profit = [float(c['attributed_profit']) for c in top_camps]

        return render_template(
            'dashboard.html',
            kpis=kpis,
            shops=shops,
            categories=categories,
            date_range_info=date_range_info,
            filters=filters,
            branch_perf=branch_perf,
            top_products=top_products,
            top_customers=top_customers,
            marketing_perf=marketing_perf,
            monthly_perf=monthly_perf,
            insights=insights,
            # JS Charts Payload
            chart_trend_labels=chart_trend_labels,
            chart_trend_revenue=chart_trend_revenue,
            chart_trend_profit=chart_trend_profit,
            chart_branch_labels=chart_branch_labels,
            chart_branch_revenue=chart_branch_revenue,
            chart_prod_labels=chart_prod_labels,
            chart_prod_revenue=chart_prod_revenue,
            chart_cat_labels=chart_cat_labels,
            chart_cat_revenue=chart_cat_revenue,
            chart_order_type_labels=chart_order_type_labels,
            chart_order_type_counts=chart_order_type_counts,
            chart_payment_labels=chart_payment_labels,
            chart_payment_counts=chart_payment_counts,
            chart_customer_labels=chart_customer_labels,
            chart_customer_revenue=chart_customer_revenue,
            chart_camp_labels=chart_camp_labels,
            chart_camp_revenue=chart_camp_revenue,
            chart_camp_profit=chart_camp_profit
        )

    except Exception as e:
        flash(f"Error loading analytics dashboard: {str(e)}", "danger")
        default_kpis = {
            "total_revenue": Decimal('0.00'),
            "total_profit": Decimal('0.00'),
            "total_orders": 0,
            "avg_order_value": Decimal('0.00'),
            "profit_margin_pct": Decimal('0.00'),
            "total_customers": 0
        }
        return render_template('dashboard.html', kpis=default_kpis, shops=[], categories=[], filters={})
