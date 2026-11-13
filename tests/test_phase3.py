import pytest
from decimal import Decimal
from app import create_app
from app.models.customer import get_all_customers, generate_next_customer_code
from app.models.sale import get_all_sales, get_sales_summary_kpis, generate_next_invoice_number, get_sale_by_id
from app.services.sales_service import process_and_save_sale

@pytest.fixture
def client():
    """
    Flask test client fixture.
    """
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_customers_page_load(client):
    """
    Tests that GET /customers returns HTTP 200 and displays seeded customers.
    """
    response = client.get('/customers')
    assert response.status_code == 200
    assert b"Customer Management" in response.data
    assert b"Aarav Shah" in response.data

def test_customer_code_generator(client):
    """
    Tests sequential customer code generation.
    """
    with client.application.app_context():
        code = generate_next_customer_code()
        assert code.startswith("CUS")
        assert len(code) == 7

def test_sales_page_load(client):
    """
    Tests that GET /sales returns HTTP 200 and displays sales KPIs and history.
    """
    response = client.get('/sales')
    assert response.status_code == 200
    assert b"Sales Management" in response.data
    assert b"BB-20260825-0001" in response.data

def test_sales_new_page_load(client):
    """
    Tests that GET /sales/new renders POS sales entry form.
    """
    response = client.get('/sales/new')
    assert response.status_code == 200
    assert b"Create New Sales Invoice" in response.data
    assert b"Order &amp; Customer Details" in response.data or b"Order & Customer Details" in response.data

def test_sales_transaction_service(client):
    """
    Tests server-side sale calculation and atomic database save logic.
    Product 1 (Espresso): selling 120.00, cost 45.00
    Product 3 (Cappuccino): selling 180.00, cost 65.00
    Qty: 1 Espresso + 1 Cappuccino = subtotal 300.00, cost 110.00
    Discount: 20.00 -> Taxable: 280.00 -> Tax (5%): 14.00
    Grand Total: 294.00, Total Profit: 294.00 - 110.00 = 184.00
    """
    with client.application.app_context():
        line_items = [
            {"product_id": 1, "quantity": 1},
            {"product_id": 3, "quantity": 1}
        ]
        sale_id = process_and_save_sale(
            shop_id=1,
            customer_id=None, # Walk-in Customer
            order_type='Dine-in',
            payment_method='UPI',
            line_items=line_items,
            discount_amount=20.0,
            tax_percentage=5.0
        )
        assert sale_id > 0

        # Verify saved sale in DB
        sale = get_sale_by_id(sale_id)
        assert sale is not None
        assert sale['subtotal'] == Decimal('300.00')
        assert sale['discount'] == Decimal('20.00')
        assert sale['tax'] == Decimal('14.00')
        assert sale['total_amount'] == Decimal('294.00')
        assert sale['total_cost'] == Decimal('110.00')
        assert sale['total_profit'] == Decimal('184.00')
        assert sale['customer_name'] == 'Walk-in Customer'

def test_invalid_sale_validation(client):
    """
    Verifies that invalid sale inputs (negative discount or missing products) raise ValueError.
    """
    with client.application.app_context():
        # Missing line items
        with pytest.raises(ValueError):
            process_and_save_sale(1, None, 'Dine-in', 'UPI', [])

        # Negative discount
        with pytest.raises(ValueError):
            process_and_save_sale(1, None, 'Dine-in', 'UPI', [{"product_id": 1, "quantity": 1}], discount_amount=-10.0)
