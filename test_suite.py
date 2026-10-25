import sys
import json
from app import app
import database as db

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

def run_tests():
    print("=" * 60)
    print("KK_COLLECTIONS — Comprehensive Verification Test Suite")
    print("=" * 60)

    client = app.test_client()
    passed = 0
    total = 0

    def assert_test(name, condition, extra=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f" [PASS] {name} {extra}")
        else:
            print(f" [FAIL] {name} {extra}")

    # 1. Database sanity check
    conn = db.get_db()
    prod_count = conn.execute("SELECT COUNT(*) FROM PRODUCTS").fetchone()[0]
    var_count = conn.execute("SELECT COUNT(*) FROM PRODUCT_VARIANTS").fetchone()[0]
    conn.close()
    assert_test("Database Seed Check", prod_count >= 35 and var_count >= 80, f"(Products: {prod_count}, Variants: {var_count})")

    # 2. Home Page
    res = client.get('/')
    assert_test("Home Page Loads", res.status_code == 200 and b"Elegance That Completes You" in res.data)

    # 3. Shop Page & Filtering
    res = client.get('/shop')
    assert_test("Shop Catalog Loads", res.status_code == 200 and b"All Handcrafted Accessories" in res.data)

    res_filter = client.get('/shop?category=bangles&max_price=400')
    assert_test("Shop Filter (Category & Price)", res_filter.status_code == 200 and b"Bangles" in res_filter.data)

    # 4. Product Details
    res = client.get('/product/1')
    assert_test("Product Details Page", res.status_code == 200 and b"Ask KK AI About This Product" in res.data)

    # 5. Cart Operations API
    add_res = client.post('/api/cart/add', json={'product_id': 1, 'quantity': 2})
    add_data = json.loads(add_res.data)
    assert_test("API Add to Cart", add_res.status_code == 200 and add_data.get('success') is True)

    cart_view_res = client.get('/cart')
    assert_test("Cart Page View", cart_view_res.status_code == 200 and b"Order Summary" in cart_view_res.data)

    # 6. Coupon Application API
    coupon_res = client.post('/api/coupon/apply', json={'code': 'KKFIRST10', 'subtotal': 500})
    coupon_data = json.loads(coupon_res.data)
    assert_test("API Coupon Code Validation", coupon_res.status_code == 200 and coupon_data.get('discount') == 50)

    # 7. Wishlist Toggle API
    wish_res = client.post('/api/wishlist/toggle', json={'product_id': 2})
    wish_data = json.loads(wish_res.data)
    assert_test("API Wishlist Toggle", wish_res.status_code == 200 and wish_data.get('success') is True)

    # 8. Checkout Order Placement
    order_post_res = client.post('/checkout', data={
        'name': 'Test Patron',
        'email': 'patron@example.com',
        'phone': '+91 99999 88888',
        'address': 'Plot 10, Brigade Road',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'pincode': '560001',
        'payment_method': 'UPI'
    }, follow_redirects=True)
    assert_test("Checkout & Order Placement", order_post_res.status_code == 200 and b"Order Successfully Placed" in order_post_res.data)

    # 9. Order Tracking Timeline
    track_res = client.get('/track-order?tracking=KK20260918001')
    assert_test("Order Tracking Timeline", track_res.status_code == 200 and b"KK20260918001" in track_res.data)

    # 10. AI Shopping Assistant Queries
    # 10a: Product Discovery
    chat1 = client.post('/api/chat', json={'message': 'Show me thread bangles'})
    chat1_data = json.loads(chat1.data)
    assert_test("AI Chat: Product Discovery", len(chat1_data.get('products', [])) > 0 and 'thread bangles' in chat1_data.get('text', '').lower())

    # 10b: Budget Shopping
    chat2 = client.post('/api/chat', json={'message': 'I need earrings under 300'})
    chat2_data = json.loads(chat2.data)
    assert_test("AI Chat: Budget-Based Filter", len(chat2_data.get('products', [])) > 0 and '300' in chat2_data.get('text', ''))

    # 10c: Color Matching
    chat3 = client.post('/api/chat', json={'message': 'I am wearing a green saree. What accessories will match?'})
    chat3_data = json.loads(chat3.data)
    assert_test("AI Chat: Saree Color Matching", 'green' in chat3_data.get('text', '').lower() and len(chat3_data.get('products', [])) > 0)

    # 10d: Combo Set Recommendation
    chat4 = client.post('/api/chat', json={'message': 'Can you create a matching set?'})
    chat4_data = json.loads(chat4.data)
    assert_test("AI Chat: Combo Recommendations", 'bangles' in chat4_data.get('text', '').lower() and 'combo_info' in chat4_data)

    # 10e: Order Tracking through Chat
    chat5 = client.post('/api/chat', json={'message': 'Where is my order #KK20260918001?'})
    chat5_data = json.loads(chat5.data)
    assert_test("AI Chat: Order Status Assistance", 'KK20260918001' in chat5_data.get('text', '') and 'order_info' in chat5_data)

    # 11. Admin Authentication & Dashboard
    admin_login_res = client.post('/admin/login', data={'email': 'admin@kkcollections.com', 'password': 'admin123'}, follow_redirects=True)
    assert_test("Admin Portal Login", admin_login_res.status_code == 200 and b"Store Performance Dashboard" in admin_login_res.data)

    dash_res = client.get('/admin')
    assert_test("Admin Dashboard Metrics", dash_res.status_code == 200 and b"Active Products" in dash_res.data)

    inv_res = client.get('/admin/inventory')
    assert_test("Admin Inventory Table", inv_res.status_code == 200 and b"Inventory Status" in inv_res.data)

    orders_res = client.get('/admin/orders')
    assert_test("Admin Orders Management", orders_res.status_code == 200 and b"Orders Management" in orders_res.data)

    cust_res = client.get('/admin/customers')
    assert_test("Admin Customers CRM", cust_res.status_code == 200 and b"Customer Accounts" in cust_res.data)

    analytics_res = client.get('/admin/analytics')
    assert_test("Admin Sales Analytics", analytics_res.status_code == 200 and b"Store Sales & Revenue Analytics" in analytics_res.data)

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed ({round(passed/total*100)}%)")
    print("=" * 60)
    return passed == total

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
