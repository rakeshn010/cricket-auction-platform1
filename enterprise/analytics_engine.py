"""
Real-Time Analytics Engine
Tracks auction metrics, bidding patterns, and team performance
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class RealTimeAnalyticsEngine:
    """
    Enterprise analytics engine for auction insights
    Tracks real-time metrics and generates predictions
    """
    
    def __init__(self):
        self._bid_metrics: Dict[str, List[Dict]] = defaultdict(list)
        self._team_metrics: Dict[str, Dict] = defaultdict(dict)
        self._player_metrics: Dict[str, Dict] = defaultdict(dict)
        self._auction_metrics: Dict[str, Any] = {}
        self._enabled = True
        logger.info("✅ Real-Time Analytics Engine initialized")
    
    def track_bid(self, team_id: str, player_id: str, amount: float, timestamp: Optional[datetime] = None):
        """Track a bid event"""
        if not self._enabled:
            return
        
        try:
            bid_data = {
                "team_id": team_id,
                "player_id": player_id,
                "amount": amount,
                "timestamp": timestamp or datetime.utcnow()
            }
            
            self._bid_metrics[team_id].append(bid_data)
            
            # Update team metrics
            if team_id not in self._team_metrics:
                self._team_metrics[team_id] = {
                    "total_bids": 0,
                    "total_spent": 0,
                    "avg_bid": 0,
                    "max_bid": 0,
                    "players_won": 0
                }
            
            self._team_metrics[team_id]["total_bids"] += 1
            self._team_metrics[team_id]["max_bid"] = max(
                self._team_metrics[team_id]["max_bid"], amount
            )
            
        except Exception as e:
            logger.error(f"Failed to track bid: {e}")
    
    def track_player_sold(self, player_id: str, team_id: str, final_price: float):
        """Track when a player is sold"""
        if not self._enabled:
            return
        
        try:
            self._player_metrics[player_id] = {
                "sold_to": team_id,
                "final_price": final_price,
                "sold_at": datetime.utcnow()
            }
            
            if team_id in self._team_metrics:
                self._team_metrics[team_id]["total_spent"] += final_price
                self._team_metrics[team_id]["players_won"] += 1
                
                # Calculate average
                total_bids = self._team_metrics[team_id]["total_bids"]
                if total_bids > 0:
                    bids = [b["amount"] for b in self._bid_metrics[team_id]]
                    self._team_metrics[team_id]["avg_bid"] = statistics.mean(bids)
        
        except Exception as e:
            logger.error(f"Failed to track player sold: {e}")
    
    def get_team_analytics(self, team_id: str) -> Dict[str, Any]:
        """Get analytics for a specific team"""
        try:
            if team_id not in self._team_metrics:
                return {}
            
            metrics = self._team_metrics[team_id].copy()
            
            # Add bidding velocity (bids per minute)
            bids = self._bid_metrics.get(team_id, [])
            if len(bids) >= 2:
                time_span = (bids[-1]["timestamp"] - bids[0]["timestamp"]).total_seconds() / 60
                metrics["bidding_velocity"] = len(bids) / max(time_span, 1)
            else:
                metrics["bidding_velocity"] = 0
            
            # Add recent activity
            recent_bids = [b for b in bids if (datetime.utcnow() - b["timestamp"]).seconds < 300]
            metrics["recent_bids_5min"] = len(recent_bids)
            
            return metrics
        
        except Exception as e:
            logger.error(f"Failed to get team analytics: {e}")
            return {}
    
    def get_player_analytics(self, player_id: str) -> Dict[str, Any]:
        """Get analytics for a specific player"""
        try:
            if player_id not in self._player_metrics:
                return {"status": "unsold"}
            
            return self._player_metrics[player_id]
        
        except Exception as e:
            logger.error(f"Failed to get player analytics: {e}")
            return {}
    
    def get_auction_summary(self) -> Dict[str, Any]:
        """Get overall auction analytics"""
        try:
            total_bids = sum(len(bids) for bids in self._bid_metrics.values())
            total_spent = sum(m.get("total_spent", 0) for m in self._team_metrics.values())
            players_sold = len(self._player_metrics)
            
            all_bids = []
            for bids in self._bid_metrics.values():
                all_bids.extend([b["amount"] for b in bids])
            
            return {
                "total_bids": total_bids,
                "total_spent": total_spent,
                "players_sold": players_sold,
                "active_teams": len(self._team_metrics),
                "avg_bid_amount": statistics.mean(all_bids) if all_bids else 0,
                "max_bid_amount": max(all_bids) if all_bids else 0,
                "min_bid_amount": min(all_bids) if all_bids else 0,
                "median_bid_amount": statistics.median(all_bids) if all_bids else 0
            }
        
        except Exception as e:
            logger.error(f"Failed to get auction summary: {e}")
            return {}
    
    def get_top_spenders(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top spending teams"""
        try:
            teams = [
                {"team_id": team_id, **metrics}
                for team_id, metrics in self._team_metrics.items()
            ]
            teams.sort(key=lambda x: x.get("total_spent", 0), reverse=True)
            return teams[:limit]
        
        except Exception as e:
            logger.error(f"Failed to get top spenders: {e}")
            return []
    
    def get_most_active_teams(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most active bidding teams"""
        try:
            teams = [
                {"team_id": team_id, **metrics}
                for team_id, metrics in self._team_metrics.items()
            ]
            teams.sort(key=lambda x: x.get("total_bids", 0), reverse=True)
            return teams[:limit]
        
        except Exception as e:
            logger.error(f"Failed to get most active teams: {e}")
            return []
    
    def predict_final_price(self, player_id: str, base_price: float, current_bids: int) -> Dict[str, Any]:
        """Predict final price based on bidding patterns"""
        try:
            # Simple prediction based on historical data
            all_final_prices = [m["final_price"] for m in self._player_metrics.values()]
            
            if not all_final_prices:
                return {
                    "predicted_price": base_price * 1.5,
                    "confidence": "low",
                    "range_min": base_price,
                    "range_max": base_price * 3
                }
            
            avg_multiplier = statistics.mean([p / base_price for p in all_final_prices if base_price > 0])
            
            predicted = base_price * avg_multiplier * (1 + current_bids * 0.1)
            
            return {
                "predicted_price": round(predicted, 2),
                "confidence": "medium" if len(all_final_prices) > 5 else "low",
                "range_min": round(predicted * 0.8, 2),
                "range_max": round(predicted * 1.2, 2),
                "based_on_players": len(all_final_prices)
            }
        
        except Exception as e:
            logger.error(f"Failed to predict final price: {e}")
            return {"predicted_price": base_price, "confidence": "low"}
    
    def reset(self):
        """Reset all analytics data"""
        self._bid_metrics.clear()
        self._team_metrics.clear()
        self._player_metrics.clear()
        self._auction_metrics.clear()
        logger.info("Analytics data reset")
    
    def disable(self):
        """Disable analytics engine"""
        self._enabled = False
        logger.warning("Analytics engine disabled")
    
    def enable(self):
        """Enable analytics engine"""
        self._enabled = True
        logger.info("Analytics engine enabled")


# Global instance
analytics_engine = RealTimeAnalyticsEngine()
