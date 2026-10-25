import re
import json
import sqlite3
from typing import Dict, Any, List, Optional
from config import Config
from database import (
    get_db, get_all_products, get_product_by_id, get_order_by_tracking,
    get_user_orders, get_all_faqs, get_session_preferences, update_session_preferences
)

# Optional Gemini import using the supported google-genai SDK
try:
    from google import genai
    HAS_GEMINI = bool(Config.GEMINI_API_KEY)
    gemini_client = None
    if HAS_GEMINI:
        gemini_client = genai.Client(api_key=Config.GEMINI_API_KEY)
except Exception:
    HAS_GEMINI = False
    gemini_client = None

class KKAssistant:
    def __init__(self):
        self.color_matches = {
            "green": ["gold", "green", "pearl", "pink"],
            "pink": ["pink", "gold", "pearl", "royal blue"],
            "rani pink": ["pink", "gold", "pearl", "green"],
            "red": ["red", "gold", "maroon", "pearl", "green"],
            "maroon": ["maroon", "gold", "pearl", "antique gold"],
            "blue": ["royal blue", "gold", "silver", "pink"],
            "royal blue": ["royal blue", "gold", "silver", "pearl"],
            "yellow": ["yellow", "gold", "green", "pearl"],
            "haldi": ["yellow", "gold", "green"],
            "white": ["pearl", "gold", "crystal", "silver"],
            "black": ["gold", "silver", "crystal", "red"],
            "gold": ["gold", "pearl", "red", "green"],
            "peach": ["pearl", "rose gold", "gold"],
            "purple": ["gold", "pearl", "magenta", "silver"],
            "magenta": ["gold", "pearl", "green", "pink"],
            "teal": ["gold", "pearl", "teal", "pink"],
            "grey": ["antique gold", "silver", "kundan", "pearl"]
        }

    def process_message(self, message: str, session_id: str, user_id: Optional[int] = None, 
                        current_product_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Main entry point for processing customer messages.
        Returns:
            {
                'text': 'Response text',
                'products': [list of product dicts],
                'action_chips': [list of strings],
                'order_info': dict or None,
                'combo_info': dict or None
            }
        """
        clean_msg = message.strip().lower()
        preferences = get_session_preferences(session_id)
        
        # 1. Update preferences from current message
        self._extract_and_save_preferences(clean_msg, session_id, preferences)
        preferences = get_session_preferences(session_id)

        # 2. Contextual Query: Ask about current product (if on product detail page)
        if current_product_id and self._is_product_question(clean_msg):
            return self._handle_product_context_question(clean_msg, current_product_id)

        # 3. Order Tracking Intent
        order_match = re.search(r'kk\d{11}', clean_msg)
        if order_match or any(k in clean_msg for k in ["where is my order", "track order", "track my order", "order status", "my order"]):
            return self._handle_order_intent(clean_msg, order_match.group(0).upper() if order_match else None, user_id)

        # 4. Combo Set Request
        if any(k in clean_msg for k in ["combo", "matching set", "set of", "complete set", "pair with", "create a set"]):
            return self._handle_combo_recommendation(clean_msg, preferences)

        # 5. Outfit / Saree Color Matching Intent
        saree_color = self._extract_outfit_color(clean_msg)
        if saree_color and any(k in clean_msg for k in ["saree", "dress", "lehenga", "suit", "wearing", "matching", "match", "wear with"]):
            return self._handle_color_matching(saree_color)

        # 6. Budget-Based Shopping Intent
        budget = self._extract_budget(clean_msg)
        if budget:
            return self._handle_budget_search(clean_msg, budget, preferences)

        # 7. Occasion-Based Recommendation Intent
        occasion = self._extract_occasion(clean_msg)
        if occasion and any(k in clean_msg for k in ["wedding", "party", "haldi", "festive", "daily", "function", "reception"]):
            return self._handle_occasion_search(occasion, clean_msg, preferences)

        # 8. Category & Product Discovery Intent
        category_intent = self._extract_category(clean_msg)
        if category_intent:
            return self._handle_category_search(category_intent, clean_msg, preferences)

        # 9. FAQ & Policy Questions
        faq_response = self._handle_faq_query(clean_msg)
        if faq_response:
            return faq_response

        # 10. Greetings & Friendly Conversation
        if any(clean_msg.startswith(k) for k in ["hi", "hello", "hey", "namaste", "good morning", "good evening", "vanakkam"]):
            return {
                "text": "Hello! 👋 Welcome to KK_COLLECTIONS. Elegance That Completes You! 💕 I'm your AI shopping assistant. How can I assist you today? You can browse our handcrafted thread bangles, jhumkas, invisible chains, or ask for occasion recommendations!",
                "products": self._get_highlight_products(4),
                "action_chips": ["Shop Bangles", "Shop Earrings", "Under ₹300", "Wedding Collection", "Track My Order", "New Arrivals"]
            }

        if any(k in clean_msg for k in ["thank", "thanks", "helpful", "bye", "goodbye"]):
            return {
                "text": "You're most welcome! 💕 Happy shopping at KK_COLLECTIONS. If you need anything else, I'm always right here.",
                "products": [],
                "action_chips": ["Shop Bangles", "Shop Earrings", "Under ₹300", "Wedding Collection"]
            }

        # 11. Generic Search or Gemini LLM enhancement if key provided
        if HAS_GEMINI:
            try:
                gemini_res = self._ask_gemini(message, preferences)
                if gemini_res:
                    return gemini_res
            except Exception as e:
                print(f"Gemini error: {e}")

        # Fallback Search across catalog
        words = [w for w in re.findall(r'\b\w+\b', clean_msg) if len(w) > 2 and w not in ["show", "give", "want", "need", "looking", "please", "like"]]
        search_term = " ".join(words[:2]) if words else clean_msg
        results = get_all_products(search=search_term, limit=6)
        
        if results:
            return {
                "text": f"Here are the most suitable pieces from our KK_COLLECTIONS catalog for you 💕",
                "products": results,
                "action_chips": ["Shop Bangles", "Shop Earrings", "Under ₹300", "Wedding Collection"]
            }
        else:
            return {
                "text": "I couldn't find that specific item in our KK_COLLECTIONS catalog. 💕 Would you like to explore our handcrafted thread bangles, designer earrings, or invisible chains?",
                "products": self._get_highlight_products(3),
                "action_chips": ["Shop Bangles", "Shop Earrings", "Under ₹300", "View All Products"]
            }

    def _extract_and_save_preferences(self, text: str, session_id: str, current_prefs: dict):
        new_prefs = {}
        # Colors
        for c in ["pink", "red", "green", "blue", "gold", "maroon", "yellow", "royal blue"]:
            if re.search(r'\b' + c + r'\b', text):
                new_prefs["favorite_color"] = c
                break
        # Budget
        budget = self._extract_budget(text)
        if budget:
            new_prefs["budget"] = budget
        # Occasion
        occ = self._extract_occasion(text)
        if occ:
            new_prefs["occasion"] = occ
            
        if new_prefs:
            update_session_preferences(session_id, new_prefs)

    def _extract_budget(self, text: str) -> Optional[float]:
        # Matches: under 300, under rs 300, under ₹300, below 500, within 400, budget 500, 300 rupees
        patterns = [
            r'(?:under|below|less than|within|upto|budget)\s*(?:rs\.?|inr|₹)?\s*(\d+)',
            r'(?:rs\.?|inr|₹)?\s*(\d+)\s*(?:budget|rupees|rs)'
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return float(m.group(1))
        return None

    def _extract_occasion(self, text: str) -> Optional[str]:
        occasions = {
            "wedding": "Wedding",
            "bridal": "Wedding",
            "marriage": "Wedding",
            "sangeet": "Party Wear",
            "reception": "Wedding",
            "party": "Party Wear",
            "festive": "Festive",
            "festival": "Festive",
            "diwali": "Festive",
            "pooja": "Festive",
            "puja": "Festive",
            "haldi": "Haldi",
            "mehendi": "Festive",
            "daily": "Daily Wear",
            "casual": "Daily Wear",
            "office": "Daily Wear",
            "college": "Daily Wear"
        }
        for k, v in occasions.items():
            if re.search(r'\b' + k + r'\b', text):
                return v
        return None

    def _extract_outfit_color(self, text: str) -> Optional[str]:
        for c in self.color_matches.keys():
            if re.search(r'\b' + c + r'\b', text):
                return c
        return None

    def _extract_category(self, text: str) -> Optional[str]:
        if any(k in text for k in ["bangle", "bangles", "kada", "chura", "choora", "valayal"]):
            return "bangles"
        if any(k in text for k in ["earring", "earrings", "jhumka", "jhumkas", "jhumki", "stud", "studs", "chandbali", "chandbalis", "ear rings"]):
            return "earrings"
        if any(k in text for k in ["chain", "chains", "invisible chain", "necklace", "pendant", "choker"]):
            return "chains"
        if any(k in text for k in ["collection", "collections", "combo", "set", "sets", "bridal set"]):
            return "collections"
        return None

    def _handle_product_context_question(self, text: str, product_id: int) -> Dict[str, Any]:
        p = get_product_by_id(product_id)
        if not p:
            return {"text": "I couldn't locate details for this product. Please choose another item.", "products": []}
            
        p_name = p['product_name']
        price = p['final_price']
        
        if any(k in text for k in ["size", "sizes"]):
            sizes_str = ", ".join(p['sizes']) if p.get('sizes') else "Free Size"
            return {
                "text": f"For **{p_name}**, the available sizes are: **{sizes_str}**. Bangles are standard Indian sizes: 2.4 (Small), 2.6 (Medium), 2.8 (Large).",
                "products": [p],
                "action_chips": ["Add to Cart", "View Size Chart", "Check Price"]
            }
            
        if any(k in text for k in ["color", "colors", "shade"]):
            colors_str = ", ".join(p['colors']) if p.get('colors') else "Standard"
            return {
                "text": f"**{p_name}** is available in: **{colors_str}**. We also do custom color orders on request!",
                "products": [p],
                "action_chips": ["Add to Cart", "Check Stock", "Delivery Time"]
            }

        if any(k in text for k in ["material", "fabric", "made of"]):
            return {
                "text": f"**{p_name}** is carefully handcrafted using premium **{p['material']}**. It features durable core framing with smooth high-luster finish.",
                "products": [p],
                "action_chips": ["Add to Cart", "Care Instructions", "Buy Now"]
            }

        if any(k in text for k in ["price", "cost", "how much"]):
            discount_note = f" (Includes {p['discount']}% off!)" if p['discount'] > 0 else ""
            return {
                "text": f"**{p_name}** is priced at **₹{price}**{discount_note}.",
                "products": [p],
                "action_chips": ["Add to Cart", "Buy Now", "Check Delivery"]
            }

        if any(k in text for k in ["wedding", "suitable for", "occasion", "party", "wear"]):
            return {
                "text": f"Yes! **{p_name}** is crafted for **{p['occasion']}** occasions. It pairs beautifully with ethnic and fusion attire.",
                "products": [p],
                "action_chips": ["Add to Cart", "Find Matching Earrings", "Find Matching Chain"]
            }

        if any(k in text for k in ["stock", "available", "in stock"]):
            stock_msg = f"Yes, it is in stock ({p['stock']} units available)." if p['stock'] > 0 else "Currently out of stock, but restock is underway!"
            return {
                "text": f"**{p_name}**: {stock_msg}",
                "products": [p],
                "action_chips": ["Add to Cart", "Buy Now"]
            }

        return {
            "text": f"**{p_name}** (₹{price}) is handcrafted with {p['material']} for {p['occasion']}. Let me know if you'd like to select a size or add it to your bag!",
            "products": [p],
            "action_chips": ["Add to Cart", "Check Available Sizes", "Care Guidelines"]
        }

    def _handle_order_intent(self, text: str, tracking_number: Optional[str], user_id: Optional[int]) -> Dict[str, Any]:
        if tracking_number:
            order = get_order_by_tracking(tracking_number)
            if order:
                items_summary = ", ".join([f"{item['product_name']} (Qty: {item['quantity']})" for item in order['items']])
                status_emoji = {
                    "Pending": "⏳",
                    "Confirmed": "✅",
                    "Packed": "📦",
                    "Shipped": "🚚",
                    "Out for Delivery": "🛵",
                    "Delivered": "🎉",
                    "Cancelled": "❌"
                }.get(order['order_status'], "📦")
                
                return {
                    "text": f"{status_emoji} **Order #{order['tracking_number']}** is currently **{order['order_status']}**.\n\n"
                            f"**Recipient:** {order['customer_name']}\n"
                            f"**Items:** {items_summary}\n"
                            f"**Total Amount:** ₹{order['total_amount']}\n"
                            f"**Destination:** {order['city']}, {order['state']} - {order['pincode']}",
                    "products": [],
                    "order_info": order,
                    "action_chips": ["Track on Map", "Delivery Timeline", "Shop More"]
                }
            else:
                return {
                    "text": f"I couldn't find an order matching #{tracking_number}. Please double-check your tracking ID or contact customer support at care@kkcollections.com.",
                    "products": [],
                    "action_chips": ["Track My Order", "Contact Support"]
                }

        # If logged in, check user's orders
        if user_id:
            user_orders = get_user_orders(user_id)
            if user_orders:
                latest = user_orders[0]
                status_emoji = "🚚" if latest['order_status'] == 'Shipped' else "📦"
                return {
                    "text": f"{status_emoji} Here is your most recent order **#{latest['tracking_number']}**:\n\n"
                            f"**Status:** {latest['order_status']}\n"
                            f"**Total:** ₹{latest['total_amount']}\n"
                            f"**Placed on:** {latest['created_at'][:10]}\n\n"
                            f"Would you like to view the complete tracking timeline?",
                    "products": [],
                    "order_info": latest,
                    "action_chips": [f"Track #{latest['tracking_number']}", "View All Orders", "Shop Bangles"]
                }
            else:
                return {
                    "text": "You don't have any active orders associated with your account yet. Let's find something gorgeous for you to wear!",
                    "products": self._get_highlight_products(3),
                    "action_chips": ["Shop Bangles", "Shop Earrings", "Under ₹300"]
                }

        return {
            "text": "To look up your order, please provide your **Order Tracking ID** (for example: `#KK20260918001`) or log in to your KK_COLLECTIONS account. 📦",
            "products": [],
            "action_chips": ["Login to My Account", "Example: Track #KK20260918001", "Help Center"]
        }

    def _handle_combo_recommendation(self, text: str, preferences: dict) -> Dict[str, Any]:
        # Recommend a complete harmonious set: Bangles + Earrings + Invisible Chain
        bangles = get_all_products(category_slug="bangles", limit=1)
        earrings = get_all_products(category_slug="earrings", limit=1)
        chains = get_all_products(category_slug="chains", limit=1)
        combos = get_all_products(category_slug="collections", limit=1)

        combo_products = []
        if bangles: combo_products.append(bangles[0])
        if earrings: combo_products.append(earrings[0])
        if chains: combo_products.append(chains[0])

        combined_price = sum([p['final_price'] for p in combo_products])
        
        # Also include our curated combo set
        all_recs = (combos + combo_products) if combos else combo_products

        return {
            "text": f"Here is a bespoke matching set curated for you! ✨\n\n"
                    f"💖 **Bangles:** {bangles[0]['product_name'] if bangles else 'Classic Bangles'}\n"
                    f"💖 **Earrings:** {earrings[0]['product_name'] if earrings else 'Silk Jhumkas'}\n"
                    f"💖 **Necklace:** {chains[0]['product_name'] if chains else 'Solitaire Invisible Chain'}\n\n"
                    f"**Combined Special Price: ₹{combined_price}** (Free Shipping Included!)",
            "products": all_recs[:4],
            "combo_info": {"combined_price": combined_price, "items_count": len(combo_products)},
            "action_chips": ["Add Full Combo to Cart", "Wedding Collection", "Shop Pink Bangles"]
        }

    def _handle_color_matching(self, outfit_color: str) -> Dict[str, Any]:
        matched_shades = self.color_matches.get(outfit_color, ["gold", "pearl"])
        shades_text = ", ".join(matched_shades).title()
        
        # Search DB for matching products
        matching_products = []
        for shade in matched_shades:
            prods = get_all_products(color=shade, limit=2)
            for p in prods:
                if p not in matching_products:
                    matching_products.append(p)
                    
        # If not enough, search by title/description
        if len(matching_products) < 3:
            more = get_all_products(search=outfit_color, limit=3)
            for p in more:
                if p not in matching_products:
                    matching_products.append(p)

        if not matching_products:
            matching_products = self._get_highlight_products(3)

        return {
            "text": f"For a **{outfit_color.capitalize()} saree / outfit**, the most flattering accessories are in **{shades_text}** tones! 💕 Here are our handcrafted matching pieces currently in stock:",
            "products": matching_products[:4],
            "action_chips": [f"More {outfit_color.capitalize()} Bangles", "Gold Jhumkas", "Invisible Chain", "Create a Set"]
        }

    def _handle_budget_search(self, text: str, max_budget: float, preferences: dict) -> Dict[str, Any]:
        category = self._extract_category(text) or preferences.get("category")
        results = get_all_products(category_slug=category, max_price=max_budget, limit=6)
        
        cat_label = category if category else "accessories"
        if results:
            return {
                "text": f"Here are gorgeous {cat_label} under **₹{int(max_budget)}** from KK_COLLECTIONS: ✨",
                "products": results,
                "action_chips": ["Shop Bangles", "Shop Earrings", "Under ₹500", "Free Shipping Info"]
            }
        else:
            cheapest = get_all_products(category_slug=category, sort_by="price_low", limit=3)
            return {
                "text": f"We don't currently have {cat_label} under ₹{int(max_budget)}, but our lowest priced premium handcrafted pieces start at ₹{cheapest[0]['final_price'] if cheapest else 180}:",
                "products": cheapest,
                "action_chips": ["Shop All Accessories", "Trending Now"]
            }

    def _handle_occasion_search(self, occasion: str, text: str, preferences: dict) -> Dict[str, Any]:
        category = self._extract_category(text)
        results = get_all_products(category_slug=category, occasion=occasion, limit=6)
        
        if not results:
            results = get_all_products(occasion=occasion, limit=6)
            
        return {
            "text": f"For **{occasion}** celebrations, here are our most recommended bridal & festive statement pieces: 💖",
            "products": results,
            "action_chips": ["Bridal Sets", "Haldi Specials", "Party Wear Earrings", "Combo Sets"]
        }

    def _handle_category_search(self, category: str, text: str, preferences: dict) -> Dict[str, Any]:
        color = preferences.get("favorite_color")
        for c in ["red", "pink", "green", "blue", "gold", "maroon", "yellow"]:
            if c in text:
                color = c
                break
                
        results = get_all_products(category_slug=category, color=color, limit=6)
        cat_names = {
            "bangles": "thread bangles and kada sets",
            "earrings": "silk thread jhumkas and designer earrings",
            "chains": "invisible chains and delicate pendants",
            "collections": "curated combos and bridal collections"
        }
        
        label = cat_names.get(category, category)
        color_note = f" in {color.capitalize()}" if color else ""
        return {
            "text": f"Sure! 💕 Here are our available {label}{color_note}:",
            "products": results,
            "action_chips": ["Under ₹300", "Under ₹500", "Wedding Collection", "Size Guide"]
        }

    def _handle_faq_query(self, text: str) -> Optional[Dict[str, Any]]:
        faqs = get_all_faqs()
        
        # Shipping / Delivery
        if any(k in text for k in ["shipping", "delivery", "courier", "how many days", "when will it reach"]):
            for f in faqs:
                if f['category'] == 'Shipping':
                    return {
                        "text": f"📦 **Shipping Policy:** {f['answer']}",
                        "products": [],
                        "action_chips": ["Track My Order", "COD Availability", "Shop Now"]
                    }

        # Return / Exchange
        if any(k in text for k in ["return", "exchange", "refund", "replace", "cancel"]):
            for f in faqs:
                if f['category'] == 'Returns':
                    return {
                        "text": f"🔄 **Return & Exchange:** {f['answer']}",
                        "products": [],
                        "action_chips": ["Contact Support", "Size Guide", "Shop Bangles"]
                    }

        # Payment / COD
        if any(k in text for k in ["cod", "cash on delivery", "payment", "upi", "card", "paytm", "gpay"]):
            for f in faqs:
                if f['category'] == 'Payment':
                    return {
                        "text": f"💳 **Payment Options:** {f['answer']}",
                        "products": [],
                        "action_chips": ["Shop Now", "Under ₹300", "Shipping Info"]
                    }

        # Size Guide
        if any(k in text for k in ["size", "sizes", "measure", "bangle size", "diameter"]):
            for f in faqs:
                if f['category'] == 'Sizing':
                    return {
                        "text": f"📏 **Size Guide:** {f['answer']}",
                        "products": [],
                        "action_chips": ["Shop Bangles", "Ask Custom Size", "Under ₹300"]
                    }

        # Product Care
        if any(k in text for k in ["care", "wash", "maintain", "tarnish", "water", "perfume"]):
            for f in faqs:
                if f['category'] == 'Product Care':
                    return {
                        "text": f"✨ **Jewelry Care Guide:** {f['answer']}",
                        "products": [],
                        "action_chips": ["Shop Bangles", "Shop Chains", "Explore Sets"]
                    }

        # Customization
        if any(k in text for k in ["custom", "customize", "customized", "match my saree", "swatch"]):
            for f in faqs:
                if f['category'] == 'Customization':
                    return {
                        "text": f"🎨 **Custom Orders:** {f['answer']}",
                        "products": [],
                        "action_chips": ["WhatsApp Store", "Shop Bangles", "Combo Sets"]
                    }

        return None

    def _get_highlight_products(self, limit: int = 4) -> List[Dict[str, Any]]:
        return get_all_products(sort_by="featured", limit=limit)

    def _ask_gemini(self, user_msg: str, preferences: dict) -> Optional[Dict[str, Any]]:
        """Optional Gemini LLM assistant with live catalog grounding"""
        if not HAS_GEMINI:
            return None
            
        prods = get_all_products(limit=10)
        catalog_summary = "\n".join([
            f"- ID {p['product_id']}: {p['product_name']} | ₹{p['final_price']} | {p['category_name']} | {p['material']} | {p['occasion']} | Colors: {p['available_colors']}"
            for p in prods
        ])
        
        system_prompt = f"""
You are "KK AI Assistant", the personal AI shopping assistant for KK_COLLECTIONS, a luxury Indian fashion accessories brand.
Brand tagline: "Elegance That Completes You".
Tagline secondary: "Bangles • Earrings • Chains • Collections".

Available Catalog Products:
{catalog_summary}

User Preferences: {json.dumps(preferences)}

Rules:
1. Warm, elegant, helpful Indian shopping tone with emojis (💕, ✨, 🌸).
2. ONLY recommend products from the catalog above. Never hallucinate unavailable items or prices.
3. If user asks for matching accessories, suggest complementary colors (e.g. green saree pairs with gold, pearl, or rani pink).
4. Respond in concise JSON format:
{{
   "text": "Your helpful response text",
   "recommended_product_ids": [1, 2, 3],
   "action_chips": ["Shop Bangles", "Shop Earrings", "Under ₹300"]
}}
"""
        if gemini_client is None:
            return None

        response = gemini_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"{system_prompt}\n\nCustomer: {user_msg}"
        )
        raw = (getattr(response, "text", "") or "").strip()
        # Parse JSON
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            data = json.loads(m.group(0))
            rec_prods = []
            for pid in data.get("recommended_product_ids", []):
                p = get_product_by_id(pid)
                if p:
                    rec_prods.append(p)
            return {
                "text": data.get("text", "Here are our recommendations for you 💕"),
                "products": rec_prods,
                "action_chips": data.get("action_chips", ["Shop Bangles", "Shop Earrings"])
            }
        return None

# Singleton instance
ai_assistant = KKAssistant()
