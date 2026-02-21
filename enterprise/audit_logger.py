"""
Enterprise Audit Logging System
Comprehensive audit trail for all critical operations
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Audit action types"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    TEAM_LOGIN = "team_login"
    ADMIN_LOGIN = "admin_login"
    BID_PLACED = "bid_placed"
    BID_REJECTED = "bid_rejected"
    PLAYER_CREATED = "player_created"
    PLAYER_APPROVED = "player_approved"
    PLAYER_REJECTED = "player_rejected"
    PLAYER_SOLD = "player_sold"
    TEAM_CREATED = "team_created"
    TEAM_UPDATED = "team_updated"
    AUCTION_STARTED = "auction_started"
    AUCTION_PAUSED = "auction_paused"
    AUCTION_ENDED = "auction_ended"
    CONFIG_CHANGED = "config_changed"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_EXPORT = "data_export"
    ADMIN_ACTION = "admin_action"


class AuditLevel(str, Enum):
    """Audit severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SECURITY = "security"


class AuditEntry:
    """Audit log entry"""
    def __init__(
        self,
        action: AuditAction,
        user_id: Optional[str],
        user_email: Optional[str],
        ip_address: Optional[str],
        details: Dict[str, Any],
        level: AuditLevel = AuditLevel.INFO,
        timestamp: Optional[datetime] = None
    ):
        self.action = action
        self.user_id = user_id
        self.user_email = user_email
        self.ip_address = ip_address
        self.details = details
        self.level = level
        self.timestamp = timestamp or datetime.utcnow()
        self.entry_id = f"{action}_{self.timestamp.timestamp()}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "action": self.action,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "ip_address": self.ip_address,
            "details": self.details,
            "level": self.level,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class EnterpriseAuditLogger:
    """
    Enterprise-grade audit logging system
    Maintains comprehensive audit trail with search and filtering
    """
    
    def __init__(self, max_entries: int = 10000):
        self._audit_log: deque = deque(maxlen=max_entries)
        self._enabled = True
        self._max_entries = max_entries
        logger.info("✅ Enterprise Audit Logger initialized")
    
    def log(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        level: AuditLevel = AuditLevel.INFO
    ):
        """Log an audit entry"""
        if not self._enabled:
            return
        
        try:
            entry = AuditEntry(
                action=action,
                user_id=user_id,
                user_email=user_email,
                ip_address=ip_address,
                details=details or {},
                level=level
            )
            
            self._audit_log.append(entry)
            
            # Log to standard logger based on level
            log_message = f"AUDIT: {action} by {user_email or user_id or 'anonymous'} from {ip_address}"
            if level == AuditLevel.CRITICAL or level == AuditLevel.SECURITY:
                logger.warning(log_message)
            else:
                logger.info(log_message)
        
        except Exception as e:
            logger.error(f"Failed to log audit entry: {e}")
    
    def get_logs(
        self,
        action: Optional[AuditAction] = None,
        user_id: Optional[str] = None,
        level: Optional[AuditLevel] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit logs with optional filtering"""
        try:
            logs = list(self._audit_log)
            
            # Apply filters
            if action:
                logs = [log for log in logs if log.action == action]
            if user_id:
                logs = [log for log in logs if log.user_id == user_id]
            if level:
                logs = [log for log in logs if log.level == level]
            
            # Return most recent first
            logs.reverse()
            return [log.to_dict() for log in logs[:limit]]
        
        except Exception as e:
            logger.error(f"Failed to get audit logs: {e}")
            return []
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all activity for a specific user"""
        return self.get_logs(user_id=user_id, limit=limit)
    
    def get_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all security-related events"""
        return self.get_logs(level=AuditLevel.SECURITY, limit=limit)
    
    def get_critical_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all critical events"""
        return self.get_logs(level=AuditLevel.CRITICAL, limit=limit)
    
    def search_logs(
        self,
        search_term: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search audit logs by term"""
        try:
            logs = list(self._audit_log)
            search_lower = search_term.lower()
            
            matching_logs = []
            for log in logs:
                log_dict = log.to_dict()
                log_str = json.dumps(log_dict).lower()
                if search_lower in log_str:
                    matching_logs.append(log_dict)
            
            matching_logs.reverse()
            return matching_logs[:limit]
        
        except Exception as e:
            logger.error(f"Failed to search logs: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audit log statistics"""
        try:
            action_counts = {}
            level_counts = {}
            user_counts = {}
            
            for entry in self._audit_log:
                action_counts[entry.action] = action_counts.get(entry.action, 0) + 1
                level_counts[entry.level] = level_counts.get(entry.level, 0) + 1
                if entry.user_id:
                    user_counts[entry.user_id] = user_counts.get(entry.user_id, 0) + 1
            
            return {
                "total_entries": len(self._audit_log),
                "max_entries": self._max_entries,
                "action_counts": action_counts,
                "level_counts": level_counts,
                "unique_users": len(user_counts),
                "most_active_users": sorted(
                    user_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                "enabled": self._enabled
            }
        
        except Exception as e:
            logger.error(f"Failed to get audit stats: {e}")
            return {}
    
    def export_logs(self, format: str = "json") -> str:
        """Export all audit logs"""
        try:
            logs = [log.to_dict() for log in self._audit_log]
            
            if format == "json":
                return json.dumps(logs, indent=2)
            else:
                return json.dumps(logs)
        
        except Exception as e:
            logger.error(f"Failed to export logs: {e}")
            return "[]"
    
    def clear_old_logs(self, days: int = 90):
        """Clear logs older than specified days"""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            original_count = len(self._audit_log)
            
            self._audit_log = deque(
                [log for log in self._audit_log if log.timestamp > cutoff],
                maxlen=self._max_entries
            )
            
            removed = original_count - len(self._audit_log)
            logger.info(f"Cleared {removed} old audit logs")
            return removed
        
        except Exception as e:
            logger.error(f"Failed to clear old logs: {e}")
            return 0
    
    def disable(self):
        """Disable audit logging"""
        self._enabled = False
        logger.warning("Audit logging disabled")
    
    def enable(self):
        """Enable audit logging"""
        self._enabled = True
        logger.info("Audit logging enabled")


# Global instance
audit_logger = EnterpriseAuditLogger()
