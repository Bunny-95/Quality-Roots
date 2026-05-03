"""
Organic Roots Configuration
Contains all configuration constants and settings
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database configuration
DATABASE_URL = f"sqlite:///{BASE_DIR}/backend/organic_roots.db"

# JWT Configuration
SECRET_KEY = "organic-roots-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Application configuration
APP_NAME = "Organic Roots"
VERSION = "1.0.0"
DEBUG = True

# CORS Configuration
ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

# QR Code Configuration
QR_BASE_URL = "http://localhost:5173/verify?batch="
QR_CODES_DIR = BASE_DIR / "qr_codes"

# API Configuration
API_PREFIX = "/api"

# Ports
BACKEND_PORT = 8000
FRONTEND_PORT = 5173

# Admin credentials (default)
ADMIN_EMAIL = "admin@organicroots.com"
ADMIN_PASSWORD = "admin123"

# File upload settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]

# Blockchain settings
BLOCKCHAIN_DIFFICULTY = 2  # Number of leading zeros required

# AI Model settings
RANDOM_STATE = 42  # For reproducible results
MODEL_DIR = BASE_DIR / "backend" / "models" / "trained"
