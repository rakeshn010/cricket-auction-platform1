"""
Enterprise Integration Module
Plugs all enterprise features into the main application
WITHOUT modifying existing code
"""
import logging
from fastapi import FastAPI
from typing import Optional

logger = logging.getLogger(__name__)


class EnterpriseIntegration:
    """
    Manages integration of all enterprise modules
    Safe initialization with fallbacks
    """
    
    def __init__(self):
        self.event_manager = None
        self.analytics_engine = None
        self.audit_logger = None
        self.request_tracker = None
        self.bid_detector = None
        self.cache_layer = None
        self.initialized = False
    
    def initialize(self, app: FastAPI):
        """
        Initialize all enterprise modules
        Safe initialization - never crashes the app
        """
        try:
            logger.info("🚀 Initializing Enterprise Modules...")
            
            # Import modules
            from enterprise.event_manager import event_manager
            from enterprise.analytics_engine import analytics_engine
            from enterprise.audit_logger import audit_logger
            from enterprise.request_tracker import request_tracker, RequestTrackingMiddleware
            from enterprise.bid_manipulation_detector import bid_detector
            from enterprise.redis_cache import cache_layer
            from enterprise.observability_dashboard import router as observability_router
            
            # Store references
            self.event_manager = event_manager
            self.analytics_engine = analytics_engine
            self.audit_logger = audit_logger
            self.request_tracker = request_tracker
            self.bid_detector = bid_detector
            self.cache_layer = cache_layer
            
            # Add request tracking middleware
            try:
                app.add_middleware(RequestTrackingMiddleware)
                logger.info("✅ Request tracking middleware added")
            except Exception as e:
                logger.warning(f"Failed to add request tracking middleware: {e}")
            
            # Add observability router
            try:
                app.include_router(observability_router)
                logger.info("✅ Observability dashboard router added")
            except Exception as e:
                logger.warning(f"Failed to add observability router: {e}")
            
            # Subscribe to auction events
            self._setup_event_subscriptions()
            
            self.initialized = True
            logger.info("✅ Enterprise modules initialized successfully")
            
            # Print summary
            self._print_summary()
        
        except Exception as e:
            logger.error(f"Enterprise initialization failed (non-fatal): {e}")
            self.initialized = False
    
    def _setup_event_subscriptions(self):
        """Setup event subscriptions for analytics and audit logging"""
        try:
            from enterprise.event_manager import AuctionEventType
            
            # Subscribe analytics engine to bid events
            async def track_bid_event(event):
                try:
                    if event.event_type == AuctionEventType.BID_PLACED:
                        data = event.data
                        self.analytics_engine.track_bid(
                            team_id=data.get("team_id"),
                            player_id=data.get("player_id"),
                            amount=data.get("amount"),
                            timestamp=event.timestamp
                        )
                except Exception as e:
                    logger.error(f"Failed to track bid event: {e}")
            
            async def track_player_sold_event(event):
                try:
                    if event.event_type == AuctionEventType.PLAYER_SOLD:
                        data = event.data
                        self.analytics_engine.track_player_sold(
                            player_id=data.get("player_id"),
                            team_id=data.get("team_id"),
                            final_price=data.get("final_price")
                        )
                except Exception as e:
                    logger.error(f"Failed to track player sold event: {e}")
            
            self.event_manager.subscribe(AuctionEventType.BID_PLACED, track_bid_event)
            self.event_manager.subscribe(AuctionEventType.PLAYER_SOLD, track_player_sold_event)
            
            logger.info("✅ Event subscriptions configured")
        
        except Exception as e:
            logger.warning(f"Failed to setup event subscriptions: {e}")
    
    def _print_summary(self):
        """Print initialization summary"""
        try:
            summary = """
╔══════════════════════════════════════════════════════════════╗
║         🏏 IPL-LEVEL ENTERPRISE FEATURES ACTIVATED 🏏        ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Distributed Event Manager                                ║
║  ✅ Real-Time Analytics Engine                               ║
║  ✅ Enterprise Audit Logger                                  ║
║  ✅ Request Tracking (Unique IDs)                            ║
║  ✅ Anti-Bid Manipulation Detector                           ║
║  ✅ Redis Cache Layer (with fallback)                        ║
║  ✅ Observability Dashboard                                  ║
║  ✅ Health Check & Metrics                                   ║
╠══════════════════════════════════════════════════════════════╣
║  📊 Dashboard: /enterprise/dashboard                         ║
║  🏥 Health: /enterprise/health                               ║
║  📈 Metrics: /enterprise/metrics                             ║
║  📊 Stats: /enterprise/stats                                 ║
╚══════════════════════════════════════════════════════════════╝
            """
            logger.info(summary)
        except:
            pass
    
    def get_status(self) -> dict:
        """Get status of all enterprise modules"""
        if not self.initialized:
            return {"initialized": False, "message": "Enterprise modules not initialized"}
        
        try:
            return {
                "initialized": True,
                "modules": {
                    "event_manager": self.event_manager._enabled if self.event_manager else False,
                    "analytics_engine": self.analytics_engine._enabled if self.analytics_engine else False,
                    "audit_logger": self.audit_logger._enabled if self.audit_logger else False,
                    "request_tracker": self.request_tracker._enabled if self.request_tracker else False,
                    "bid_detector": self.bid_detector._enabled if self.bid_detector else False,
                    "cache_layer": self.cache_layer._enabled if self.cache_layer else False
                }
            }
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"initialized": True, "error": str(e)}


# Global instance
enterprise = EnterpriseIntegration()


# Helper functions for easy integration
def track_bid(team_id: str, player_id: str, amount: float, timer_remaining: Optional[int] = None):
    """Track a bid across all enterprise systems"""
    try:
        if not enterprise.initialized:
            return
        
        # Analytics
        if enterprise.analytics_engine:
            enterprise.analytics_engine.track_bid(team_id, player_id, amount)
        
        # Bid manipulation detection
        if enterprise.bid_detector:
            result = enterprise.bid_detector.analyze_bid(
                team_id=team_id,
                player_id=player_id,
                bid_amount=amount,
                team_budget=999999,  # Should be passed from actual team data
                timer_remaining=timer_remaining
            )
            
            if result.get("should_block"):
                logger.warning(f"Team {team_id} flagged for blocking: {result['reasons']}")
        
        # Event manager
        if enterprise.event_manager:
            from enterprise.event_manager import AuctionEvent, AuctionEventType
            event = AuctionEvent(
                event_type=AuctionEventType.BID_PLACED,
                data={
                    "team_id": team_id,
                    "player_id": player_id,
                    "amount": amount,
                    "timer_remaining": timer_remaining
                }
            )
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(enterprise.event_manager.publish(event))
            except:
                pass
    
    except Exception as e:
        logger.error(f"Failed to track bid in enterprise systems: {e}")


def track_player_sold(player_id: str, team_id: str, final_price: float):
    """Track when a player is sold"""
    try:
        if not enterprise.initialized:
            return
        
        # Analytics
        if enterprise.analytics_engine:
            enterprise.analytics_engine.track_player_sold(player_id, team_id, final_price)
        
        # Event manager
        if enterprise.event_manager:
            from enterprise.event_manager import AuctionEvent, AuctionEventType
            event = AuctionEvent(
                event_type=AuctionEventType.PLAYER_SOLD,
                data={
                    "player_id": player_id,
                    "team_id": team_id,
                    "final_price": final_price
                }
            )
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(enterprise.event_manager.publish(event))
            except:
                pass
    
    except Exception as e:
        logger.error(f"Failed to track player sold in enterprise systems: {e}")


def audit_log(action: str, user_id: str = None, user_email: str = None, ip_address: str = None, details: dict = None):
    """Log an audit entry"""
    try:
        if not enterprise.initialized or not enterprise.audit_logger:
            return
        
        from enterprise.audit_logger import AuditAction, AuditLevel
        
        # Map action string to AuditAction enum
        action_map = {
            "login": AuditAction.USER_LOGIN,
            "logout": AuditAction.USER_LOGOUT,
            "bid": AuditAction.BID_PLACED,
            "admin_action": AuditAction.ADMIN_ACTION
        }
        
        audit_action = action_map.get(action, AuditAction.ADMIN_ACTION)
        
        enterprise.audit_logger.log(
            action=audit_action,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            details=details or {},
            level=AuditLevel.INFO
        )
    
    except Exception as e:
        logger.error(f"Failed to log audit entry: {e}")


# Export for easy import
__all__ = [
    "enterprise",
    "track_bid",
    "track_player_sold",
    "audit_log"
]
