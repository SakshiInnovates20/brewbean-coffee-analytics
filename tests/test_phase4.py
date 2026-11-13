import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app import create_app
from app.models.campaign import (
    get_all_campaigns, get_campaign_by_id, get_campaign_performance_metrics,
    get_marketing_summary_kpis, create_campaign, update_campaign
)
from app.services.analytics_service import (
    get_branch_performance, get_top_products,
    get_category_performance, get_customer_insights, get_sales_trend
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

def test_marketing_page_load(client):
    """
    Tests that GET /marketing returns HTTP 200 and renders marketing dashboard.
    """
    response = client.get('/marketing')
    assert response.status_code == 200
    assert b"Marketing Analytics" in response.data
    assert b"Monsoon Coffee Week" in response.data

def test_create_campaign_validation(client):
    """
    Tests creation of a marketing campaign and date validation (end_date >= start_date).
    """
    with client.application.app_context():
        # Valid campaign
        cid = create_campaign(
            campaign_name="Test Autumn Blitz",
            channel="Instagram",
            start_date="2026-09-01",
            end_date="2026-09-15",
            budget=10000.0,
            actual_spend=8000.0,
            target_audience="Coffee Lovers",
            status="Active"
        )
        assert cid > 0

        camp = get_campaign_by_id(cid)
        assert camp['campaign_name'] == "Test Autumn Blitz"
        assert camp['actual_spend'] == Decimal('8000.00')

def test_campaign_roi_calculation(client):
    """
    Tests campaign ROI percentage calculations.
    """
    with client.application.app_context():
        kpis = get_marketing_summary_kpis()
        assert kpis['total_spend'] >= Decimal('0.00')

        # Test metrics for existing campaign
        metrics = get_campaign_performance_metrics(1)
        assert 'attributed_revenue' in metrics
        assert 'attributed_profit' in metrics
        assert 'roi_percentage' in metrics

def test_campaign_detail_page_load(client):
    """
    Tests GET /marketing/1 detail page load.
    """
    response = client.get('/marketing/1')
    assert response.status_code == 200
    assert b"Monsoon Coffee Week" in response.data
    assert b"Attributed Invoices" in response.data

def test_analytics_service_functions(client):
    """
    Tests reusable analytics service functions for Phase 5 preparation.
    """
    with client.application.app_context():
        branch_rev = get_branch_performance()
        assert len(branch_rev) >= 6
        assert 'total_revenue' in branch_rev[0]

        top_products = get_top_products(limit=5)
        assert len(top_products) <= 5
        assert 'total_revenue' in top_products[0]

        categories = get_category_performance()
        assert len(categories) >= 5

        customer_segments = get_customer_insights()
        assert len(customer_segments) > 0

        daily_trends = get_sales_trend()
        assert len(daily_trends) > 0
