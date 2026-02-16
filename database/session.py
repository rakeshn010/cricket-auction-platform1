"""
Database session management.
Handles MongoDB connection and provides database instance.
"""
from pymongo import MongoClient
from core.config import settings
import logging

logger = logging.getLogger(__name__)

try:
    client = MongoClient(settings.DATABASE_URL)
    db = client[settings.DB_NAME]
    
    # Test connection
    client.server_info()
    logger.info(f"Connected to MongoDB: {settings.DB_NAME}")
    
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise
