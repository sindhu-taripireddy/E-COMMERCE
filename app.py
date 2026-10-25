import os
import uuid
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, flash
)
from werkzeug.security import check_password_hash, generate_password_hash
from config import Config
import database as db
from ai_assistant import ai_assistant

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database tables exist and are seeded
try:
    from demo_data import seed_database
    seed_database()
except Exception as _e:
    print(f"Database auto-init note: {_e}")

# --- Helpers & Decorators ---
def get_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in as an administrator to access this page.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to access your account.", "info")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_global_context():
    sess_id = get_session_id()
    user_id = session.get("user_id")
    
    # Cart details
    cart = db.get_or_create_cart(user_id=user_id, session_id=sess_id)
    cart_details = db.get_cart_details(cart["cart_id"])
    
    # Wishlist count
    wishlist_items = db.get_wishlist_items(user_id=user_id, session_id=sess_id)
    
    # Categories
    categories = db.get_categories()
    
    return {
        "store_name": Config.STORE_NAME,
        "tagline": Config.TAGLINE,
        "secondary_tagline": Config.SECONDARY_TAGLINE,
        "instagram_url": Config.INSTAGRAM_URL,
        "cart_count": cart_details["total_items"],
        "cart_total": cart_details["subtotal"],
        "wishlist_count": len(wishlist_items),
        "nav_categories": categories,
        "current_user_name": session.get("user_name"),
        "is_authenticated": bool(session.get("user_id")),
        "is_admin": bool(session.get("admin_logged_in"))
    }

# --- Customer Facing Routes ---
@app.route("/")
def home():
    featured_products = db.get_featured_products(limit=8)
    trending_products = db.get_trending_products(limit=8)
    new_arrivals = db.get_new_arrivals(limit=8)
    categories = db.get_categories()
    return render_template(
        "index.html",
        featured_products=featured_products,
        trending_products=trending_products,
        new_arrivals=new_arrivals,
        categories=categories
    )

@app.route("/shop")
def shop():
    category_slug = request.args.get("category")
    search = request.args.get("search")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    color = request.args.get("color")
    size = request.args.get("size")
    occasion = request.args.get("occasion")
    sort_by = request.args.get("sort_by", "featured")
    
    products = db.get_all_products(
        category_slug=category_slug,
        search=search,
        min_price=min_price,
        max_price=max_price,
        color=color,
        size=size,
        occasion=occasion,
        sort_by=sort_by
    )
    
    categories = db.get_categories()
    active_category = db.get_category_by_slug(category_slug) if category_slug else None
    
    return render_template(
        "shop.html",
        products=products,
        categories=categories,
        active_category=active_category,
        current_category=category_slug,
        current_search=search,
        current_sort=sort_by,
        current_color=color,
        current_size=size,
        current_occasion=occasion,
        current_max_price=max_price or 1500
    )

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = db.get_product_by_id(product_id)
    if not product:
        flash("The requested accessory could not be found.", "warning")
        return redirect(url_for("shop"))
        
    # Related products from same category
    related = db.get_all_products(category_slug=product["category_slug"], limit=4)
    related = [p for p in related if p["product_id"] != product_id]
    
    return render_template("product_detail.html", product=product, related_products=related)

# --- Cart & Checkout ---
@app.route("/cart")
def cart_view():
    sess_id = get_session_id()
    user_id = session.get("user_id")
    cart = db.get_or_create_cart(user_id=user_id, session_id=sess_id)
    cart_details = db.get_cart_details(cart["cart_id"])
    return render_template("cart.html", cart=cart_details)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    sess_id = get_session_id()
    user_id = session.get("user_id")
    cart = db.get_or_create_cart(user_id=user_id, session_id=sess_id)
    cart_details = db.get_cart_details(cart["cart_id"])
    
    if not cart_details["items"]:
        flash("Your shopping cart is currently empty.", "info")
        return redirect(url_for("shop"))
        
    if request.method == "POST":
        customer_name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        pincode = request.form.get("pincode", "").strip()
        payment_method = request.form.get("payment_method", "UPI")
        discount_code = request.form.get("discount_code", "").strip()
        notes = request.form.get("notes", "").strip()
        
        if not (customer_name and email and phone and address and city and state and pincode):
            flash("Please complete all required shipping fields.", "danger")
            return render_template("checkout.html", cart=cart_details)
            
        order_res = db.create_order(
            user_id=user_id,
            customer_name=customer_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            cart_details=cart_details,
            payment_method=payment_method,
            discount_code=discount_code,
            notes=notes
        )
        
        # Clear cart upon successful order
        db.clear_cart(cart["cart_id"])
        
        # Save order tracking in session for quick access
        session["last_order_id"] = order_res["order_id"]
        session["last_tracking_number"] = order_res["tracking_number"]
        
        return redirect(url_for("order_confirmation", order_id=order_res["order_id"]))
        
    # Pre-fill address if logged in
    user_address = None
    if user_id:
        conn = db.get_db()
        addr_row = conn.execute("SELECT * FROM ADDRESSES WHERE user_id = ? ORDER BY is_default DESC LIMIT 1", (user_id,)).fetchone()
        conn.close()
        if addr_row:
            user_address = dict(addr_row)
            
    return render_template("checkout.html", cart=cart_details, saved_address=user_address)

@app.route("/order-confirmation/<int:order_id>")
def order_confirmation(order_id):
    order = db.get_order_by_id(order_id)
    if not order:
        flash("Order details not found.", "warning")
        return redirect(url_for("home"))
    return render_template("order_confirmation.html", order=order)

@app.route("/track-order")
def track_order_page():
    tracking_number = request.args.get("tracking")
    order = None
    if tracking_number:
        order = db.get_order_by_tracking(tracking_number)
        if not order:
            flash(f"No order found for tracking ID #{tracking_number}. Please check your order details.", "warning")
    return render_template("order_tracking.html", order=order, query_tracking=tracking_number)

@app.route("/track/<tracking_number>")
def track_order_direct(tracking_number):
    order = db.get_order_by_tracking(tracking_number)
    return render_template("order_tracking.html", order=order, query_tracking=tracking_number)

@app.route("/my-orders")
@login_required
def my_orders():
    user_id = session.get("user_id")
    orders = db.get_user_orders(user_id)
    return render_template("my_orders.html", orders=orders)

@app.route("/wishlist")
def wishlist_view():
    sess_id = get_session_id()
    user_id = session.get("user_id")
    items = db.get_wishlist_items(user_id=user_id, session_id=sess_id)
    return render_template("wishlist.html", items=items)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/faq")
def faq():
    faqs = db.get_all_faqs()
    # Group by category
    faq_groups = {}
    for f in faqs:
        faq_groups.setdefault(f["category"], []).append(f)
    return render_template("faq.html", faq_groups=faq_groups)

# --- Customer Authentication ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("home"))
        
    next_page = request.args.get("next") or url_for("home")
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        conn = db.get_db()
        user = conn.execute("SELECT * FROM USERS WHERE email = ?", (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            flash(f"Welcome back, {user['name']}! 💕", "success")
            return redirect(next_page)
        else:
            flash("Invalid email or password. Please try again.", "danger")
            
    return render_template("auth/login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("home"))
        
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        
        if not (name and email and password):
            flash("Please fill in all required fields.", "warning")
            return render_template("auth/register.html")
            
        conn = db.get_db()
        existing = conn.execute("SELECT * FROM USERS WHERE email = ?", (email,)).fetchone()
        if existing:
            conn.close()
            flash("An account with this email already exists. Please sign in.", "info")
            return redirect(url_for("login"))
            
        hashed_pw = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO USERS (name, email, password_hash, phone) VALUES (?, ?, ?, ?)",
                       (name, email, hashed_pw, phone))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        session["user_id"] = user_id
        session["user_name"] = name
        session["user_email"] = email
        flash("Your KK_COLLECTIONS account has been created! Welcome to our family. 💕", "success")
        return redirect(url_for("home"))
        
    return render_template("auth/register.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("user_email", None)
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("home"))

# --- REST APIs for Front-End Interactions ---
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    current_product_id = data.get("current_product_id")
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
        
    sess_id = get_session_id()
    user_id = session.get("user_id")
    
    # Ensure session exists in CHAT_SESSIONS table for foreign key constraint
    db.get_or_create_chat_session(sess_id, user_id)
    
    # Save user message
    db.save_chat_message(sess_id, "user", message)
    
    # Process through AI Assistant engine
    response = ai_assistant.process_message(
        message=message,
        session_id=sess_id,
        user_id=user_id,
        current_product_id=current_product_id
    )
    
    # Save AI response
    db.save_chat_message(sess_id, "ai", response["text"], metadata=response)
    
    return jsonify(response)

@app.route("/api/chat/history", methods=["GET"])
def api_chat_history():
    sess_id = get_session_id()
    history = db.get_chat_history(sess_id, limit=30)
    return jsonify({"history": history})

@app.route("/api/cart/add", methods=["POST"])
def api_cart_add():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    variant_id = data.get("variant_id")
    quantity = int(data.get("quantity", 1))
    
    if not product_id:
        return jsonify({"success": False, "error": "Product ID required"}), 400
        
    sess_id = get_session_id()
    user_id = session.get("user_id")
    cart = db.get_or_create_cart(user_id=user_id, session_id=sess_id)
    
    db.add_to_cart(cart["cart_id"], product_id, variant_id, quantity)
    updated_cart = db.get_cart_details(cart["cart_id"])
    
    return jsonify({
        "success": True,
        "message": "Added to your shopping bag! 💕",
        "cart": updated_cart
    })

@app.route("/api/cart/update", methods=["POST"])
def api_cart_update():
    data = request.get_json() or {}
    item_id = data.get("item_id")
    quantity = int(data.get("quantity", 1))
    
    db.update_cart_item(item_id, quantity)
    
    sess_id = get_session_id()
    user_id = session.get("user_id")
    cart = db.get_or_create_cart(user_id=user_id, session_id=sess_id)
    updated_cart = db.get_cart_details(cart["cart_id"])
    
    return jsonify({"success": True, "cart": updated_cart})

@app.route("/api/cart/remove", methods=["POST"])
def api_cart_remove():
    data = request.get_json() or {}
    item_id = data.get("item_id")
    
    db.remove_cart_item(item_id)
    
    sess_id = get_session_id()
    user_id = session.get("user_id")
    cart = db.get_or_create_cart(user_id=user_id, session_id=sess_id)
    updated_cart = db.get_cart_details(cart["cart_id"])
    
    return jsonify({"success": True, "cart": updated_cart})

@app.route("/api/cart/count", methods=["GET"])
def api_cart_count():
    sess_id = get_session_id()
    user_id = session.get("user_id")
    cart = db.get_or_create_cart(user_id=user_id, session_id=sess_id)
    cart_details = db.get_cart_details(cart["cart_id"])
    return jsonify({
        "total_items": cart_details["total_items"],
        "subtotal": cart_details["subtotal"]
    })

@app.route("/api/wishlist/toggle", methods=["POST"])
def api_wishlist_toggle():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    
    if not product_id:
        return jsonify({"success": False, "error": "Product ID required"}), 400
        
    sess_id = get_session_id()
    user_id = session.get("user_id")
    
    is_in_wishlist = db.toggle_wishlist(user_id=user_id, session_id=sess_id, product_id=product_id)
    items = db.get_wishlist_items(user_id=user_id, session_id=sess_id)
    
    msg = "Added to your wishlist 💕" if is_in_wishlist else "Removed from your wishlist"
    return jsonify({
        "success": True,
        "is_in_wishlist": is_in_wishlist,
        "total_count": len(items),
        "message": msg
    })

@app.route("/api/coupon/apply", methods=["POST"])
def api_coupon_apply():
    data = request.get_json() or {}
    code = data.get("code", "").strip().upper()
    subtotal = float(data.get("subtotal", 0))
    
    valid_coupons = {
        "KKFIRST10": (10, "10% Welcome Discount applied! 🎉"),
        "KK10": (10, "10% Festive Discount applied! 🎉"),
        "ELEGANCE15": (15, "15% Special Discount applied! ✨")
    }
    
    if code in valid_coupons:
        pct, msg = valid_coupons[code]
        discount = round(subtotal * (pct / 100))
        new_total = max(0, subtotal - discount)
        return jsonify({
            "success": True,
            "discount": discount,
            "new_total": new_total,
            "message": msg
        })
    else:
        return jsonify({
            "success": False,
            "message": "Invalid or expired coupon code. Try KKFIRST10!"
        }), 400

@app.route("/api/reviews/add", methods=["POST"])
def api_review_add():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    customer_name = data.get("customer_name", "").strip() or session.get("user_name", "Customer")
    rating = int(data.get("rating", 5))
    comment = data.get("comment", "").strip()
    
    if not (product_id and comment):
        return jsonify({"success": False, "error": "Comment is required"}), 400
        
    user_id = session.get("user_id")
    db.add_review(product_id, user_id, customer_name, rating, comment)
    
    return jsonify({"success": True, "message": "Thank you for your valuable review! 💕"})

# --- Admin Portal Routes ---
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))
        
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        conn = db.get_db()
        admin = conn.execute("SELECT * FROM ADMIN WHERE email = ?", (email,)).fetchone()
        conn.close()
        
        if admin and check_password_hash(admin["password_hash"], password):
            session["admin_logged_in"] = True
            session["admin_id"] = admin["admin_id"]
            session["admin_name"] = admin["name"]
            flash(f"Welcome to KK_COLLECTIONS Management Portal, {admin['name']}!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid administrator credentials.", "danger")
            
    return render_template("admin/login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_id", None)
    session.pop("admin_name", None)
    flash("You have been signed out from the admin portal.", "info")
    return redirect(url_for("admin_login"))

@app.route("/admin")
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    metrics = db.get_dashboard_metrics()
    return render_template("admin/dashboard.html", metrics=metrics)

@app.route("/admin/products")
@admin_required
def admin_products():
    products = db.get_all_products(limit=200)
    categories = db.get_categories()
    return render_template("admin/products.html", products=products, categories=categories)

@app.route("/admin/products/add", methods=["POST"])
@admin_required
def admin_product_add():
    name = request.form.get("product_name", "").strip()
    category_id = int(request.form.get("category_id"))
    price = float(request.form.get("price", 0))
    discount = float(request.form.get("discount", 0))
    description = request.form.get("description", "").strip()
    material = request.form.get("material", "").strip()
    occasion = request.form.get("occasion", "").strip()
    stock = int(request.form.get("stock", 20))
    image = request.form.get("image", "bangles_thread_pink.jpg").strip()
    
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO PRODUCTS (product_name, category_id, description, price, discount, material, occasion, image, stock)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, category_id, description, price, discount, material, occasion, image, stock))
    conn.commit()
    conn.close()
    
    flash(f"Product '{name}' added successfully!", "success")
    return redirect(url_for("admin_products"))

@app.route("/admin/products/edit/<int:product_id>", methods=["POST"])
@admin_required
def admin_product_edit(product_id):
    name = request.form.get("product_name", "").strip()
    category_id = int(request.form.get("category_id"))
    price = float(request.form.get("price", 0))
    discount = float(request.form.get("discount", 0))
    description = request.form.get("description", "").strip()
    material = request.form.get("material", "").strip()
    occasion = request.form.get("occasion", "").strip()
    stock = int(request.form.get("stock", 20))
    
    conn = db.get_db()
    conn.execute('''
    UPDATE PRODUCTS SET product_name = ?, category_id = ?, description = ?,
           price = ?, discount = ?, material = ?, occasion = ?, stock = ?
    WHERE product_id = ?
    ''', (name, category_id, description, price, discount, material, occasion, stock, product_id))
    conn.commit()
    conn.close()
    
    flash("Product details updated successfully!", "success")
    return redirect(url_for("admin_products"))

@app.route("/admin/products/delete/<int:product_id>", methods=["POST"])
@admin_required
def admin_product_delete(product_id):
    conn = db.get_db()
    conn.execute("DELETE FROM PRODUCTS WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()
    flash("Product deleted successfully.", "info")
    return redirect(url_for("admin_products"))

@app.route("/admin/inventory")
@admin_required
def admin_inventory():
    conn = db.get_db()
    variants = conn.execute('''
    SELECT pv.*, p.product_name, p.price, p.image, c.name as category_name
    FROM PRODUCT_VARIANTS pv
    JOIN PRODUCTS p ON pv.product_id = p.product_id
    JOIN CATEGORIES c ON p.category_id = c.category_id
    ORDER BY pv.stock ASC, p.product_name ASC
    ''').fetchall()
    conn.close()
    return render_template("admin/inventory.html", inventory=[dict(v) for v in variants])

@app.route("/admin/inventory/update", methods=["POST"])
@admin_required
def admin_inventory_update():
    variant_id = request.form.get("variant_id")
    stock = int(request.form.get("stock", 0))
    
    conn = db.get_db()
    conn.execute("UPDATE PRODUCT_VARIANTS SET stock = ? WHERE variant_id = ?", (stock, variant_id))
    conn.commit()
    conn.close()
    
    flash("Stock quantity updated.", "success")
    return redirect(url_for("admin_inventory"))

@app.route("/admin/orders")
@admin_required
def admin_orders():
    status_filter = request.args.get("status", "All")
    orders = db.get_all_orders(status=status_filter)
    return render_template("admin/orders.html", orders=orders, current_status=status_filter)

@app.route("/admin/orders/status/<int:order_id>", methods=["POST"])
@admin_required
def admin_order_status_update(order_id):
    new_status = request.form.get("order_status")
    db.update_order_status(order_id, new_status)
    flash(f"Order #{order_id} status updated to {new_status}!", "success")
    return redirect(url_for("admin_orders"))

@app.route("/admin/customers")
@admin_required
def admin_customers():
    conn = db.get_db()
    customers_rows = conn.execute('''
    SELECT u.*, 
           COUNT(o.order_id) as total_orders,
           COALESCE(SUM(o.total_amount), 0) as total_spent,
           MAX(o.created_at) as last_order_date
    FROM USERS u
    LEFT JOIN ORDERS o ON u.user_id = o.user_id
    WHERE u.role = 'customer'
    GROUP BY u.user_id
    ORDER BY total_spent DESC
    ''').fetchall()
    conn.close()
    return render_template("admin/customers.html", customers=[dict(c) for c in customers_rows])

@app.route("/admin/analytics")
@admin_required
def admin_analytics():
    metrics = db.get_dashboard_metrics()
    conn = db.get_db()
    
    # Monthly sales trends
    monthly_rows = conn.execute('''
    SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as orders_count, SUM(total_amount) as revenue
    FROM ORDERS
    WHERE order_status != 'Cancelled'
    GROUP BY month
    ORDER BY month DESC
    LIMIT 6
    ''').fetchall()
    
    # Average Order Value
    avg_order_val = conn.execute('''
    SELECT COALESCE(AVG(total_amount), 0) FROM ORDERS WHERE order_status != 'Cancelled'
    ''').fetchone()[0]
    
    conn.close()
    return render_template(
        "admin/analytics.html",
        metrics=metrics,
        monthly_sales=[dict(m) for m in monthly_rows],
        avg_order_value=round(avg_order_val, 2)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    try:
        from waitress import serve
        print(f"Starting server on http://localhost:{port} (or http://127.0.0.1:{port})")
        serve(app, host="0.0.0.0", port=port)
    except ImportError:
        app.run(debug=False, use_reloader=False, host="0.0.0.0", port=port)
