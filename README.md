# ☕ BrewBean Coffee — Multi-Branch Sales & Marketing Analytics System

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?style=flat-square&logo=chartdotjs&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap&logoColor=white)
![Pytest](https://img.shields.io/badge/Tested%20with-Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)

An end-to-end **sales and marketing analytics system** for a 6-branch coffee chain. It records every sale through a POS-style interface, stores it in a relational **MySQL** database, and turns it into an **interactive dashboard** with KPIs, trends and automated business insights, so managers can see which branches, products, customers and campaigns actually drive profit.

---

## 📸 Dashboard Preview

![BrewBean analytics dashboard](screenshots/dashboard.png)

| POS Sales Entry | Marketing Campaign ROI |
|---|---|
| ![Sales entry](screenshots/sales_entry.png) | ![Marketing ROI](screenshots/marketing.png) |

---

## 💡 What This Project Demonstrates

- **Data modelling:** designed a normalised 8-table relational schema (shops, products, customers, sales, line items, campaigns)
- **SQL analytics:** KPIs, branch and product rankings, category mix, customer segmentation and monthly trends, all calculated with SQL aggregations and dynamic filters
- **Business metrics:** revenue, net profit, Average Order Value, profit margin % and marketing ROI %
- **Data visualisation:** interactive dashboard with line, bar and doughnut charts, filterable by date, branch, category and order type
- **Automated insights:** rule-based engine that writes plain-language findings from the data
- **Data generation & testing:** synthetic data generator for realistic sales volumes, plus a Pytest test suite

---

## 🎯 Project Objective

The goal of the **BrewBean Coffee Analytics System** is to provide store managers and business owners with actionable business intelligence. It answers key business questions such as:
- Which branch generates the highest revenue and profit?
- Which coffee and menu products are top sellers?
- What customer segments (New, Returning, Regular, VIP, Walk-in) contribute most to sales?
- Which marketing campaigns produce the highest Return on Investment (ROI)?
- What payment methods and order types (Dine-in, Takeaway, Delivery) are most popular?

---

## 🌟 Main Features

1. **Interactive Analytics Dashboard (`/dashboard`)**:
   - Filterable KPI summary cards (Total Revenue, Total Net Profit, Orders Count, Average Order Value, Profit Margin %, Unique Customers).
   - Multi-field filters by Date Range, Store Branch, Product Category, and Order Type.
   - Interactive Chart.js visualizations (Line trends, Bar charts, Doughnut breakdowns).
   - Automated rule-based business insights.
2. **Branch Management (`/shops`)**: Manage store locations, cities, branch codes (`BB001` to `BB006`), and managers.
3. **Product Catalog (`/products`)**: Manage menu items, categories, cost prices, selling prices, and item profit margins.
4. **Customer Directory (`/customers`)**: Register customer profiles with auto-generated customer codes (`CUS0001`, `CUS0002`...), customer types, and loyalty membership status.
5. **POS Sales Entry & Invoicing (`/sales/new`, `/sales`)**: Create Point-of-Sale orders with multiple product line items, automatic price lookups, live calculations, sequential invoice numbering (`BB-YYYYMMDD-XXXX`), and printable tax invoices (`/sales/<id>`).
6. **Marketing Campaign ROI Engine (`/marketing`)**: Track marketing campaign channels, budgets, actual spend, attributed sales revenue/profit, and campaign ROI %.

---

## 🧮 Core Financial & Analytics Formulas

All metrics are calculated directly from MySQL data using these formulas:

1. **Item Revenue** = $\text{Quantity} \times \text{Selling Price}$
2. **Item Cost** = $\text{Quantity} \times \text{Cost Price}$
3. **Item Profit** = $\text{Item Revenue} - \text{Item Cost}$
4. **Subtotal** = $\sum \text{Item Revenue}$
5. **Tax Amount (5%)** = $(\text{Subtotal} - \text{Discount}) \times \frac{5}{100}$
6. **Total Amount (Invoice Revenue)** = $(\text{Subtotal} - \text{Discount}) + \text{Tax Amount}$
7. **Total Cost** = $\sum \text{Item Cost}$
8. **Net Profit** = $\text{Total Amount} - \text{Total Cost}$
9. **Average Order Value (AOV)** = $\frac{\text{Total Revenue}}{\text{Total Number of Orders}}$
10. **Profit Margin %** = $\left( \frac{\text{Total Net Profit}}{\text{Total Revenue}} \right) \times 100$
11. **Marketing ROI %** = $\left( \frac{\text{Attributed Profit} - \text{Actual Marketing Spend}}{\text{Actual Marketing Spend}} \right) \times 100$

---

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.12, Flask 3.0+
- **Database**: MySQL 8.0, PyMySQL
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3
- **Data Visualizations**: Chart.js 4.4
- **Testing**: Pytest

---

## 📁 Project Structure

```text
BrewBean/
│
├── app/
│   ├── models/             # Database access functions (shop, product, customer, sale, campaign)
│   ├── routes/             # Flask route handlers (main, dashboard, shops, products, customers, sales, marketing)
│   ├── services/           # Business logic & analytics aggregations (sales_service, analytics_service)
│   ├── templates/          # HTML templates (Jinja2)
│   ├── static/             # Static CSS and JS files
│   ├── config.py           # Flask environment configuration
│   ├── db.py               # MySQL PyMySQL connection wrapper
│   └── __init__.py         # Flask app factory
│
├── database/
│   ├── schema.sql          # MySQL database schema (8 tables)
│   └── seed.sql            # Initial seed data script
│
├── scripts/
│   ├── init_db.py          # Database initialization runner
│   └── generate_demo_data.py # Synthetic sales generator script
│
├── tests/                  # Pytest automated test suite
├── .env.example            # Environment configuration template
├── .gitignore              # Git exclusion file
├── README.md               # Project documentation
├── requirements.txt        # Python package dependencies
└── run.py                  # Application entry point
```

---

## 🗄️ Database Tables (8 Relational Tables)

1. **`franchises`**: Franchise brand information.
2. **`shops`**: Retail store branches, locations, and branch managers.
3. **`product_categories`**: Menu item categories (Coffee, Cold Beverages, Tea, Food, Desserts, Snacks).
4. **`products`**: Menu products, cost prices, selling prices, and active status.
5. **`customers`**: Registered customer profiles, customer types, and loyalty flags.
6. **`marketing_campaigns`**: Advertising campaigns, channels, start/end dates, budgets, and spend.
7. **`sales`**: Sales invoice transaction headers (total amount, cost, profit, order type, payment method, shop_id, customer_id, campaign_id).
8. **`sale_items`**: Order line items breakdown (quantity, unit price, item revenue, item cost, item profit).

---

## 🚀 How to Setup and Run

### 1. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database Connection (`.env`)
Copy `.env.example` to `.env` and set your local MySQL connection settings:
```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-brewbean-coffee-2026

DB_HOST=127.0.0.1
DB_PORT=3307
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=brewbean_analytics
```

### 4. Initialize Database & Seed Data
```bash
python scripts/init_db.py
```

### 5. Generate Demo Sales Data (Optional)
```bash
python scripts/generate_demo_data.py --count 600
```

### 6. Run Application
```bash
python run.py
```
Open your browser at: `http://127.0.0.1:5000/`

---

## 🌐 Main Application Routes

- `/`: Home landing page
- `/dashboard`: Interactive Multi-Branch Analytics Dashboard
- `/shops`: Branch management directory
- `/products`: Product catalog & menu management
- `/customers`: Customer directory & loyalty tracking
- `/sales`: Sales log dashboard
- `/sales/new`: POS sales entry form
- `/sales/<id>`: Printable tax invoice receipt view
- `/marketing`: Marketing campaign directory & ROI tracking
- `/marketing/<id>`: Campaign performance detail view
- `/health`: System health API endpoint

---

## 🧪 How to Run Tests

Run the Pytest suite covering all core application modules:
```bash
pytest tests/
```
