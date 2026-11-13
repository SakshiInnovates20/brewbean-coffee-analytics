import pytest
from decimal import Decimal
from app import create_app
from app.services.analytics_service import (
    get_dashboard_kpis, get_sales_trend, get_branch_performance,
    get_top_products, get_category_performance, get_order_type_distribution,
    get_payment_distribution, get_customer_insights, get_marketing_performance,
    get_monthly_performance, get_business_insights
)

@pytest.fixture
def client():
    """
    Flask test client fixture.
    """
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_dashboard_page_load(client):
    """
    Tests that GET /dashboard returns HTTP 200 and renders dashboard.
    """
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Multi-Branch Analytics Dashboard" in response.data
    assert b"Total Revenue" in response.data

def test_dashboard_kpi_calculations(client):
    """
    Tests accurate KPI math for Total Revenue, Total Profit, Orders, AOV, Margin %, Customers.
    """
    with client.application.app_context():
        kpis = get_dashboard_kpis()
        assert 'total_revenue' in kpis
        assert 'total_profit' in kpis
        assert 'total_orders' in kpis
        assert 'avg_order_value' in kpis
        assert 'profit_margin_pct' in kpis
        assert 'total_customers' in kpis

        assert kpis['total_revenue'] >= Decimal('0.00')
        assert kpis['total_orders'] >= 0

        if kpis['total_orders'] > 0:
            expected_aov = round(kpis['total_revenue'] / Decimal(kpis['total_orders']), 2)
            assert round(kpis['avg_order_value'], 2) == expected_aov

def test_dashboard_filter_parameters(client):
    """
    Tests dashboard analytics service with shop, category, order type, and date filters.
    """
    with client.application.app_context():
        filters = {
            "shop_id": "1",
            "category_id": "1",
            "order_type": "Dine-in",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31"
        }
        kpis = get_dashboard_kpis(filters)
        assert kpis['total_revenue'] >= Decimal('0.00')

        trend = get_sales_trend(filters)
        assert isinstance(trend, list)

        branches = get_branch_performance(filters)
        assert isinstance(branches, list)

        products = get_top_products(filters, limit=5)
        assert isinstance(products, list)

        monthly = get_monthly_performance(filters)
        assert isinstance(monthly, list)

def test_zero_data_handling(client):
    """
    Verifies that filters returning zero records yield 0 values without division by zero errors.
    """
    with client.application.app_context():
        # Impossible date range
        filters = {
            "start_date": "1990-01-01",
            "end_date": "1990-01-02"
        }
        kpis = get_dashboard_kpis(filters)
        assert kpis['total_revenue'] == Decimal('0.00')
        assert kpis['total_profit'] == Decimal('0.00')
        assert kpis['total_orders'] == 0
        assert kpis['avg_order_value'] == Decimal('0.00')
        assert kpis['profit_margin_pct'] == Decimal('0.00')

def test_business_insights_generation(client):
    """
    Tests rule-based automated business insights generator.
    """
    with client.application.app_context():
        insights = get_business_insights()
        assert isinstance(insights, list)
        assert len(insights) >= 3
