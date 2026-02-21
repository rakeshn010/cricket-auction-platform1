"""
Distributed Auction Event Manager
Handles event-driven architecture for auction events
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class AuctionEventType(str, Enum):
    """Auction event types"""
    BID_PLACED = "bid_placed"
    BID_WON = "bid_won"
    PLAYER_SOLD = "player_sold"
    PLAYER_UNSOLD = "player_unsold"
    AUCTION_STARTED = "auction_started"
    AUCTION_PAUSED = "auction_paused"
    AUCTION_RESUMED = "auction_resumed"
    AUCTION_ENDED = "auction_ended"
    TIMER_TICK = "timer_tick"
    TIMER_EXPIRED = "timer_expired"
    TEAM_BUDGET_LOW = "team_budget_low"
    PLAYER_ACTIVATED = "player_activated"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class AuctionEvent:
    """Auction event data structure"""
    def __init__(
        self,
        event_type: AuctionEventType,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
        self.event_id = event_id or f"{event_type}_{self.timestamp.timestamp()}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class DistributedEventManager:
    """
    Enterprise-grade event manager for auction events
    Supports pub/sub pattern with multiple subscribers
    """
    
    def __init__(self):
        self._subscribers: Dict[AuctionEventType, List[Callable]] = defaultdict(list)
        self._event_history: List[AuctionEvent] = []
        self._max_history = 1000
        self._enabled = True
        logger.info("✅ Distributed Event Manager initialized")
    
    def subscribe(self, event_type: AuctionEventType, callback: Callable):
        """Subscribe to an event type"""
        try:
            self._subscribers[event_type].append(callback)
            logger.info(f"Subscribed to {event_type}")
        except Exception as e:
            logger.error(f"Failed to subscribe to {event_type}: {e}")
    
    def unsubscribe(self, event_type: AuctionEventType, callback: Callable):
        """Unsubscribe from an event type"""
        try:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                logger.info(f"Unsubscribed from {event_type}")
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {event_type}: {e}")
    
    async def publish(self, event: AuctionEvent):
        """Publish an event to all subscribers"""
        if not self._enabled:
            return
        
        try:
            # Store in history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            # Notify subscribers
            subscribers = self._subscribers.get(event.event_type, [])
            for callback in subscribers:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"Subscriber callback failed for {event.event_type}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {e}")
    
    def get_event_history(self, event_type: Optional[AuctionEventType] = None, limit: int = 100) -> List[Dict]:
        """Get event history"""
        try:
            if event_type:
                events = [e for e in self._event_history if e.event_type == event_type]
            else:
                events = self._event_history
            
            return [e.to_dict() for e in events[-limit:]]
        except Exception as e:
            logger.error(f"Failed to get event history: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event manager statistics"""
        try:
            event_counts = defaultdict(int)
            for event in self._event_history:
                event_counts[event.event_type] += 1
            
            return {
                "total_events": len(self._event_history),
                "event_counts": dict(event_counts),
                "subscriber_counts": {
                    event_type: len(callbacks)
                    for event_type, callbacks in self._subscribers.items()
                },
                "enabled": self._enabled
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    def clear_history(self):
        """Clear event history"""
        self._event_history.clear()
        logger.info("Event history cleared")
    
    def disable(self):
        """Disable event manager"""
        self._enabled = False
        logger.warning("Event manager disabled")
    
    def enable(self):
        """Enable event manager"""
        self._enabled = True
        logger.info("Event manager enabled")


# Global instance
event_manager = DistributedEventManager()
