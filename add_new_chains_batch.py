import sqlite3
from database import get_db

def add_new_chains():
    conn = get_db()
    cursor = conn.cursor()

    cat_chains = cursor.execute("SELECT category_id FROM CATEGORIES WHERE slug = 'chains'").fetchone()[0]

    chain_items = [
        {
            "name": "Ruby & Emerald Floral Invisible Chain with Matching Studs (Set of 2)",
            "category_id": cat_chains,
            "description": "Handcrafted invisible neck chain featuring traditional South Indian floral motifs with ruby-pink petals and emerald green centers, accompanied by matching floral stud earrings. Lightweight, festive, and timeless.",
            "price": 349.0,
            "discount": 15,
            "material": "Invisible Wire, Ruby Kempu Stones, Emerald Centers, Gold Plated Brass",
            "occasion": "Festive",
            "image": "chains_ruby_emerald_floral_set.jpg",
            "rating": 5.0,
            "stock": 35,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Ruby / Green", "16 inch", 20), ("Ruby / Green", "18 inch", 15)]
        },
        {
            "name": "5-Point Starburst CZ Diamond Invisible Chain with Drop Earrings",
            "category_id": cat_chains,
            "description": "Glistening floating invisible chain adorned with five multi-faceted cubic zirconia starburst floral pendants and paired with lightweight matching drop hook earrings. Creates a sparkling constellation effect on the neckline.",
            "price": 380.0,
            "discount": 10,
            "material": "Nylon Invisible Cord, AAA Cubic Zirconia, Gold Plated Ear Hooks",
            "occasion": "Party Wear",
            "image": "chains_starburst_diamond_set.jpg",
            "rating": 4.9,
            "stock": 40,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Gold / Crystal", "16 inch", 20), ("Gold / Crystal", "18 inch", 20)]
        },
        {
            "name": "Minimalist 3-Pendant Starburst Invisible Collar Necklace",
            "category_id": cat_chains,
            "description": "Ultra-delicate invisible cord collar necklace featuring three sparkling crystal starburst medallions that rest gracefully along the collarbone. Perfect for western blouses, office wear, and deep-neck kurtis.",
            "price": 249.0,
            "discount": 0,
            "material": "High-Tension Nylon Wire, Crystal Starburst Charms, 18K Gold Polish",
            "occasion": "Daily Wear",
            "image": "chains_starburst_mannequin.jpg",
            "rating": 4.8,
            "stock": 50,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Gold / Crystal", "16 inch", 25), ("Gold / Crystal", "18 inch", 25)]
        },
        {
            "name": "Floating Freshwater Pearl & Floral Crystal Invisible Chain",
            "category_id": cat_chains,
            "description": "Timeless invisible cord necklace alternating between lustrous faux freshwater pearls and radiant floral crystal blossoms. Subdued luxury for formal and celebratory evenings.",
            "price": 320.0,
            "discount": 10,
            "material": "Invisible Cord, Faux Freshwater Pearls, CZ Crystals, Golden Spacers",
            "occasion": "Party Wear",
            "image": "chains_pearl_floral_black_silk.jpg",
            "rating": 5.0,
            "stock": 30,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Pearl White / Gold", "16 inch", 15), ("Pearl White / Gold", "18 inch", 15)]
        },
        {
            "name": "Royal Kundan Teardrop & Pearl Tassel Invisible Choker Necklace",
            "category_id": cat_chains,
            "description": "Regal invisible wire choker studded with teardrop polki kundan gemstones and cascading micro-pearl bunch tassels. Beautiful harmony of antique Indian opulence with modern weightless comfort.",
            "price": 449.0,
            "discount": 15,
            "material": "Invisible Wire, Polki Kundan Drops, Clustered Seed Pearls, Gold Mountings",
            "occasion": "Wedding",
            "image": "chains_kundan_pearl_droplet_choker.jpg",
            "rating": 5.0,
            "stock": 25,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Antique Gold / Pearl", "16 inch", 15), ("Antique Gold / Pearl", "18 inch", 10)]
        }
    ]

    for p in chain_items:
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
                sku = f"KK-CHN-{pid}-{col[:3].upper()}-{sz.replace(' ', '')}"
                cursor.execute('''
                INSERT INTO PRODUCT_VARIANTS (product_id, color, size, stock, sku)
                VALUES (?, ?, ?, ?, ?)
                ''', (pid, col, sz, stk, sku))

            cursor.execute('''
            INSERT INTO REVIEWS (product_id, user_id, customer_name, rating, comment)
            VALUES (?, 1, 'Kavya S.', 5, 'The invisible chain is genuinely weightless! Looks like the crystal flowers are floating on skin. Got so many compliments!')
            ''', (pid,))

    conn.commit()
    conn.close()
    print("Successfully added 5 new authentic invisible chains to database!")

if __name__ == "__main__":
    add_new_chains()
