#!/usr/bin/env python3
"""
Database Backup Script
Backs up MongoDB database with compression and retention policy.
Run daily via cron: 0 2 * * * /path/to/backup_database.py
"""
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_backup():
    """Create a compressed MongoDB backup."""
    if not settings.BACKUP_ENABLED:
        logger.info("Backups are disabled in configuration")
        return
    
    # Create backup directory if it doesn't exist
    backup_dir = Path(settings.BACKUP_PATH)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = backup_dir / backup_name
    
    logger.info(f"Starting backup to {backup_path}")
    
    try:
        # Run mongodump with compression
        cmd = [
            "mongodump",
            f"--uri={settings.DATABASE_URL}/{settings.DB_NAME}",
            f"--out={backup_path}",
            "--gzip"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Backup completed successfully: {backup_path}")
        logger.info(f"Backup size: {get_dir_size(backup_path)} MB")
        
        # Clean old backups
        cleanup_old_backups(backup_dir)
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Backup failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during backup: {e}")
        return False


def get_dir_size(path: Path) -> float:
    """Get directory size in MB."""
    total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    return round(total / (1024 * 1024), 2)


def cleanup_old_backups(backup_dir: Path):
    """Remove backups older than retention period."""
    retention_days = settings.BACKUP_RETENTION_DAYS
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    logger.info(f"Cleaning backups older than {retention_days} days")
    
    removed_count = 0
    for backup in backup_dir.iterdir():
        if not backup.is_dir() or not backup.name.startswith("backup_"):
            continue
        
        # Extract date from backup name (backup_YYYYMMDD_HHMMSS)
        try:
            date_str = backup.name.split("_")[1]
            backup_date = datetime.strptime(date_str, "%Y%m%d")
            
            if backup_date < cutoff_date:
                logger.info(f"Removing old backup: {backup.name}")
                subprocess.run(["rm", "-rf", str(backup)], check=True)
                removed_count += 1
        except (IndexError, ValueError) as e:
            logger.warning(f"Could not parse backup date from {backup.name}: {e}")
    
    logger.info(f"Removed {removed_count} old backups")


def verify_backup(backup_path: Path) -> bool:
    """Verify backup integrity."""
    # Check if backup directory exists and has files
    if not backup_path.exists():
        return False
    
    files = list(backup_path.rglob("*.bson.gz"))
    if not files:
        logger.error("No BSON files found in backup")
        return False
    
    logger.info(f"Backup verification passed: {len(files)} collections backed up")
    return True


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Starting database backup")
    logger.info("=" * 50)
    
    success = create_backup()
    
    if success:
        logger.info("Backup completed successfully")
        sys.exit(0)
    else:
        logger.error("Backup failed")
        sys.exit(1)
