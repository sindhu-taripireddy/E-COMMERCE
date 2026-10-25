import sqlite3
from database import get_db

def add_new_bangles():
    conn = get_db()
    cursor = conn.cursor()

    cat_bangles = cursor.execute("SELECT category_id FROM CATEGORIES WHERE slug = 'bangles'").fetchone()[0]

    bangle_items = [
        {
            "name": "Royal Magenta Purple Dual-Band Silk Thread Kada with Kundan Bloom",
            "category_id": cat_bangles,
            "description": "Exquisite jamun-magenta silk thread split dual-band kada crowned with an ornate multi-petal floral kundan centerpiece and antique golden lace border. An artisanal showstopper for reception and festive styling.",
            "price": 449.0,
            "discount": 10,
            "material": "Pure Silk Thread, Antique Brass Frame, Floral Kundan Stones",
            "occasion": "Party Wear",
            "image": "bangles_purple_floral_kundan.jpg",
            "rating": 5.0,
            "stock": 28,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Magenta / Purple", "2.4", 8), ("Magenta / Purple", "2.6", 12), ("Magenta / Purple", "2.8", 8)]
        },
        {
            "name": "Rani Pink Silk Thread Bangles with Pinwheel Kundan Motifs",
            "category_id": cat_bangles,
            "description": "Bright festive rani pink hand-wound silk thread bangles studded with spinning pinwheel floral kundan stones and delicate golden crystal rivets. High-sheen silk finish for energetic celebration.",
            "price": 320.0,
            "discount": 15,
            "material": "Silk Thread, Brass Base, Micro-Kundan Charms",
            "occasion": "Festive",
            "image": "bangles_rani_pink_pinwheel.jpg",
            "rating": 4.9,
            "stock": 35,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Rani Pink", "2.4", 12), ("Rani Pink", "2.6", 15), ("Rani Pink", "2.8", 8)]
        },
        {
            "name": "Deep Maroon Silk Thread Bangles with Dipped Leaf Kundan Chain",
            "category_id": cat_bangles,
            "description": "Opulent bridal maroon silk thread bangles encircled with diagonally swept stone chains and delicate 3-leaf marquis kundan clusters. Designed for bridal sarees and traditional occasions.",
            "price": 360.0,
            "discount": 10,
            "material": "Rich Velvet-Silk Thread, Brass Core, Marquis Kundan, Stone Chain",
            "occasion": "Wedding",
            "image": "bangles_maroon_leaf_chain.jpg",
            "rating": 5.0,
            "stock": 30,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Maroon", "2.4", 10), ("Maroon", "2.6", 12), ("Maroon", "2.8", 8)]
        },
        {
            "name": "Crimson Red Silk Thread Bangles with Golden Kamal (Lotus) Motifs",
            "category_id": cat_bangles,
            "description": "Vibrant crimson red silk thread bangles adorned with traditional auspicious lotus (kamal) kundan motifs in embossed antique gold framing. Auspicious and timeless for pooja and weddings.",
            "price": 299.0,
            "discount": 0,
            "material": "Pure Silk Thread, Gold Plated Brass, Lotus Kundan Accents",
            "occasion": "Traditional",
            "image": "bangles_red_lotus_kundan.jpg",
            "rating": 4.9,
            "stock": 40,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Red", "2.4", 12), ("Red", "2.6", 18), ("Red", "2.8", 10)]
        },
        {
            "name": "Midnight Black Silk Thread Kada with Cluster Kundan & Leaf Work",
            "category_id": cat_bangles,
            "description": "Sophisticated midnight black hand-crafted silk thread kada featuring elaborate floral kundan bouquets and layered leaf stonework. A modern, striking statement piece for contemporary ethnic attire.",
            "price": 420.0,
            "discount": 10,
            "material": "Black Silk Thread, Kundan Crystals, Gold Casing, Brass Kada",
            "occasion": "Party Wear",
            "image": "bangles_black_royal_kundan.jpg",
            "rating": 5.0,
            "stock": 25,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Black", "2.4", 8), ("Black", "2.6", 10), ("Black", "2.8", 7)]
        }
    ]

    for p in bangle_items:
        exists = cursor.execute("SELECT product_id FROM PRODUCTS WHERE product_name = ?", (p["name"],)).fetchone()
        if exists:
            pid = exists[0]
            cursor.execute('''
            UPDATE PRODUCTS SET 
                category_id = ?, description = ?, price = ?, discount = ?,
                material = ?, occasion = ?, image = ?, rating = ?, stock = ?,
                is_featured = 1, is_trending = 1, is_new = 1
            WHERE product_id = ?
            ''', (p["category_id"], p["description"], p["price"], p["discount"],
                  p["material"], p["occasion"], p["image"], p["rating"], p["stock"], pid))
        else:
            cursor.execute('''
            INSERT INTO PRODUCTS (
                product_name, category_id, description, price, discount,
                material, occasion, image, rating, stock,
                is_featured, is_trending, is_new
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (p["name"], p["category_id"], p["description"], p["price"], p["discount"],
                  p["material"], p["occasion"], p["image"], p["rating"], p["stock"],
                  p["is_featured"], p["is_trending"], p["is_new"]))
            pid = cursor.lastrowid

            for col, sz, stk in p["variants"]:
                sku = f"KK-BGL-{pid}-{col[:3].upper()}-{sz.replace(' ', '')}"
                cursor.execute('''
                INSERT INTO PRODUCT_VARIANTS (product_id, color, size, stock, sku)
                VALUES (?, ?, ?, ?, ?)
                ''', (pid, col, sz, stk, sku))

            cursor.execute('''
            INSERT INTO REVIEWS (product_id, user_id, customer_name, rating, comment)
            VALUES (?, 1, 'Meenakshi Sundaram', 5, 'Magnificent silk wrapping! The kundan detailing is firmly mounted and does not snag on saree fabric. Simply royal!')
            ''', (pid,))

    conn.commit()
    conn.close()
    print("Successfully added 5 new authentic silk thread bangles to database!")

if __name__ == "__main__":
    add_new_bangles()
