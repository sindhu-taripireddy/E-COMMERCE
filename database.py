import sqlite3
import json
import datetime
from pathlib import Path
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. USERS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS USERS (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        phone TEXT,
        role TEXT DEFAULT 'customer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. ADMIN
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ADMIN (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT DEFAULT 'superadmin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 3. CATEGORIES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CATEGORIES (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        description TEXT,
        image TEXT
    )
    ''')
    
    # 4. PRODUCTS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PRODUCTS (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        discount REAL DEFAULT 0,
        material TEXT,
        occasion TEXT,
        image TEXT NOT NULL,
        rating REAL DEFAULT 4.8,
        stock INTEGER DEFAULT 20,
        is_featured INTEGER DEFAULT 0,
        is_trending INTEGER DEFAULT 0,
        is_new INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES CATEGORIES (category_id) ON DELETE CASCADE
    )
    ''')
    
    # 5. PRODUCT_VARIANTS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PRODUCT_VARIANTS (
        variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        color TEXT,
        size TEXT,
        stock INTEGER DEFAULT 10,
        sku TEXT,
        FOREIGN KEY (product_id) REFERENCES PRODUCTS (product_id) ON DELETE CASCADE
    )
    ''')
    
    # 6. CART
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CART (
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        session_id TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES USERS (user_id) ON DELETE CASCADE
    )
    ''')
    
    # 7. CART_ITEMS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CART_ITEMS (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        variant_id INTEGER,
        quantity INTEGER NOT NULL DEFAULT 1,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cart_id) REFERENCES CART (cart_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES PRODUCTS (product_id) ON DELETE CASCADE,
        FOREIGN KEY (variant_id) REFERENCES PRODUCT_VARIANTS (variant_id) ON DELETE SET NULL
    )
    ''')
    
    # 8. WISHLIST
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS WISHLIST (
        wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        session_id TEXT,
        product_id INTEGER NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES USERS (user_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES PRODUCTS (product_id) ON DELETE CASCADE,
        UNIQUE(user_id, product_id),
        UNIQUE(session_id, product_id)
    )
    ''')
    
    # 9. ORDERS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ORDERS (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_number TEXT UNIQUE NOT NULL,
        user_id INTEGER,
        customer_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        pincode TEXT NOT NULL,
        subtotal REAL NOT NULL,
        delivery_fee REAL DEFAULT 0,
        discount_amount REAL DEFAULT 0,
        total_amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payment_status TEXT DEFAULT 'Completed',
        order_status TEXT DEFAULT 'Confirmed',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES USERS (user_id) ON DELETE SET NULL
    )
    ''')
    
    # 10. ORDER_ITEMS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ORDER_ITEMS (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER,
        variant_id INTEGER,
        product_name TEXT NOT NULL,
        color TEXT,
        size TEXT,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        subtotal REAL NOT NULL,
        image TEXT,
        FOREIGN KEY (order_id) REFERENCES ORDERS (order_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES PRODUCTS (product_id) ON DELETE SET NULL
    )
    ''')
    
    # 11. PAYMENTS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PAYMENTS (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        method TEXT NOT NULL,
        transaction_ref TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Success',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES ORDERS (order_id) ON DELETE CASCADE
    )
    ''')
    
    # 12. REVIEWS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS REVIEWS (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        user_id INTEGER,
        customer_name TEXT NOT NULL,
        rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
        comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES PRODUCTS (product_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES USERS (user_id) ON DELETE SET NULL
    )
    ''')
    
    # 13. ADDRESSES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ADDRESSES (
        address_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        pincode TEXT NOT NULL,
        is_default INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES USERS (user_id) ON DELETE CASCADE
    )
    ''')
    
    # 14. FAQ
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS FAQ (
        faq_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    )
    ''')
    
    # 15. CHAT_SESSIONS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CHAT_SESSIONS (
        session_id TEXT PRIMARY KEY,
        user_id INTEGER,
        preferences TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES USERS (user_id) ON DELETE CASCADE
    )
    ''')
    
    # 16. CHAT_MESSAGES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CHAT_MESSAGES (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        metadata TEXT DEFAULT '{}',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES CHAT_SESSIONS (session_id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()

# --- Product Query Functions ---
def get_categories():
    conn = get_db()
    categories = conn.execute("SELECT * FROM CATEGORIES ORDER BY category_id ASC").fetchall()
    conn.close()
    return [dict(c) for c in categories]

def get_category_by_slug(slug):
    conn = get_db()
    cat = conn.execute("SELECT * FROM CATEGORIES WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    return dict(cat) if cat else None

def get_all_products(category_slug=None, search=None, min_price=None, max_price=None, 
                     color=None, size=None, occasion=None, sort_by="featured", limit=100):
    conn = get_db()
    query = '''
    SELECT p.*, c.name as category_name, c.slug as category_slug,
           (SELECT GROUP_CONCAT(DISTINCT pv.color) FROM PRODUCT_VARIANTS pv WHERE pv.product_id = p.product_id) as available_colors,
           (SELECT GROUP_CONCAT(DISTINCT pv.size) FROM PRODUCT_VARIANTS pv WHERE pv.product_id = p.product_id) as available_sizes
    FROM PRODUCTS p
    JOIN CATEGORIES c ON p.category_id = c.category_id
    WHERE 1=1
    '''
    params = []
    
    if category_slug:
        query += " AND c.slug = ?"
        params.append(category_slug)
        
    if search:
        query += " AND (p.product_name LIKE ? OR p.description LIKE ? OR p.material LIKE ? OR p.occasion LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])
        
    if min_price is not None:
        query += " AND (p.price - (p.price * p.discount / 100)) >= ?"
        params.append(float(min_price))
        
    if max_price is not None:
        query += " AND (p.price - (p.price * p.discount / 100)) <= ?"
        params.append(float(max_price))
        
    if occasion:
        query += " AND p.occasion LIKE ?"
        params.append(f"%{occasion}%")
        
    if color:
        query += " AND p.product_id IN (SELECT product_id FROM PRODUCT_VARIANTS WHERE color LIKE ?)"
        params.append(f"%{color}%")
        
    if size:
        query += " AND p.product_id IN (SELECT product_id FROM PRODUCT_VARIANTS WHERE size = ?)"
        params.append(size)
        
    # Sorting
    if sort_by == "price_low":
        query += " ORDER BY (p.price - (p.price * p.discount / 100)) ASC"
    elif sort_by == "price_high":
        query += " ORDER BY (p.price - (p.price * p.discount / 100)) DESC"
    elif sort_by == "newest":
        query += " ORDER BY p.is_new DESC, p.created_at DESC"
    elif sort_by == "rating":
        query += " ORDER BY p.rating DESC"
    elif sort_by == "best_selling":
        query += " ORDER BY p.is_trending DESC, p.rating DESC"
    else: # featured
        query += " ORDER BY p.is_featured DESC, p.rating DESC, p.product_id DESC"
        
    query += " LIMIT ?"
    params.append(limit)
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    products = []
    for r in rows:
        d = dict(r)
        d['final_price'] = round(d['price'] * (1 - d['discount'] / 100))
        d['colors_list'] = d['available_colors'].split(',') if d['available_colors'] else []
        d['sizes_list'] = d['available_sizes'].split(',') if d['available_sizes'] else []
        products.append(d)
    return products

def get_product_by_id(product_id):
    conn = get_db()
    row = conn.execute('''
    SELECT p.*, c.name as category_name, c.slug as category_slug
    FROM PRODUCTS p
    JOIN CATEGORIES c ON p.category_id = c.category_id
    WHERE p.product_id = ?
    ''', (product_id,)).fetchone()
    
    if not row:
        conn.close()
        return None
        
    product = dict(row)
    product['final_price'] = round(product['price'] * (1 - product['discount'] / 100))
    
    # Variants
    variants = conn.execute('''
    SELECT * FROM PRODUCT_VARIANTS WHERE product_id = ? ORDER BY color, size
    ''', (product_id,)).fetchall()
    product['variants'] = [dict(v) for v in variants]
    
    # Extract unique colors & sizes
    colors = set()
    sizes = set()
    for v in product['variants']:
        if v['color']:
            colors.add(v['color'])
        if v['size']:
            sizes.add(v['size'])
    product['colors'] = sorted(list(colors))
    product['sizes'] = sorted(list(sizes))
    
    # Reviews
    reviews = conn.execute('''
    SELECT * FROM REVIEWS WHERE product_id = ? ORDER BY created_at DESC
    ''', (product_id,)).fetchall()
    product['reviews'] = [dict(rev) for rev in reviews]
    product['review_count'] = len(product['reviews'])
    
    conn.close()
    return product

def get_featured_products(limit=8):
    return get_all_products(sort_by="featured", limit=limit)

def get_trending_products(limit=8):
    return get_all_products(sort_by="best_selling", limit=limit)

def get_new_arrivals(limit=8):
    return get_all_products(sort_by="newest", limit=limit)

# --- Cart Operations ---
def get_or_create_cart(user_id=None, session_id=None):
    conn = get_db()
    cursor = conn.cursor()
    
    cart = None
    if user_id:
        cart = cursor.execute("SELECT * FROM CART WHERE user_id = ?", (user_id,)).fetchone()
    elif session_id:
        cart = cursor.execute("SELECT * FROM CART WHERE session_id = ?", (session_id,)).fetchone()
        
    if not cart:
        cursor.execute("INSERT INTO CART (user_id, session_id) VALUES (?, ?)", (user_id, session_id))
        conn.commit()
        cart_id = cursor.lastrowid
        cart = cursor.execute("SELECT * FROM CART WHERE cart_id = ?", (cart_id,)).fetchone()
        
    conn.close()
    return dict(cart)

def add_to_cart(cart_id, product_id, variant_id=None, quantity=1):
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if existing item in cart with same product and variant
    if variant_id:
        existing = cursor.execute('''
        SELECT * FROM CART_ITEMS WHERE cart_id = ? AND product_id = ? AND variant_id = ?
        ''', (cart_id, product_id, variant_id)).fetchone()
    else:
        existing = cursor.execute('''
        SELECT * FROM CART_ITEMS WHERE cart_id = ? AND product_id = ? AND variant_id IS NULL
        ''', (cart_id, product_id)).fetchone()
        
    if existing:
        new_qty = existing['quantity'] + quantity
        cursor.execute("UPDATE CART_ITEMS SET quantity = ? WHERE item_id = ?", (new_qty, existing['item_id']))
    else:
        cursor.execute('''
        INSERT INTO CART_ITEMS (cart_id, product_id, variant_id, quantity)
        VALUES (?, ?, ?, ?)
        ''', (cart_id, product_id, variant_id, quantity))
        
    conn.commit()
    conn.close()
    return True

def get_cart_details(cart_id):
    conn = get_db()
    rows = conn.execute('''
    SELECT ci.item_id, ci.quantity, ci.variant_id, p.product_id, p.product_name, p.price, 
           p.discount, p.image, p.stock, pv.color, pv.size, pv.sku
    FROM CART_ITEMS ci
    JOIN PRODUCTS p ON ci.product_id = p.product_id
    LEFT JOIN PRODUCT_VARIANTS pv ON ci.variant_id = pv.variant_id
    WHERE ci.cart_id = ?
    ORDER BY ci.added_at DESC
    ''', (cart_id,)).fetchall()
    conn.close()
    
    items = []
    subtotal = 0
    total_items = 0
    for r in rows:
        item = dict(r)
        final_unit_price = round(item['price'] * (1 - item['discount'] / 100))
        item['unit_price'] = final_unit_price
        item['line_total'] = final_unit_price * item['quantity']
        subtotal += item['line_total']
        total_items += item['quantity']
        items.append(item)
        
    # Delivery fee rules: Free over ₹499, otherwise ₹49
    delivery_fee = 0 if (subtotal >= 499 or subtotal == 0) else 49
    total = subtotal + delivery_fee
    
    return {
        'items': items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
        'total_items': total_items,
        'free_shipping_threshold': 499,
        'free_shipping_remaining': max(0, 499 - subtotal)
    }

def update_cart_item(item_id, quantity):
    conn = get_db()
    if quantity <= 0:
        conn.execute("DELETE FROM CART_ITEMS WHERE item_id = ?", (item_id,))
    else:
        conn.execute("UPDATE CART_ITEMS SET quantity = ? WHERE item_id = ?", (quantity, item_id))
    conn.commit()
    conn.close()

def remove_cart_item(item_id):
    conn = get_db()
    conn.execute("DELETE FROM CART_ITEMS WHERE item_id = ?", (item_id,))
    conn.commit()
    conn.close()

def clear_cart(cart_id):
    conn = get_db()
    conn.execute("DELETE FROM CART_ITEMS WHERE cart_id = ?", (cart_id,))
    conn.commit()
    conn.close()

# --- Wishlist Operations ---
def toggle_wishlist(user_id=None, session_id=None, product_id=None):
    conn = get_db()
    cursor = conn.cursor()
    
    if user_id:
        existing = cursor.execute("SELECT * FROM WISHLIST WHERE user_id = ? AND product_id = ?", (user_id, product_id)).fetchone()
    else:
        existing = cursor.execute("SELECT * FROM WISHLIST WHERE session_id = ? AND product_id = ?", (session_id, product_id)).fetchone()
        
    is_in_wishlist = False
    if existing:
        cursor.execute("DELETE FROM WISHLIST WHERE wishlist_id = ?", (existing['wishlist_id'],))
        is_in_wishlist = False
    else:
        cursor.execute("INSERT INTO WISHLIST (user_id, session_id, product_id) VALUES (?, ?, ?)", (user_id, session_id, product_id))
        is_in_wishlist = True
        
    conn.commit()
    conn.close()
    return is_in_wishlist

def get_wishlist_items(user_id=None, session_id=None):
    conn = get_db()
    if user_id:
        rows = conn.execute('''
        SELECT w.wishlist_id, p.*, c.name as category_name
        FROM WISHLIST w
        JOIN PRODUCTS p ON w.product_id = p.product_id
        JOIN CATEGORIES c ON p.category_id = c.category_id
        WHERE w.user_id = ?
        ORDER BY w.added_at DESC
        ''', (user_id,)).fetchall()
    else:
        rows = conn.execute('''
        SELECT w.wishlist_id, p.*, c.name as category_name
        FROM WISHLIST w
        JOIN PRODUCTS p ON w.product_id = p.product_id
        JOIN CATEGORIES c ON p.category_id = c.category_id
        WHERE w.session_id = ?
        ORDER BY w.added_at DESC
        ''', (session_id,)).fetchall()
    conn.close()
    
    res = []
    for r in rows:
        d = dict(r)
        d['final_price'] = round(d['price'] * (1 - d['discount'] / 100))
        res.append(d)
    return res

# --- Order Operations ---
def generate_tracking_number():
    import random
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    rand_suffix = f"{random.randint(100, 999)}"
    return f"KK{today_str}{rand_suffix}"

def create_order(user_id, customer_name, email, phone, address, city, state, pincode,
                 cart_details, payment_method="UPI", discount_code=None, notes=""):
    conn = get_db()
    cursor = conn.cursor()
    
    tracking_number = generate_tracking_number()
    subtotal = cart_details['subtotal']
    delivery_fee = cart_details['delivery_fee']
    discount_amount = 0
    
    # Optional coupon logic
    if discount_code and discount_code.upper() in ["KK10", "WELCOME10", "KKFIRST10"]:
        discount_amount = round(subtotal * 0.10)
        
    total_amount = max(0, subtotal + delivery_fee - discount_amount)
    
    cursor.execute('''
    INSERT INTO ORDERS (
        tracking_number, user_id, customer_name, email, phone,
        address, city, state, pincode, subtotal, delivery_fee,
        discount_amount, total_amount, payment_method, payment_status,
        order_status, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Completed', 'Confirmed', ?)
    ''', (
        tracking_number, user_id, customer_name, email, phone,
        address, city, state, pincode, subtotal, delivery_fee,
        discount_amount, total_amount, payment_method, notes
    ))
    order_id = cursor.lastrowid
    
    # Order items
    for item in cart_details['items']:
        cursor.execute('''
        INSERT INTO ORDER_ITEMS (
            order_id, product_id, variant_id, product_name,
            color, size, price, quantity, subtotal, image
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_id, item['product_id'], item.get('variant_id'), item['product_name'],
            item.get('color'), item.get('size'), item['unit_price'], item['quantity'],
            item['line_total'], item.get('image')
        ))
        
        # Deduct stock
        cursor.execute("UPDATE PRODUCTS SET stock = MAX(0, stock - ?) WHERE product_id = ?", 
                       (item['quantity'], item['product_id']))
        if item.get('variant_id'):
            cursor.execute("UPDATE PRODUCT_VARIANTS SET stock = MAX(0, stock - ?) WHERE variant_id = ?",
                           (item['quantity'], item['variant_id']))
            
    # Record payment
    cursor.execute('''
    INSERT INTO PAYMENTS (order_id, method, transaction_ref, amount, status)
    VALUES (?, ?, ?, ?, 'Success')
    ''', (order_id, payment_method, f"TXN_{tracking_number}", total_amount))
    
    conn.commit()
    conn.close()
    
    return {
        'order_id': order_id,
        'tracking_number': tracking_number,
        'total_amount': total_amount
    }

def get_order_by_tracking(tracking_number):
    conn = get_db()
    # Normalize input
    clean_tracking = tracking_number.strip().upper().replace("#", "")
    order = conn.execute("SELECT * FROM ORDERS WHERE tracking_number = ?", (clean_tracking,)).fetchone()
    if not order:
        conn.close()
        return None
        
    order_dict = dict(order)
    items = conn.execute("SELECT * FROM ORDER_ITEMS WHERE order_id = ?", (order_dict['order_id'],)).fetchall()
    order_dict['items'] = [dict(i) for i in items]
    
    payment = conn.execute("SELECT * FROM PAYMENTS WHERE order_id = ?", (order_dict['order_id'],)).fetchone()
    order_dict['payment'] = dict(payment) if payment else None
    
    conn.close()
    return order_dict

def get_order_by_id(order_id):
    conn = get_db()
    order = conn.execute("SELECT * FROM ORDERS WHERE order_id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        return None
        
    order_dict = dict(order)
    items = conn.execute("SELECT * FROM ORDER_ITEMS WHERE order_id = ?", (order_dict['order_id'],)).fetchall()
    order_dict['items'] = [dict(i) for i in items]
    conn.close()
    return order_dict

def get_user_orders(user_id):
    conn = get_db()
    rows = conn.execute('''
    SELECT * FROM ORDERS WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    
    orders = []
    for r in rows:
        od = dict(r)
        items = conn.execute("SELECT * FROM ORDER_ITEMS WHERE order_id = ?", (od['order_id'],)).fetchall()
        od['items'] = [dict(i) for i in items]
        orders.append(od)
        
    conn.close()
    return orders

def get_all_orders(status=None):
    conn = get_db()
    if status and status != 'All':
        rows = conn.execute("SELECT * FROM ORDERS WHERE order_status = ? ORDER BY created_at DESC", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM ORDERS ORDER BY created_at DESC").fetchall()
        
    orders = []
    for r in rows:
        od = dict(r)
        items = conn.execute("SELECT * FROM ORDER_ITEMS WHERE order_id = ?", (od['order_id'],)).fetchall()
        od['items'] = [dict(i) for i in items]
        orders.append(od)
        
    conn.close()
    return orders

def update_order_status(order_id, new_status):
    conn = get_db()
    conn.execute("UPDATE ORDERS SET order_status = ? WHERE order_id = ?", (new_status, order_id))
    conn.commit()
    conn.close()

# --- Admin & Analytics ---
def get_dashboard_metrics():
    conn = get_db()
    total_sales = conn.execute("SELECT COALESCE(SUM(total_amount), 0) FROM ORDERS WHERE order_status != 'Cancelled'").fetchone()[0]
    total_orders = conn.execute("SELECT COUNT(*) FROM ORDERS").fetchone()[0]
    total_products = conn.execute("SELECT COUNT(*) FROM PRODUCTS").fetchone()[0]
    total_customers = conn.execute("SELECT COUNT(*) FROM USERS WHERE role = 'customer'").fetchone()[0]
    low_stock_count = conn.execute("SELECT COUNT(*) FROM PRODUCTS WHERE stock <= 5").fetchone()[0]
    
    # Recent orders
    recent_orders_rows = conn.execute('''
    SELECT * FROM ORDERS ORDER BY created_at DESC LIMIT 5
    ''').fetchall()
    recent_orders = [dict(r) for r in recent_orders_rows]
    
    # Category sales distribution
    category_sales_rows = conn.execute('''
    SELECT c.name, COALESCE(SUM(oi.subtotal), 0) as total_revenue, COUNT(oi.order_item_id) as items_sold
    FROM CATEGORIES c
    LEFT JOIN PRODUCTS p ON c.category_id = p.category_id
    LEFT JOIN ORDER_ITEMS oi ON p.product_id = oi.product_id
    GROUP BY c.category_id
    ORDER BY total_revenue DESC
    ''').fetchall()
    category_sales = [dict(r) for r in category_sales_rows]
    
    # Top selling products
    top_products_rows = conn.execute('''
    SELECT p.product_id, p.product_name, p.image, p.price, COALESCE(SUM(oi.quantity), 0) as sold_count,
           COALESCE(SUM(oi.subtotal), 0) as revenue
    FROM PRODUCTS p
    LEFT JOIN ORDER_ITEMS oi ON p.product_id = oi.product_id
    GROUP BY p.product_id
    ORDER BY sold_count DESC
    LIMIT 5
    ''').fetchall()
    top_products = [dict(r) for r in top_products_rows]
    
    conn.close()
    return {
        'total_sales': round(total_sales, 2),
        'total_orders': total_orders,
        'total_products': total_products,
        'total_customers': total_customers,
        'low_stock_count': low_stock_count,
        'recent_orders': recent_orders,
        'category_sales': category_sales,
        'top_products': top_products
    }

# --- Chat & AI Database Functions ---
def get_or_create_chat_session(session_id, user_id=None):
    conn = get_db()
    cursor = conn.cursor()
    session = cursor.execute("SELECT * FROM CHAT_SESSIONS WHERE session_id = ?", (session_id,)).fetchone()
    if not session:
        cursor.execute("INSERT INTO CHAT_SESSIONS (session_id, user_id) VALUES (?, ?)", (session_id, user_id))
        conn.commit()
        session = cursor.execute("SELECT * FROM CHAT_SESSIONS WHERE session_id = ?", (session_id,)).fetchone()
    conn.close()
    return dict(session)

def save_chat_message(session_id, sender, message, metadata=None):
    conn = get_db()
    cursor = conn.cursor()
    meta_json = json.dumps(metadata or {})
    cursor.execute('''
    INSERT INTO CHAT_MESSAGES (session_id, sender, message, metadata)
    VALUES (?, ?, ?, ?)
    ''', (session_id, sender, message, meta_json))
    cursor.execute("UPDATE CHAT_SESSIONS SET last_active = CURRENT_TIMESTAMP WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

def get_chat_history(session_id, limit=20):
    conn = get_db()
    rows = conn.execute('''
    SELECT * FROM CHAT_MESSAGES WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?
    ''', (session_id, limit)).fetchall()
    conn.close()
    
    history = []
    for r in rows:
        d = dict(r)
        try:
            d['metadata'] = json.loads(d['metadata'])
        except:
            d['metadata'] = {}
        history.append(d)
    return history

def get_session_preferences(session_id):
    conn = get_db()
    row = conn.execute("SELECT preferences FROM CHAT_SESSIONS WHERE session_id = ?", (session_id,)).fetchone()
    conn.close()
    if row and row['preferences']:
        try:
            return json.loads(row['preferences'])
        except:
            return {}
    return {}

def update_session_preferences(session_id, new_prefs):
    current = get_session_preferences(session_id)
    current.update(new_prefs)
    conn = get_db()
    conn.execute("UPDATE CHAT_SESSIONS SET preferences = ? WHERE session_id = ?", (json.dumps(current), session_id))
    conn.commit()
    conn.close()
    return current

# --- FAQs and Reviews ---
def get_all_faqs():
    conn = get_db()
    rows = conn.execute("SELECT * FROM FAQ ORDER BY category, faq_id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_review(product_id, user_id, customer_name, rating, comment):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO REVIEWS (product_id, user_id, customer_name, rating, comment)
    VALUES (?, ?, ?, ?, ?)
    ''', (product_id, user_id, customer_name, rating, comment))
    
    # Recalculate average product rating
    avg_rating = cursor.execute("SELECT AVG(rating) FROM REVIEWS WHERE product_id = ?", (product_id,)).fetchone()[0]
    if avg_rating:
        cursor.execute("UPDATE PRODUCTS SET rating = ? WHERE product_id = ?", (round(avg_rating, 1), product_id))
        
    conn.commit()
    conn.close()
