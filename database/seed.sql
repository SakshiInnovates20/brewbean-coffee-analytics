-- BrewBean Coffee Analytics System — Seed Data Script (Phase 2, Phase 3 & Phase 4)

USE brewbean_analytics;

-- 1. SEED FRANCHISE
INSERT IGNORE INTO franchises (franchise_id, franchise_name, owner_name, contact_email, phone)
VALUES (1, 'BrewBean Coffee', 'BrewBean Corporate', 'corporate@brewbeancoffee.com', '+91-9876543210');

-- 2. SEED SHOPS
INSERT IGNORE INTO shops (shop_id, franchise_id, shop_code, shop_name, city, area, manager_name, opening_date, status)
VALUES
(1, 1, 'BB001', 'BrewBean Alkapuri', 'Vadodara', 'Alkapuri', 'Sakshi Parmar', '2022-01-15', 'Active'),
(2, 1, 'BB002', 'BrewBean Manjalpur', 'Vadodara', 'Manjalpur', 'Kirteeraj Revar', '2022-06-20', 'Active'),
(3, 1, 'BB003', 'BrewBean Satellite', 'Ahmedabad', 'Satellite', 'Manvi Mehta', '2023-02-10', 'Active'),
(4, 1, 'BB004', 'BrewBean Vesu', 'Surat', 'Vesu', 'Tushar Jariwala', '2023-08-05', 'Active'),
(5, 1, 'BB005', 'BrewBean Navrangpura', 'Ahmedabad', 'Navrangpura', 'Vaibhav Patel', '2023-11-12', 'Active'),
(6, 1, 'BB006', 'BrewBean Andheri', 'Mumbai', 'Andheri', 'Milan Patel', '2024-01-08', 'Active');

-- 3. SEED PRODUCT CATEGORIES
INSERT IGNORE INTO product_categories (category_id, category_name, description)
VALUES
(1, 'Coffee', 'Hot freshly brewed espresso based coffee beverages'),
(2, 'Cold Beverages', 'Iced coffees, cold brews, and refreshing chillers'),
(3, 'Tea', 'Artisanal hot and iced teas'),
(4, 'Food', 'Freshly toasted sandwiches, burgers, and hot savory meals'),
(5, 'Desserts', 'Delicious pastries, cakes, brownies, and sweet treats'),
(6, 'Snacks', 'Quick bite snacks and sides');

-- 4. SEED PRODUCTS
INSERT IGNORE INTO products (product_id, category_id, product_name, description, cost_price, selling_price, status)
VALUES
(1, 1, 'Espresso', 'Rich single shot espresso blend', 45.00, 120.00, 'Active'),
(2, 1, 'Americano', 'Espresso diluted with hot water', 50.00, 140.00, 'Active'),
(3, 1, 'Cappuccino', 'Equal parts espresso, steamed milk, and foam', 65.00, 180.00, 'Active'),
(4, 1, 'Latte', 'Creamy espresso topped with smooth steamed milk', 70.00, 190.00, 'Active'),
(5, 1, 'Mocha', 'Espresso blended with rich chocolate and steamed milk', 80.00, 210.00, 'Active'),
(6, 1, 'Flat White', 'Double shot espresso with velvety micro-foam', 75.00, 195.00, 'Active'),

(7, 2, 'Cold Coffee', 'Classic blended iced coffee with milk and ice cream', 70.00, 190.00, 'Active'),
(8, 2, 'Cold Brew', 'Steeped 16-hour cold coffee extract served chilled', 85.00, 220.00, 'Active'),
(9, 2, 'Iced Latte', 'Chilled espresso poured over ice and cold milk', 75.00, 200.00, 'Active'),

(10, 3, 'Masala Tea', 'Traditional Indian spiced milk tea', 30.00, 90.00, 'Active'),
(11, 3, 'Green Tea', 'Antioxidant-rich organic green tea', 35.00, 100.00, 'Active'),

(12, 4, 'Veg Sandwich', 'Grilled double decker vegetable sandwich', 60.00, 160.00, 'Active'),
(13, 4, 'Paneer Sandwich', 'Spiced paneer cottage cheese toasted sandwich', 75.00, 190.00, 'Active'),
(14, 4, 'Veg Burger', 'Crispy potato & vegetable patty burger with fries', 70.00, 180.00, 'Active'),

(15, 6, 'Garlic Bread', 'Toasted oven garlic bread slices with cheese', 50.00, 140.00, 'Active'),
(16, 6, 'French Fries', 'Crispy salted golden potato fries', 45.00, 130.00, 'Active'),

(17, 5, 'Brownie', 'Rich fudgy dark chocolate walnut brownie', 55.00, 150.00, 'Active'),
(18, 5, 'Muffin', 'Freshly baked blueberry vanilla muffin', 40.00, 120.00, 'Active'),
(19, 5, 'Cheesecake', 'Classic New York baked slice cheesecake', 95.00, 250.00, 'Active'),
(20, 5, 'Cookie', 'Chunky double chocolate chip cookie', 30.00, 80.00, 'Active');

-- 5. SEED CUSTOMERS
INSERT IGNORE INTO customers (customer_id, customer_code, name, age_group, gender, city, customer_type, loyalty_member, registration_date)
VALUES
(1, 'CUS0001', 'Aarav Shah', '25-34', 'Male', 'Vadodara', 'Regular', TRUE, '2023-01-10'),
(2, 'CUS0002', 'Riya Patel', '18-24', 'Female', 'Vadodara', 'VIP', TRUE, '2023-03-15'),
(3, 'CUS0003', 'Karan Mehta', '35-44', 'Male', 'Ahmedabad', 'Returning', FALSE, '2023-05-20'),
(4, 'CUS0004', 'Ananya Joshi', '25-34', 'Female', 'Surat', 'Regular', TRUE, '2023-07-12'),
(5, 'CUS0005', 'Rohan Desai', '45-54', 'Male', 'Mumbai', 'VIP', TRUE, '2023-08-01'),
(6, 'CUS0006', 'Pooja Solanki', '18-24', 'Female', 'Ahmedabad', 'New', FALSE, '2023-09-18'),
(7, 'CUS0007', 'Devang Trivedi', '25-34', 'Male', 'Vadodara', 'Returning', TRUE, '2023-10-05'),
(8, 'CUS0008', 'Isha Bhatt', '25-34', 'Female', 'Surat', 'Regular', TRUE, '2023-11-22'),
(9, 'CUS0009', 'Hardik Parmar', '35-44', 'Male', 'Mumbai', 'New', FALSE, '2023-12-04'),
(10, 'CUS0010', 'Kavya Saxena', '18-24', 'Female', 'Ahmedabad', 'VIP', TRUE, '2024-01-15');

-- 6. SEED MARKETING CAMPAIGNS
INSERT IGNORE INTO marketing_campaigns (campaign_id, campaign_name, channel, start_date, end_date, budget, actual_spend, target_audience, status)
VALUES
(1, 'Monsoon Coffee Week', 'Instagram', '2026-06-01', '2026-06-15', 15000.00, 12000.00, 'Young professionals & students', 'Completed'),
(2, 'Festive Latte Campaign', 'Google Ads', '2026-07-01', '2026-07-31', 25000.00, 22000.00, 'Coffee lovers & office commuters', 'Completed'),
(3, 'Weekend Combo Push', 'Facebook', '2026-08-01', '2026-08-31', 18000.00, 15000.00, 'Families & Weekend Diners', 'Active'),
(4, 'Student Discount Campaign', 'WhatsApp', '2026-08-10', '2026-09-10', 8000.00, 6000.00, 'University & College Students', 'Active'),
(5, 'Instagram Cold Brew Push', 'Instagram', '2026-08-15', '2026-09-15', 12000.00, 9500.00, 'Youth & Cold Coffee lovers', 'Active'),
(6, 'Loyalty VIP Member Offer', 'Email', '2026-08-01', '2026-08-20', 5000.00, 4500.00, 'Registered VIP Loyalty Members', 'Completed'),
(7, 'Diwali Coffee Fest', 'Offline', '2026-10-15', '2026-10-30', 35000.00, 0.00, 'All Retail Shoppers', 'Planned'),
(8, 'New Branch Launch Campaign', 'Influencer', '2026-01-01', '2026-01-20', 40000.00, 38000.00, 'Mumbai Foodies & Bloggers', 'Completed'),
(9, 'Morning Coffee Push', 'Referral', '2026-09-01', '2026-09-30', 10000.00, 0.00, 'Daily Morning Commuters', 'Planned'),
(10, 'Corporate Catering Blitz', 'Other', '2026-05-01', '2026-05-31', 20000.00, 19000.00, 'Corporate HR & Event Managers', 'Completed');

-- 7. SEED SALES (Sample Invoices with Optional Campaign Links)
INSERT IGNORE INTO sales (sale_id, invoice_number, shop_id, customer_id, campaign_id, sale_date, order_type, payment_method, subtotal, discount, tax, total_amount, total_cost, total_profit)
VALUES
(1, 'BB-20260825-0001', 1, 1, 3, '2026-08-25 09:15:00', 'Dine-in', 'UPI', 370.00, 20.00, 17.50, 367.50, 135.00, 232.50),
(2, 'BB-20260825-0002', 1, 2, 6, '2026-08-25 10:30:00', 'Takeaway', 'Credit Card', 500.00, 50.00, 22.50, 472.50, 205.00, 267.50),
(3, 'BB-20260826-0003', 2, NULL, NULL, '2026-08-26 11:45:00', 'Dine-in', 'Cash', 270.00, 0.00, 13.50, 283.50, 95.00, 188.50),
(4, 'BB-20260826-0004', 3, 3, 3, '2026-08-26 14:20:00', 'Delivery', 'Wallet', 630.00, 30.00, 30.00, 630.00, 245.00, 385.00),
(5, 'BB-20260827-0005', 4, 4, 4, '2026-08-27 16:00:00', 'Takeaway', 'UPI', 380.00, 0.00, 19.00, 399.00, 140.00, 259.00),
(6, 'BB-20260827-0006', 5, NULL, NULL, '2026-08-27 17:30:00', 'Dine-in', 'Cash', 180.00, 0.00, 9.00, 189.00, 65.00, 124.00),
(7, 'BB-20260828-0007', 6, 5, 8, '2026-08-28 18:45:00', 'Dine-in', 'Credit Card', 720.00, 70.00, 32.50, 682.50, 260.00, 422.50),
(8, 'BB-20260828-0008', 1, 7, 5, '2026-08-28 20:10:00', 'Takeaway', 'UPI', 410.00, 10.00, 20.00, 420.00, 150.00, 270.00),
(9, 'BB-20260829-0009', 2, NULL, NULL, '2026-08-29 08:30:00', 'Dine-in', 'Cash', 210.00, 0.00, 10.50, 220.50, 75.00, 145.50),
(10, 'BB-20260829-0010', 3, 6, 5, '2026-08-29 12:15:00', 'Delivery', 'Debit Card', 540.00, 40.00, 25.00, 525.00, 200.00, 325.00),
(11, 'BB-20260829-0011', 4, 8, NULL, '2026-08-29 15:50:00', 'Takeaway', 'UPI', 330.00, 0.00, 16.50, 346.50, 120.00, 226.50),
(12, 'BB-20260830-0012', 5, 10, 3, '2026-08-30 11:00:00', 'Dine-in', 'UPI', 570.00, 50.00, 26.00, 546.00, 210.00, 336.00),
(13, 'BB-20260830-0013', 6, 9, NULL, '2026-08-30 13:25:00', 'Dine-in', 'Credit Card', 450.00, 0.00, 22.50, 472.50, 170.00, 302.50),
(14, 'BB-20260830-0014', 1, NULL, NULL, '2026-08-30 14:10:00', 'Takeaway', 'Cash', 260.00, 0.00, 13.00, 273.00, 95.00, 178.00),
(15, 'BB-20260830-0015', 2, 2, 6, '2026-08-30 14:40:00', 'Dine-in', 'UPI', 490.00, 30.00, 23.00, 483.00, 180.00, 303.00);

-- 8. SEED SALE ITEMS
INSERT IGNORE INTO sale_items (sale_item_id, sale_id, product_id, quantity, unit_price, item_discount, item_revenue, item_cost, item_profit)
VALUES
-- Sale 1
(1, 1, 3, 1, 180.00, 0.00, 180.00, 65.00, 115.00), -- Cappuccino
(2, 1, 7, 1, 190.00, 0.00, 190.00, 70.00, 120.00), -- Cold Coffee
-- Sale 2
(3, 2, 19, 1, 250.00, 0.00, 250.00, 95.00, 155.00), -- Cheesecake
(4, 2, 17, 1, 150.00, 0.00, 150.00, 55.00, 95.00), -- Brownie
(5, 2, 18, 1, 120.00, 0.00, 120.00, 40.00, 80.00), -- Muffin
-- Sale 3
(6, 3, 4, 1, 190.00, 0.00, 190.00, 70.00, 120.00), -- Latte
(7, 3, 20, 1, 80.00, 0.00, 80.00, 30.00, 50.00), -- Cookie
-- Sale 4
(8, 4, 13, 2, 190.00, 0.00, 380.00, 150.00, 230.00), -- Paneer Sandwich x2
(9, 4, 8, 1, 220.00, 0.00, 220.00, 85.00, 135.00), -- Cold Brew
(10, 4, 10, 1, 90.00, 0.00, 90.00, 30.00, 60.00), -- Masala Tea
-- Sale 5
(11, 5, 14, 1, 180.00, 0.00, 180.00, 70.00, 110.00), -- Veg Burger
(12, 5, 9, 1, 200.00, 0.00, 200.00, 75.00, 125.00), -- Iced Latte
-- Sale 6
(13, 6, 3, 1, 180.00, 0.00, 180.00, 65.00, 115.00), -- Cappuccino
-- Sale 7
(14, 7, 5, 2, 210.00, 0.00, 420.00, 160.00, 260.00), -- Mocha x2
(15, 7, 19, 1, 250.00, 0.00, 250.00, 95.00, 155.00), -- Cheesecake
(16, 7, 20, 1, 80.00, 0.00, 80.00, 30.00, 50.00), -- Cookie
-- Sale 8
(17, 8, 6, 1, 195.00, 0.00, 195.00, 75.00, 120.00), -- Flat White
(18, 8, 5, 1, 215.00, 0.00, 215.00, 80.00, 135.00), -- Mocha
-- Sale 9
(19, 9, 1, 1, 120.00, 0.00, 120.00, 45.00, 75.00), -- Espresso
(20, 9, 10, 1, 90.00, 0.00, 90.00, 30.00, 60.00), -- Masala Tea
-- Sale 10
(21, 10, 12, 2, 160.00, 0.00, 320.00, 120.00, 200.00), -- Veg Sandwich x2
(22, 10, 8, 1, 220.00, 0.00, 220.00, 85.00, 135.00), -- Cold Brew
-- Sale 11
(23, 11, 15, 1, 140.00, 0.00, 140.00, 50.00, 90.00), -- Garlic Bread
(24, 11, 4, 1, 190.00, 0.00, 190.00, 70.00, 120.00), -- Latte
-- Sale 12
(25, 12, 3, 2, 180.00, 0.00, 360.00, 130.00, 230.00), -- Cappuccino x2
(26, 12, 5, 1, 210.00, 0.00, 210.00, 80.00, 130.00), -- Mocha
-- Sale 13
(27, 13, 8, 1, 220.00, 0.00, 220.00, 85.00, 135.00), -- Cold Brew
(28, 13, 16, 1, 130.00, 0.00, 130.00, 45.00, 85.00), -- French Fries
(29, 13, 18, 1, 120.00, 0.00, 120.00, 40.00, 80.00), -- Muffin
-- Sale 14
(30, 14, 2, 1, 140.00, 0.00, 140.00, 50.00, 90.00), -- Americano
(31, 14, 18, 1, 120.00, 0.00, 120.00, 40.00, 80.00), -- Muffin
-- Sale 15
(32, 15, 4, 1, 190.00, 0.00, 190.00, 70.00, 120.00), -- Latte
(33, 15, 17, 2, 150.00, 0.00, 300.00, 110.00, 190.00); -- Brownie x2
