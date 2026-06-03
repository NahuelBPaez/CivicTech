# config_vars.py
import os
from dotenv import load_dotenv

# Carga variables desde .env
load_dotenv()

# Variables para MongoDB
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "civictech")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# URI construida para conveniencia
if MONGO_USER and MONGO_PASSWORD:
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
else:
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"
