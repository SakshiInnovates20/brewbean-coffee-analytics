import pytest
from decimal import Decimal
from app import create_app
from app.models.shop import get_all_shops, get_shop_by_id, is_shop_code_taken
from app.models.product import get_all_products, get_product_by_id, attach_profit_per_unit

@pytest.fixture
def client():
    """
    Flask test client fixture.
    """
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_database_seeded_records(client):
    """
    Verifies that initial seed data contains expected records.
    """
    with client.application.app_context():
        shops = get_all_shops()
        assert len(shops) >= 6
        
        products = get_all_products()
        assert len(products) >= 20

def test_shops_page_load(client):
    """
    Tests that GET /shops returns HTTP 200 and displays seeded shops.
    """
    response = client.get('/shops')
    assert response.status_code == 200
    assert b"Shop Management" in response.data
    assert b"BB001" in response.data
    assert b"BrewBean Alkapuri" in response.data

def test_shop_code_validation(client):
    """
    Verifies unique shop code validation.
    """
    with client.application.app_context():
        assert is_shop_code_taken('BB001') is True
        assert is_shop_code_taken('BB9999') is False

def test_products_page_load(client):
    """
    Tests that GET /products returns HTTP 200 and displays seeded products.
    """
    response = client.get('/products')
    assert response.status_code == 200
    assert b"Product Management" in response.data
    assert b"Espresso" in response.data
    assert b"Cappuccino" in response.data

def test_profit_per_unit_calculation():
    """
    Tests dynamic calculation of profit_per_unit (selling_price - cost_price).
    """
    dummy_product = {
        'product_name': 'Test Coffee',
        'cost_price': Decimal('50.00'),
        'selling_price': Decimal('140.00')
    }
    result = attach_profit_per_unit(dummy_product)
    assert result['profit_per_unit'] == Decimal('90.00')
