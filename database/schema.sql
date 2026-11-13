-- BrewBean Coffee Analytics System — Complete Database Schema (Phase 2)
-- Target Database: brewbean_analytics

CREATE DATABASE IF NOT EXISTS brewbean_analytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE brewbean_analytics;

-- Disable foreign key checks for clean table initialization if needed
SET FOREIGN_KEY_CHECKS = 0;

-- 1. TABLE: franchises
CREATE TABLE IF NOT EXISTS franchises (
    franchise_id INT AUTO_INCREMENT PRIMARY KEY,
    franchise_name VARCHAR(150) NOT NULL,
    owner_name VARCHAR(150),
    contact_email VARCHAR(150),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. TABLE: shops
CREATE TABLE IF NOT EXISTS shops (
    shop_id INT AUTO_INCREMENT PRIMARY KEY,
    franchise_id INT NOT NULL,
    shop_code VARCHAR(20) UNIQUE NOT NULL,
    shop_name VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL,
    area VARCHAR(100),
    manager_name VARCHAR(150),
    opening_date DATE,
    status ENUM('Active','Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_shops_franchise FOREIGN KEY (franchise_id)
        REFERENCES franchises(franchise_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 3. TABLE: product_categories
CREATE TABLE IF NOT EXISTS product_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255)
) ENGINE=InnoDB;

-- 4. TABLE: products
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    product_name VARCHAR(150) NOT NULL,
    description VARCHAR(255),
    cost_price DECIMAL(10,2) NOT NULL CHECK (cost_price >= 0),
    selling_price DECIMAL(10,2) NOT NULL CHECK (selling_price >= 0),
    status ENUM('Active','Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_category FOREIGN KEY (category_id)
        REFERENCES product_categories(category_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 5. TABLE: customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(150),
    age_group VARCHAR(20),
    gender VARCHAR(20),
    city VARCHAR(100),
    customer_type ENUM('New','Returning','Regular','VIP') DEFAULT 'New',
    loyalty_member BOOLEAN DEFAULT FALSE,
    registration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 6. TABLE: marketing_campaigns
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    campaign_id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_name VARCHAR(150) NOT NULL,
    channel VARCHAR(50),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    budget DECIMAL(12,2) DEFAULT 0,
    actual_spend DECIMAL(12,2) DEFAULT 0,
    target_audience VARCHAR(255),
    status ENUM('Planned','Active','Completed','Cancelled') DEFAULT 'Planned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 7. TABLE: sales
CREATE TABLE IF NOT EXISTS sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    shop_id INT NOT NULL,
    customer_id INT NULL,
    campaign_id INT NULL,
    sale_date DATETIME NOT NULL,
    order_type ENUM('Dine-in','Takeaway','Delivery') NOT NULL,
    payment_method ENUM('Cash','UPI','Credit Card','Debit Card','Wallet') NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    discount DECIMAL(12,2) NOT NULL DEFAULT 0,
    tax DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_cost DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_profit DECIMAL(12,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sales_shop FOREIGN KEY (shop_id)
        REFERENCES shops(shop_id) ON DELETE RESTRICT,
    CONSTRAINT fk_sales_customer FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id) ON DELETE SET NULL,
    CONSTRAINT fk_sales_campaign FOREIGN KEY (campaign_id)
        REFERENCES marketing_campaigns(campaign_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 8. TABLE: sale_items
CREATE TABLE IF NOT EXISTS sale_items (
    sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    item_discount DECIMAL(10,2) DEFAULT 0,
    item_revenue DECIMAL(12,2) NOT NULL,
    item_cost DECIMAL(12,2) NOT NULL,
    item_profit DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_sale_items_sale FOREIGN KEY (sale_id)
        REFERENCES sales(sale_id) ON DELETE CASCADE,
    CONSTRAINT fk_sale_items_product FOREIGN KEY (product_id)
        REFERENCES products(product_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;
