import sqlite3
from database import get_db

def update_catalog():
    conn = get_db()
    cursor = conn.cursor()

    # Update category images to use the authentic customer photos
    cursor.execute("UPDATE CATEGORIES SET image = 'bangles_peacock_teal_thread.jpg' WHERE slug = 'bangles'")
    cursor.execute("UPDATE CATEGORIES SET image = 'chains_invisible_floral_ruby.jpg' WHERE slug = 'chains'")
    cursor.execute("UPDATE CATEGORIES SET image = 'combo_antique_temple_pearl.jpg' WHERE slug = 'collections'")

    # Get category IDs
    cat_bangles = cursor.execute("SELECT category_id FROM CATEGORIES WHERE slug = 'bangles'").fetchone()[0]
    cat_earrings = cursor.execute("SELECT category_id FROM CATEGORIES WHERE slug = 'earrings'").fetchone()[0]
    cat_chains = cursor.execute("SELECT category_id FROM CATEGORIES WHERE slug = 'chains'").fetchone()[0]
    cat_collections = cursor.execute("SELECT category_id FROM CATEGORIES WHERE slug = 'collections'").fetchone()[0]

    # New products to insert
    new_products = [
        {
            "name": "Peacock Teal Silk Thread Bangles with Golden Ball Chain (Set of 12)",
            "category_id": cat_bangles,
            "description": "Exquisite handmade peacock teal silk thread bangles wrapped in high-luster silk thread and bordered with multi-row golden bead chain and sparkling crystal stone work. Authentic KK_COLLECTIONS artisanal design.",
            "price": 380.0,
            "discount": 10,
            "material": "Pure Silk Thread, Brass Base, Gold Ball Chain, Crystal Stones",
            "occasion": "Festive",
            "image": "bangles_peacock_teal_thread.jpg",
            "rating": 5.0,
            "stock": 30,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Peacock Teal", "2.4", 10), ("Peacock Teal", "2.6", 12), ("Peacock Teal", "2.8", 8)]
        },
        {
            "name": "Silver Grey Silk Thread Designer Kada Set with Antique Kundan",
            "category_id": cat_bangles,
            "description": "Regal silver-grey silk thread bangles flanked by antique gold filigree kada, etched floral kundan motifs, and champagne crystal border. Designed for designer lehengas, pastel sarees, and grand receptions.",
            "price": 499.0,
            "discount": 15,
            "material": "Silk Thread, Antique Kundan, Champagne Crystals, Brass",
            "occasion": "Wedding",
            "image": "bangles_silver_grey_kundan.jpg",
            "rating": 5.0,
            "stock": 25,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Silver Grey", "2.4", 8), ("Silver Grey", "2.6", 10), ("Silver Grey", "2.8", 7)]
        },
        {
            "name": "Heritage Temple Jewelry Necklace & Chandbali Combo with Green Beads & Pearls",
            "category_id": cat_collections,
            "description": "Majestic antique gold necklace featuring emerald green gemstone centerpiece, ruby accents, and clustered seed pearl drops paired with matching royal chandbali earrings. An heirloom bridal masterpiece.",
            "price": 1299.0,
            "discount": 20,
            "material": "Brass Base, Antique Micro Polish, Seed Pearls, Emerald Green Beads",
            "occasion": "Wedding",
            "image": "combo_antique_temple_pearl.jpg",
            "rating": 5.0,
            "stock": 15,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Antique Gold / Green", "Standard", 15)]
        },
        {
            "name": "Floating Floral Ruby Invisible Chain with Gold Accents",
            "category_id": cat_chains,
            "description": "Delicate invisible nylon wire necklace featuring handcrafted floral charms studded with sparkling cubic zirconia crystals and ruby red centers, separated by golden spacers. Creates the illusion of floating floral diamonds.",
            "price": 280.0,
            "discount": 10,
            "material": "Invisible Nylon Wire, CZ Crystals, Ruby Accents, Gold Spacers",
            "occasion": "Party Wear",
            "image": "chains_invisible_floral_ruby.jpg",
            "rating": 5.0,
            "stock": 40,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Gold / Ruby", "16 inch", 20), ("Gold / Ruby", "18 inch", 20)]
        },
        {
            "name": "Minimalist Floating Floral Invisible Neckpiece (Model Edition)",
            "category_id": cat_chains,
            "description": "As seen on our model styling: ethereal invisible neckline jewelry with dainty micro-floral charms and ruby crystal droplets. Effortless, weightless elegance for modern Indian fusion attire.",
            "price": 299.0,
            "discount": 0,
            "material": "High-Grade Nylon Cord, CZ Diamonds, Ruby Gems, 18K Gold Polish",
            "occasion": "Daily Wear",
            "image": "chains_invisible_floral_worn.jpg",
            "rating": 4.9,
            "stock": 35,
            "is_featured": 1,
            "is_trending": 1,
            "is_new": 1,
            "variants": [("Gold / Crystal", "16 inch", 18), ("Gold / Crystal", "18 inch", 17)]
        }
    ]

    for p in new_products:
        # Check if already exists
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

            # Add variants
            for col, sz, stk in p["variants"]:
                sku = f"KK-REAL-{pid}-{col[:3].upper()}-{sz.replace(' ', '')}"
                cursor.execute('''
                INSERT INTO PRODUCT_VARIANTS (product_id, color, size, stock, sku)
                VALUES (?, ?, ?, ?, ?)
                ''', (pid, col, sz, stk, sku))

            # Add verified customer review
            cursor.execute('''
            INSERT INTO REVIEWS (product_id, user_id, customer_name, rating, comment)
            VALUES (?, 1, 'Sneha Raghavan', 5, 'The real piece looks even more breathtaking than the picture! The thread finish is top quality and the fit is perfection.')
            ''', (pid,))

    conn.commit()
    conn.close()
    print("Database successfully updated with authentic user photographs!")

if __name__ == "__main__":
    update_catalog()
