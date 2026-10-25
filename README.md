# KK_COLLECTIONS — AI-Powered Fashion Accessories E-Commerce Platform

> **Tagline:** Elegance That Completes You  
> **Secondary Tagline:** Bangles • Earrings • Chains • Collections  
> **Business Reference:** [Instagram @kk_collectons](https://www.instagram.com/kk_collectons?stkn=MW5neW1lYWlkMDhxbA==)

A complete, responsive, production-ready e-commerce web platform for **KK_COLLECTIONS**, an Indian fashion accessories brand specializing in handcrafted silk thread bangles, traditional jhumkas, bridal chura sets, minimal invisible chains, and bespoke combo sets.

The platform combines a high-conversion shopping experience with an intelligent **KK AI Shopping Assistant** and a comprehensive **Seller Admin Management Portal**.

---

## 🌟 Key Features

### 1. Customer Shopping Experience
- **Luxury Brand Aesthetics:** Royal wine & burgundy, champagne cream, and gold accent styling inspired by premium Indian fashion boutiques.
- **Shop Catalog & Discovery:** 
  - Dynamic filtering by **Category** (Bangles, Earrings, Chains, Collections), **Price Slider** (₹200 - ₹1,500), **Color Swatches** (Red, Pink, Green, Blue, Gold, Maroon, Yellow), **Bangle Sizes** (2.4, 2.6, 2.8), and **Occasion** (Wedding, Festive, Party Wear, Traditional, Daily Wear, Haldi).
  - Sorting: Featured, Newest, Price Low-to-High, Price High-to-Low, Best Selling.
- **Product Details Page:**
  - High-resolution gallery & handcrafted badges.
  - Interactive color & size variant selectors with live stock indicators.
  - Verified customer reviews & rating submission form.
  - **"Ask KK AI About This Product 🤖"** button that opens the AI Assistant with instant product context.
- **Cart & Bag Management:**
  - Itemized variant breakdown (Color, Size, SKU).
  - Real-time quantity stepper and line total updates.
  - **Free Shipping Progress Meter** (unlocked on orders over ₹499).
  - Coupon code support (Try `KKFIRST10` for 10% welcome discount).
- **Checkout & Simulated Payments:**
  - 2-step checkout with address auto-fill for logged-in patrons.
  - Realistic simulated payment options: **UPI** (Dynamic QR code & VPA), **Credit/Debit Card**, **Net Banking**, and **Cash on Delivery (COD)**.
- **Order Tracking Timeline:**
  - Visual 6-stage milestone tracker:  
    `Order Placed` ➔ `Confirmed` ➔ `Packed` ➔ `Shipped` ➔ `Out for Delivery` ➔ `Delivered`
  - Integrated carrier tracking details and direct AI query lookup.

---

### 2. KK AI Shopping Assistant 🤖
A floating conversational AI assistant accessible across all customer pages (`💬 KK AI`):
- **Natural Language Product Discovery:**
  - *"Show me thread bangles"* ➔ Displays interactive product cards with direct "Add to Cart" inside chat.
- **Budget-Based Queries:**
  - *"I need earrings under ₹300"* ➔ Accurately extracts budget ceiling and filters database.
- **Outfit & Saree Color Matching:**
  - *"I am wearing a green saree. What accessories will match?"* ➔ Advises complementary tones (gold, emerald green, pearl, contrasting pink) and queries matching catalog inventory.
- **Occasion-Based Recommendations:**
  - *"I need something for a wedding"* ➔ Curates bridal bangles, chandbali earrings, and kundan sets.
- **Combo Set Assembly:**
  - *"Can you create a matching set?"* ➔ Combines Bangles + Jhumkas + Invisible Chain and computes bundled pricing.
- **Order Tracking in Chat:**
  - *"Where is my order #KK20260918001?"* ➔ Returns live delivery status and link to timeline.
- **FAQ & Care Support:**
  - Answers shipping timelines, COD policies, returns, bangle sizing guides, and thread jewelry care.
- **Strict Anti-Hallucination & Dual-Mode Engine:**
  - Queries actual SQLite database; never invents fake prices or out-of-stock items.
  - Built-in NLP/RAG engine guarantees 100% offline & demo reliability.
  - Seamlessly leverages **Google Gemini API** when `GEMINI_API_KEY` is provided.

---

### 3. Seller Admin Dashboard 📊
A seller portal for business management:
- **KPI Overview Cards:** Total Sales, Total Orders, Active Products, Registered Customers, Low Stock Alerts.
- **Interactive Visualizations:** Chart.js revenue velocity line charts and category volume doughnut charts.
- **Product Management:** Add new accessories, edit prices/descriptions/variants, and remove items.
- **Inventory & Variant Tracking:** SKUs mapped across colors and sizes (2.4, 2.6, 2.8) with stock status indicators (🟢 In Stock, 🟡 Low Stock, 🔴 Out of Stock).
- **Order Management:** Filter orders by status and transition orders with one click (`Pending` ➔ `Confirmed` ➔ `Packed` ➔ `Shipped` ➔ `Delivered`).
- **Customer CRM & Analytics:** Customer lifetime spend, average order value (AOV), and monthly performance history.

---

## 🔑 Pre-Seeded Demo Credentials

| Role | Email | Password | Features Accessible |
|---|---|---|---|
| **Store Administrator** | `admin@kkcollections.com` | `admin123` | Full Seller Portal, Inventory, Orders, Analytics |
| **Demo Customer** | `demo@kkcollections.com` | `customer123` | Saved Address, Order History, Wishlist |

### Demo Tracking IDs for Testing:
- `#KK20260918001` (Status: **Shipped** — Thread Bangles + Pink Jhumkas)
- `#KK20260915002` (Status: **Delivered** — Solitaire Invisible Chain)

---

## 🚀 Running the Project

### 1. Prerequisites
Python 3.10+ installed.

### 2. Run Application
```powershell
python app.py
```
The application will launch on:
```
http://127.0.0.1:5000
```

### 3. (Optional) Enable Google Gemini LLM API
To enable Gemini API alongside the built-in search engine:
```powershell
$env:GEMINI_API_KEY="your-gemini-api-key-here"
python app.py
```
*(Note: If no API key is provided, the AI Assistant runs with its built-in NLP & RAG database engine with 0ms external latency).*

---

## 🗄️ Database Architecture
Built on SQLite with foreign key enforcement:
- `USERS`: Customer accounts and profiles
- `ADMIN`: Protected administrative credentials
- `CATEGORIES`: Bangles, Earrings, Chains, Collections
- `PRODUCTS`: Master product catalog with pricing, discounts, and ratings
- `PRODUCT_VARIANTS`: Colors, bangle sizes (2.4, 2.6, 2.8), and individual SKU stocks
- `CART` & `CART_ITEMS`: Guest and user persistent shopping bags
- `WISHLIST`: Saved items
- `ORDERS` & `ORDER_ITEMS`: Complete order records with delivery statuses
- `PAYMENTS`: Simulated transaction references
- `REVIEWS`: Customer ratings and feedback
- `ADDRESSES`: Multi-city delivery addresses
- `FAQ`: Categorized store policies and care guides
- `CHAT_SESSIONS` & `CHAT_MESSAGES`: AI conversation history and session preferences
