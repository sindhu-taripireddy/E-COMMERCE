import sqlite3
from werkzeug.security import generate_password_hash
from database import get_db, init_db

def seed_database():
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if database is already seeded
    existing = cursor.execute("SELECT COUNT(*) FROM PRODUCTS").fetchone()[0]
    if existing > 0:
        print("Database already populated. Skipping seed.")
        conn.close()
        return

    print("Seeding KK_COLLECTIONS database with authentic catalog & demo data...")

    # 1. ADMIN USER
    cursor.execute('''
    INSERT INTO ADMIN (email, password_hash, name, role)
    VALUES (?, ?, ?, ?)
    ''', (
        "admin@kkcollections.com",
        generate_password_hash("admin123"),
        "Kavitha K (Store Owner)",
        "superadmin"
    ))

    # 2. DEMO CUSTOMER
    cursor.execute('''
    INSERT INTO USERS (name, email, password_hash, phone, role)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        "Priya Sharma",
        "demo@kkcollections.com",
        generate_password_hash("customer123"),
        "+91 98765 12345",
        "customer"
    ))
    demo_user_id = cursor.lastrowid

    # Customer Address
    cursor.execute('''
    INSERT INTO ADDRESSES (user_id, name, phone, address, city, state, pincode, is_default)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        demo_user_id,
        "Priya Sharma",
        "+91 98765 12345",
        "Flat 402, Lotus Grandeur, 14th Main, Indiranagar",
        "Bengaluru",
        "Karnataka",
        "560038",
        1
    ))

    # 3. CATEGORIES
    categories_data = [
        ("Bangles", "bangles", "Handcrafted thread bangles, bridal chura, and designer temple sets", "bangles_peacock_teal_thread.jpg"),
        ("Earrings", "earrings", "Silk thread jhumkas, chandbalis, and statement designer studs", "earrings_thread_jhumka_pink.jpg"),
        ("Chains", "chains", "Minimalist invisible chains, floating pearls, and elegant pendants", "chains_invisible_floral_ruby.jpg"),
        ("Collections", "collections", "Curated bridal, festive, and matching combo sets", "combo_antique_temple_pearl.jpg")
    ]
    
    category_map = {}
    for name, slug, desc, img in categories_data:
        cursor.execute("INSERT INTO CATEGORIES (name, slug, description, image) VALUES (?, ?, ?, ?)",
                       (name, slug, desc, img))
        category_map[slug] = cursor.lastrowid

    # 4. PRODUCTS & VARIANTS
    # (name, cat_slug, desc, price, discount, material, occasion, image, rating, stock, featured, trending, new, variants)
    # variants: list of (color, size, stock)
    catalog = [
        # AUTHENTIC PRODUCTS FROM INSTAGRAM REFERENCE
        (
            "Peacock Teal Silk Thread Bangles with Golden Ball Chain (Set of 12)",
            "bangles",
            "Exquisite handmade peacock teal silk thread bangles wrapped in high-luster silk thread and bordered with multi-row golden bead chain and sparkling crystal stone work. Authentic KK_COLLECTIONS artisanal design.",
            380.0, 10, "Pure Silk Thread, Brass Base, Gold Ball Chain, Crystal Stones", "Festive", "bangles_peacock_teal_thread.jpg", 5.0, 30, 1, 1, 1,
            [("Peacock Teal", "2.4", 10), ("Peacock Teal", "2.6", 12), ("Peacock Teal", "2.8", 8)]
        ),
        (
            "Silver Grey Silk Thread Designer Kada Set with Antique Kundan",
            "bangles",
            "Regal silver-grey silk thread bangles flanked by antique gold filigree kada, etched floral kundan motifs, and champagne crystal border. Designed for designer lehengas, pastel sarees, and grand receptions.",
            499.0, 15, "Silk Thread, Antique Kundan, Champagne Crystals, Brass", "Wedding", "bangles_silver_grey_kundan.jpg", 5.0, 25, 1, 1, 1,
            [("Silver Grey", "2.4", 8), ("Silver Grey", "2.6", 10), ("Silver Grey", "2.8", 7)]
        ),
        (
            "Heritage Temple Jewelry Necklace & Chandbali Combo with Green Beads & Pearls",
            "collections",
            "Majestic antique gold necklace featuring emerald green gemstone centerpiece, ruby accents, and clustered seed pearl drops paired with matching royal chandbali earrings. An heirloom bridal masterpiece.",
            1299.0, 20, "Brass Base, Antique Micro Polish, Seed Pearls, Emerald Green Beads", "Wedding", "combo_antique_temple_pearl.jpg", 5.0, 15, 1, 1, 1,
            [("Antique Gold / Green", "Standard", 15)]
        ),
        (
            "Floating Floral Ruby Invisible Chain with Gold Accents",
            "chains",
            "Delicate invisible nylon wire necklace featuring handcrafted floral charms studded with sparkling cubic zirconia crystals and ruby red centers, separated by golden spacers. Creates the illusion of floating floral diamonds.",
            280.0, 10, "Invisible Nylon Wire, CZ Crystals, Ruby Accents, Gold Spacers", "Party Wear", "chains_invisible_floral_ruby.jpg", 5.0, 40, 1, 1, 1,
            [("Gold / Ruby", "16 inch", 20), ("Gold / Ruby", "18 inch", 20)]
        ),
        (
            "Minimalist Floating Floral Invisible Neckpiece (Model Edition)",
            "chains",
            "As seen on our model styling: ethereal invisible neckline jewelry with dainty micro-floral charms and ruby crystal droplets. Effortless, weightless elegance for modern Indian fusion attire.",
            299.0, 0, "High-Grade Nylon Cord, CZ Diamonds, Ruby Gems, 18K Gold Polish", "Daily Wear", "chains_invisible_floral_worn.jpg", 4.9, 35, 1, 1, 1,
            [("Gold / Crystal", "16 inch", 18), ("Gold / Crystal", "18 inch", 17)]
        ),

        # ADDITIONAL AUTHENTIC HANDCRAFTED BANGLES
        (
            "Royal Magenta Purple Dual-Band Silk Thread Kada with Kundan Bloom",
            "bangles",
            "Exquisite jamun-magenta silk thread split dual-band kada crowned with an ornate multi-petal floral kundan centerpiece and antique golden lace border. An artisanal showstopper for reception and festive styling.",
            449.0, 10, "Pure Silk Thread, Antique Brass Frame, Floral Kundan Stones", "Party Wear", "bangles_purple_floral_kundan.jpg", 5.0, 28, 1, 1, 1,
            [("Magenta / Purple", "2.4", 8), ("Magenta / Purple", "2.6", 12), ("Magenta / Purple", "2.8", 8)]
        ),
        (
            "Rani Pink Silk Thread Bangles with Pinwheel Kundan Motifs",
            "bangles",
            "Bright festive rani pink hand-wound silk thread bangles studded with spinning pinwheel floral kundan stones and delicate golden crystal rivets. High-sheen silk finish for energetic celebration.",
            320.0, 15, "Silk Thread, Brass Base, Micro-Kundan Charms", "Festive", "bangles_rani_pink_pinwheel.jpg", 4.9, 35, 1, 1, 1,
            [("Rani Pink", "2.4", 12), ("Rani Pink", "2.6", 15), ("Rani Pink", "2.8", 8)]
        ),
        (
            "Deep Maroon Silk Thread Bangles with Dipped Leaf Kundan Chain",
            "bangles",
            "Opulent bridal maroon silk thread bangles encircled with diagonally swept stone chains and delicate 3-leaf marquis kundan clusters. Designed for bridal sarees and traditional occasions.",
            360.0, 10, "Rich Velvet-Silk Thread, Brass Core, Marquis Kundan, Stone Chain", "Wedding", "bangles_maroon_leaf_chain.jpg", 5.0, 30, 1, 1, 1,
            [("Maroon", "2.4", 10), ("Maroon", "2.6", 12), ("Maroon", "2.8", 8)]
        ),
        (
            "Crimson Red Silk Thread Bangles with Golden Kamal (Lotus) Motifs",
            "bangles",
            "Vibrant crimson red silk thread bangles adorned with traditional auspicious lotus (kamal) kundan motifs in embossed antique gold framing. Auspicious and timeless for pooja and weddings.",
            299.0, 0, "Pure Silk Thread, Gold Plated Brass, Lotus Kundan Accents", "Traditional", "bangles_red_lotus_kundan.jpg", 4.9, 40, 1, 1, 1,
            [("Red", "2.4", 12), ("Red", "2.6", 18), ("Red", "2.8", 10)]
        ),
        (
            "Midnight Black Silk Thread Kada with Cluster Kundan & Leaf Work",
            "bangles",
            "Sophisticated midnight black hand-crafted silk thread kada featuring elaborate floral kundan bouquets and layered leaf stonework. A modern, striking statement piece for contemporary ethnic attire.",
            420.0, 10, "Black Silk Thread, Kundan Crystals, Gold Casing, Brass Kada", "Party Wear", "bangles_black_royal_kundan.jpg", 5.0, 25, 1, 1, 1,
            [("Black", "2.4", 8), ("Black", "2.6", 10), ("Black", "2.8", 7)]
        ),

        # BANGLES
        (
            "Classic Silk Thread Bangles Set (Set of 8)",
            "bangles",
            "Exquisite handcrafted silk thread bangles wrapped with high-luster thread and detailed with delicate metallic golden accents. Comfortable for festive wear and daily elegance.",
            299.0, 15, "Silk Thread, Brass Base", "Festive", "bangles_thread_red.jpg", 4.9, 35, 1, 1, 0,
            [("Red", "2.4", 10), ("Red", "2.6", 15), ("Red", "2.8", 10),
             ("Maroon", "2.4", 8), ("Maroon", "2.6", 12), ("Maroon", "2.8", 6)]
        ),
        (
            "Rani Pink Festive Thread Bangles",
            "bangles",
            "Vibrant rani pink silk thread bangles adorned with sparkling micro-kundan stones and pearl bead border. Perfect match for pink sarees, lehengas, and anarkalis.",
            349.0, 10, "Silk Thread, Kundan Beads", "Party Wear", "bangles_thread_pink.jpg", 4.8, 25, 1, 1, 1,
            [("Pink", "2.4", 8), ("Pink", "2.6", 12), ("Pink", "2.8", 5)]
        ),
        (
            "Emerald Green Silk Thread Bangles",
            "bangles",
            "Rich emerald green hand-wound bangles with fine gold zari thread spirals. Enhances traditional silk sarees and festive celebrations.",
            280.0, 0, "Pure Silk Thread, Gold Zari", "Traditional", "bangles_thread_green.jpg", 4.7, 30, 0, 0, 1,
            [("Green", "2.4", 10), ("Green", "2.6", 12), ("Green", "2.8", 8)]
        ),
        (
            "Royal Blue Kundan Thread Bangles",
            "bangles",
            "Majestic royal blue velvet-silk bangles studded with floral kundan motifs. An opulent choice for sangeet nights and reception parties.",
            399.0, 20, "Silk Thread, Kundan Stones", "Wedding", "bangles_thread_blue.jpg", 4.9, 18, 1, 1, 0,
            [("Royal Blue", "2.4", 6), ("Royal Blue", "2.6", 8), ("Royal Blue", "2.8", 4)]
        ),
        (
            "Golden Velvet Thread Bangles",
            "bangles",
            "Versatile matte gold thread bangles wrapped tightly over a durable brass core. Blends effortlessly with any ethnic outfit.",
            249.0, 0, "Velvet Silk Thread", "Daily Wear", "bangles_thread_gold.jpg", 4.6, 40, 0, 0, 0,
            [("Gold", "2.4", 12), ("Gold", "2.6", 18), ("Gold", "2.8", 10)]
        ),
        (
            "Designer Kundan Chura Set",
            "bangles",
            "Grand traditional chura set featuring authentic kundan centerpieces, carved kada bangles, and pearl borders. Made for weddings and milestone occasions.",
            899.0, 15, "Brass, Kundan, Glass Pearls", "Wedding", "bangles_designer_kundan.jpg", 5.0, 12, 1, 1, 1,
            [("Red", "2.4", 4), ("Red", "2.6", 5), ("Red", "2.8", 3),
             ("Maroon", "2.4", 3), ("Maroon", "2.6", 4), ("Maroon", "2.8", 2)]
        ),
        (
            "Traditional Antique Gold Bangles (Set of 4)",
            "bangles",
            "Heritage temple jewelry finish carved with delicate floral filigree motifs. Matte antique micro-plating that does not tarnish easily.",
            499.0, 10, "Copper Alloy, Antique Gold Plated", "Traditional", "bangles_traditional_matte.jpg", 4.8, 22, 0, 1, 0,
            [("Antique Gold", "2.4", 6), ("Antique Gold", "2.6", 10), ("Antique Gold", "2.8", 6)]
        ),
        (
            "Royal Bridal Chura with Latkan",
            "bangles",
            "Spectacular bridal wedding chura set with velvet-red thread base, intricate crystal kundan work, and dangling pearl latkans.",
            1299.0, 20, "Velvet Thread, Kundan, Pearl Drops", "Wedding", "bangles_bridal_heavy.jpg", 5.0, 8, 1, 1, 1,
            [("Red", "2.4", 3), ("Red", "2.6", 3), ("Red", "2.8", 2)]
        ),

        # EARRINGS
        (
            "Pink Silk Thread Jhumkas with Pearl Drops",
            "earrings",
            "Lightweight handmade silk thread dome jhumkas decorated with seed pearls and crystal stones. Extremely comfortable for all-day wear without ear lobe pull.",
            220.0, 0, "Silk Thread, Brass Base, Seed Pearls", "Festive", "earrings_thread_jhumka_pink.jpg", 4.9, 45, 1, 1, 0,
            [("Pink", "Standard", 45)]
        ),
        (
            "Emerald Green Thread Jhumkas",
            "earrings",
            "Stunning deep green thread jhumkas with gold filigree cap and hanging pearl beads. Pairs gorgeously with green sarees, lehengas, or contrasting mustard yellow.",
            240.0, 0, "Silk Thread, Gold Zari, Pearls", "Festive", "earrings_thread_jhumka_green.jpg", 4.8, 30, 0, 1, 0,
            [("Green", "Standard", 30)]
        ),
        (
            "Traditional Antique Temple Jhumkas",
            "earrings",
            "Majestic antique gold jhumkas featuring Goddess Lakshmi motif and dangling ghungroos. High quality heritage polish.",
            380.0, 15, "Brass, Antique Micro Polish", "Traditional", "earrings_traditional_temple.jpg", 4.9, 24, 1, 1, 0,
            [("Antique Gold", "Standard", 24)]
        ),
        (
            "Designer Crystal Drop Earrings",
            "earrings",
            "Contemporary party-wear drop earrings encrusted with faceted cubic zirconia crystals in a shimmering rose-gold plating.",
            320.0, 10, "Cubic Zirconia, Rose Gold Plating", "Party Wear", "earrings_designer_cz.jpg", 4.7, 28, 0, 0, 1,
            [("Silver", "Standard", 15), ("Rose Gold", "Standard", 13)]
        ),
        (
            "Royal Bridal Chandbali Earrings",
            "earrings",
            "Opulent crescent-shaped bridal chandbalis with layered kundan stones, green meenakari enameling, and clustered pearl drops.",
            550.0, 18, "Kundan, Meenakari, Faux Pearls", "Wedding", "earrings_bridal_chandbali.jpg", 5.0, 14, 1, 1, 1,
            [("Gold / Pearl", "Standard", 8), ("Red / Gold", "Standard", 6)]
        ),
        (
            "Haldi Floral Thread Studs",
            "earrings",
            "Cheerful yellow silk thread floral studs with crystal center. Designed specially for Haldi, Mehendi, and casual day events.",
            180.0, 0, "Silk Thread, Crystal Stud", "Haldi", "earrings_thread_studs_yellow.jpg", 4.7, 50, 0, 1, 1,
            [("Yellow", "Standard", 50)]
        ),

        # CHAINS
        (
            "Ruby & Emerald Floral Invisible Chain with Matching Studs (Set of 2)",
            "chains",
            "Handcrafted invisible neck chain featuring traditional South Indian floral motifs with ruby-pink petals and emerald green centers, accompanied by matching floral stud earrings. Lightweight, festive, and timeless.",
            349.0, 15, "Invisible Wire, Ruby Kempu Stones, Emerald Centers, Gold Plated Brass", "Festive", "chains_ruby_emerald_floral_set.jpg", 5.0, 35, 1, 1, 1,
            [("Ruby / Green", "16 inch", 20), ("Ruby / Green", "18 inch", 15)]
        ),
        (
            "5-Point Starburst CZ Diamond Invisible Chain with Drop Earrings",
            "chains",
            "Glistening floating invisible chain adorned with five multi-faceted cubic zirconia starburst floral pendants and paired with lightweight matching drop hook earrings. Creates a sparkling constellation effect on the neckline.",
            380.0, 10, "Nylon Invisible Cord, AAA Cubic Zirconia, Gold Plated Ear Hooks", "Party Wear", "chains_starburst_diamond_set.jpg", 4.9, 40, 1, 1, 1,
            [("Gold / Crystal", "16 inch", 20), ("Gold / Crystal", "18 inch", 20)]
        ),
        (
            "Minimalist 3-Pendant Starburst Invisible Collar Necklace",
            "chains",
            "Ultra-delicate invisible cord collar necklace featuring three sparkling crystal starburst medallions that rest gracefully along the collarbone. Perfect for western blouses, office wear, and deep-neck kurtis.",
            249.0, 0, "High-Tension Nylon Wire, Crystal Starburst Charms, 18K Gold Polish", "Daily Wear", "chains_starburst_mannequin.jpg", 4.8, 50, 1, 1, 1,
            [("Gold / Crystal", "16 inch", 25), ("Gold / Crystal", "18 inch", 25)]
        ),
        (
            "Floating Freshwater Pearl & Floral Crystal Invisible Chain",
            "chains",
            "Timeless invisible cord necklace alternating between lustrous faux freshwater pearls and radiant floral crystal blossoms. Subdued luxury for formal and celebratory evenings.",
            320.0, 10, "Invisible Cord, Faux Freshwater Pearls, CZ Crystals, Golden Spacers", "Party Wear", "chains_pearl_floral_black_silk.jpg", 5.0, 30, 1, 1, 1,
            [("Pearl White / Gold", "16 inch", 15), ("Pearl White / Gold", "18 inch", 15)]
        ),
        (
            "Royal Kundan Teardrop & Pearl Tassel Invisible Choker Necklace",
            "chains",
            "Regal invisible wire choker studded with teardrop polki kundan gemstones and cascading micro-pearl bunch tassels. Beautiful harmony of antique Indian opulence with modern weightless comfort.",
            449.0, 15, "Invisible Wire, Polki Kundan Drops, Clustered Seed Pearls, Gold Mountings", "Wedding", "chains_kundan_pearl_droplet_choker.jpg", 5.0, 25, 1, 1, 1,
            [("Antique Gold / Pearl", "16 inch", 15), ("Antique Gold / Pearl", "18 inch", 10)]
        ),
        (
            "Solitaire Invisible Crystal Chain",
            "chains",
            "Ultra-fine transparent nylon invisible cord holding a brilliant sparkling solitaire pendant. Creates the mesmerizing illusion of a gemstone floating on your collarbone.",
            199.0, 0, "Invisible Nylon Cord, High-Grade CZ Crystal", "Daily Wear", "chains_invisible_crystal.jpg", 4.9, 60, 1, 1, 0,
            [("Silver Crystal", "16 inch", 35), ("Silver Crystal", "18 inch", 25)]
        ),
        (
            "Floating Pearl Invisible Chain",
            "chains",
            "Subtle and timeless invisible nylon necklace with a lustrous teardrop faux freshwater pearl. Beautiful under western shirts or traditional blouses.",
            220.0, 10, "Invisible Cord, Faux Pearl", "Daily Wear", "chains_invisible_pearl.jpg", 4.8, 40, 0, 0, 1,
            [("Pearl White", "16 inch", 25), ("Pearl White", "18 inch", 15)]
        ),
        (
            "Rose Gold Teardrop Pendant Chain",
            "chains",
            "Delicate hypoallergenic stainless steel chain with a teardrop Austrian crystal framed in rose gold. Water-resistant and tarnish-free for daily wear.",
            349.0, 15, "Stainless Steel, Rose Gold PVD", "Party Wear", "chains_pendant_rosegold.jpg", 4.8, 30, 0, 1, 0,
            [("Rose Gold", "18 inch", 30)]
        ),
        (
            "Antique Gold Floral Pendant Chain",
            "chains",
            "Traditional floral medallion pendant strung on a textured golden link chain. Subtle, royal, and lightweight.",
            299.0, 0, "Brass, Antique Matte Gold", "Traditional", "chains_traditional_pendant.jpg", 4.6, 20, 0, 0, 0,
            [("Antique Gold", "18 inch", 20)]
        ),

        # COMBOS & COLLECTIONS
        (
            "Royal Bridal Complete Combo Set",
            "collections",
            "The ultimate wedding ensemble: Grand Kundan Bangle Set (Set of 6), Matching Bridal Chandbali Earrings, and a delicate Solitaire Invisible Chain. Handpicked harmony.",
            1499.0, 25, "Silk Thread, Kundan, Pearls, Invisible Cord", "Wedding", "combo_bridal_set.jpg", 5.0, 10, 1, 1, 1,
            [("Red / Gold", "2.4", 3), ("Red / Gold", "2.6", 4), ("Red / Gold", "2.8", 3)]
        ),
        (
            "Rani Pink Festive Matching Combo",
            "collections",
            "Charming 3-piece combo featuring Rani Pink silk thread bangles (Set of 4), matching pink thread jhumkas, and an invisible crystal neckpiece.",
            599.0, 15, "Silk Thread, Pearls, Invisible Cord", "Festive", "combo_festive_pink.jpg", 4.9, 16, 1, 1, 1,
            [("Pink", "2.4", 5), ("Pink", "2.6", 8), ("Pink", "2.8", 3)]
        ),
        (
            "Golden Haldi Special Set",
            "collections",
            "Specially curated for Haldi ceremonies: Bright yellow floral thread studs paired with golden velvet bangles. Radiant and festive.",
            399.0, 10, "Silk Thread, Velvet Core, Crystals", "Haldi", "combo_haldi_yellow.jpg", 4.8, 25, 0, 1, 0,
            [("Yellow / Gold", "2.4", 8), ("Yellow / Gold", "2.6", 12), ("Yellow / Gold", "2.8", 5)]
        )
    ]

    product_id_map = {}
    for item in catalog:
        name, cat_slug, desc, price, disc, mat, occ, img, rat, stk, feat, trend, isnew, variants = item
        cat_id = category_map[cat_slug]
        
        cursor.execute('''
        INSERT INTO PRODUCTS (
            product_name, category_id, description, price, discount,
            material, occasion, image, rating, stock,
            is_featured, is_trending, is_new
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, cat_id, desc, price, disc, mat, occ, img, rat, stk, feat, trend, isnew))
        
        pid = cursor.lastrowid
        product_id_map[name] = pid
        
        # Add variants
        for color, size, var_stock in variants:
            sku = f"KK-{cat_slug[:3].upper()}-{pid}-{color[:3].upper()}-{size.replace('.', '')}"
            cursor.execute('''
            INSERT INTO PRODUCT_VARIANTS (product_id, color, size, stock, sku)
            VALUES (?, ?, ?, ?, ?)
            ''', (pid, color, size, var_stock, sku))

    # 5. REVIEWS
    reviews_data = [
        ("Classic Silk Thread Bangles Set (Set of 8)", "Ananya Iyer", 5, "The finishing of these thread bangles is unbelievable! Perfectly smooth, no loose threads, and they look royal with my Kanjeevaram saree."),
        ("Classic Silk Thread Bangles Set (Set of 8)", "Meera Krishnan", 5, "Fast delivery to Chennai! Loved the packaging and the size 2.6 fits comfortably."),
        ("Rani Pink Festive Thread Bangles", "Priya Sharma", 5, "The rani pink color is so bright and festive. Got dozens of compliments at my friend's Sangeet!"),
        ("Pink Silk Thread Jhumkas with Pearl Drops", "Deepika Patel", 5, "So feather-light! Usually heavy earrings hurt my ears, but I wore these for 7 hours without any pain. Highly recommend!"),
        ("Solitaire Invisible Crystal Chain", "Sneha Reddy", 5, "I wear this invisible chain almost every single day to work. Subtle and elegant, exactly as pictured."),
        ("Royal Bridal Complete Combo Set", "Divya Nair", 5, "Ordered this for my wedding events. The combo saved me so much time trying to match pieces separately. Beautiful craftsmanship by KK_COLLECTIONS!"),
        ("Royal Blue Kundan Thread Bangles", "Ritu Agarwal", 4, "Rich royal blue color. Customer care on WhatsApp was very helpful with the size recommendation.")
    ]
    
    for prod_name, cust_name, rating, comment in reviews_data:
        if prod_name in product_id_map:
            cursor.execute('''
            INSERT INTO REVIEWS (product_id, user_id, customer_name, rating, comment)
            VALUES (?, ?, ?, ?, ?)
            ''', (product_id_map[prod_name], demo_user_id, cust_name, rating, comment))

    # 6. FAQS
    faqs_data = [
        ("Shipping", "What are the shipping charges and delivery timeframes?", 
         "We offer FREE shipping across India on all orders over ₹499. For orders below ₹499, a nominal delivery fee of ₹49 applies. Orders are typically processed within 24 hours and delivered in 3 to 5 business days."),
        
        ("Shipping", "How can I track my order?", 
         "You can easily track your order on our 'Order Tracking' page using your order tracking number (e.g., #KK20260918001), or simply ask our KK AI Assistant 'Where is my order?' anytime!"),
        
        ("Payment", "Is Cash on Delivery (COD) available?", 
         "Yes! Cash on Delivery is available across 26,000+ pincodes in India for orders up to ₹2,500. We also accept UPI (Google Pay, PhonePe, Paytm), Credit/Debit Cards, and Net Banking."),
        
        ("Returns", "What is your return and exchange policy?", 
         "We have a 7-day hassle-free exchange and return policy for unworn accessories in original packaging. If you received an incorrect size or damaged piece, simply contact us via WhatsApp or email care@kkcollections.com with your Order ID."),
        
        ("Sizing", "How do I choose the correct bangle size?", 
         "Standard Indian bangle sizing: Size 2.4 (Small, inner diameter 2.25 inches / 5.7 cm), Size 2.6 (Medium, inner diameter 2.375 inches / 6.0 cm), Size 2.8 (Large, inner diameter 2.5 inches / 6.4 cm). You can also measure the inside diameter of a bangle that fits you well."),
        
        ("Product Care", "How do I take care of silk thread and handmade accessories?", 
         "Keep your silk thread bangles and jhumkas away from direct contact with water, sprays, and alcohol-based perfumes. Always store each piece in the provided zip-lock pouch or velvet box in a cool, dry place."),
        
        ("Customization", "Do you offer custom matching colors for sarees and bridal lehengas?", 
         "Yes! KK_COLLECTIONS specializes in customized silk thread bangles and jewelry sets matched to your saree or dress swatches. Reach out via WhatsApp or ask KK AI Assistant for custom inquiries.")
    ]
    
    for cat, q, a in faqs_data:
        cursor.execute("INSERT INTO FAQ (category, question, answer) VALUES (?, ?, ?)", (cat, q, a))

    # 7. DEMO ORDERS
    # Demo Order 1: In Shipped status (order #KK20260918001 as referenced in prompt requirements)
    pid_bangles = product_id_map["Classic Silk Thread Bangles Set (Set of 8)"]
    pid_earrings = product_id_map["Pink Silk Thread Jhumkas with Pearl Drops"]
    
    cursor.execute('''
    INSERT INTO ORDERS (
        tracking_number, user_id, customer_name, email, phone,
        address, city, state, pincode, subtotal, delivery_fee,
        discount_amount, total_amount, payment_method, payment_status,
        order_status, notes, created_at
    ) VALUES (
        'KK20260918001', ?, 'Priya Sharma', 'demo@kkcollections.com', '+91 98765 12345',
        'Flat 402, Lotus Grandeur, 14th Main, Indiranagar', 'Bengaluru', 'Karnataka', '560038',
        519.0, 0.0, 50.0, 469.0, 'UPI', 'Completed', 'Shipped',
        'Gift wrap requested with festive note', datetime('now', '-2 days')
    )
    ''', (demo_user_id,))
    order1_id = cursor.lastrowid
    
    cursor.execute('''
    INSERT INTO ORDER_ITEMS (order_id, product_id, product_name, color, size, price, quantity, subtotal, image)
    VALUES (?, ?, 'Classic Silk Thread Bangles Set (Set of 8)', 'Red', '2.6', 254.0, 1, 254.0, 'bangles_thread_red.jpg')
    ''', (order1_id, pid_bangles))
    cursor.execute('''
    INSERT INTO ORDER_ITEMS (order_id, product_id, product_name, color, size, price, quantity, subtotal, image)
    VALUES (?, ?, 'Pink Silk Thread Jhumkas with Pearl Drops', 'Pink', 'Standard', 220.0, 1, 220.0, 'earrings_thread_jhumka_pink.jpg')
    ''', (order1_id, pid_earrings))
    
    cursor.execute('''
    INSERT INTO PAYMENTS (order_id, method, transaction_ref, amount, status)
    VALUES (?, 'UPI', 'TXN_KK20260918001', 469.0, 'Success')
    ''', (order1_id,))

    # Demo Order 2: Delivered status
    pid_chain = product_id_map["Solitaire Invisible Crystal Chain"]
    cursor.execute('''
    INSERT INTO ORDERS (
        tracking_number, user_id, customer_name, email, phone,
        address, city, state, pincode, subtotal, delivery_fee,
        discount_amount, total_amount, payment_method, payment_status,
        order_status, notes, created_at
    ) VALUES (
        'KK20260915002', ?, 'Ananya Iyer', 'ananya.iyer@example.com', '+91 98450 98765',
        '45, Green Glen Layout, Bellandur', 'Bengaluru', 'Karnataka', '560103',
        199.0, 49.0, 0.0, 248.0, 'Card', 'Completed', 'Delivered',
        'Delivered on time', datetime('now', '-5 days')
    )
    ''', (None,))
    order2_id = cursor.lastrowid
    
    cursor.execute('''
    INSERT INTO ORDER_ITEMS (order_id, product_id, product_name, color, size, price, quantity, subtotal, image)
    VALUES (?, ?, 'Solitaire Invisible Crystal Chain', 'Silver Crystal', '16 inch', 199.0, 1, 199.0, 'chains_invisible_crystal.jpg')
    ''', (order2_id, pid_chain))

    conn.commit()
    conn.close()
    print("KK_COLLECTIONS database initialized and seeded successfully!")

if __name__ == "__main__":
    seed_database()
