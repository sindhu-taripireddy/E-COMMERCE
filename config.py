import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "kk_collections.db"
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
PRODUCT_IMAGES_DIR = BASE_DIR / "static" / "images" / "products"

# Ensure required directories exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
PRODUCT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "kk_collections_secret_key_2026_super_secure")
    DATABASE = str(DATABASE_PATH)
    UPLOAD_FOLDER = str(UPLOAD_FOLDER)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    
    # AI Engine Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    AI_MODEL_NAME = "gemini-1.5-flash"
    
    # Store Information
    STORE_NAME = "KK_COLLECTIONS"
    TAGLINE = "Elegance That Completes You"
    SECONDARY_TAGLINE = "Bangles • Earrings • Chains • Collections"
    INSTAGRAM_URL = "https://www.instagram.com/kk_collectons?stkn=MW5neW1lYWlkMDhxbA=="
    SUPPORT_EMAIL = "care@kkcollections.com"
    SUPPORT_PHONE = "+91 98765 43210"
    WHATSAPP_NUMBER = "+919876543210"
