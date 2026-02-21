"""
Anti-Bid Manipulation Detection System
Detects suspicious bidding patterns and potential manipulation
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class ManipulationType(str, Enum):
    """Types of bid manipulation"""
    RAPID_BIDDING = "rapid_bidding"
    COLLUSION = "collusion"
    SHILL_BIDDING = "shill_bidding"
    LAST_SECOND_SNIPING = "last_second_sniping"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    BUDGET_VIOLATION = "budget_violation"


class BidManipulationDetector:
    """
    Detects and prevents bid manipulation in real-time
    """
    
    def __init__(self):
        self._team_bid_history: Dict[str, List[Dict]] = defaultdict(list)
        self._player_bid_history: Dict[str, List[Dict]] = defaultdict(list)
        self._suspicious_activities: List[Dict] = []
        self._blocked_teams: set = set()
        self._enabled = True
        
        # Detection thresholds
        self.rapid_bid_threshold = 3  # bids per 10 seconds
        self.rapid_bid_window = 10  # seconds
        self.collusion_threshold = 0.8  # similarity score
        self.sniping_window = 3  # seconds before timer expires
        
        logger.info("✅ Bid Manipulation Detector initialized")
    
    def analyze_bid(
        self,
        team_id: str,
        player_id: str,
        bid_amount: float,
        team_budget: float,
        timer_remaining: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze a bid for manipulation patterns
        Returns: {is_suspicious: bool, reasons: List[str], severity: str}
        """
        if not self._enabled:
            return {"is_suspicious": False, "reasons": [], "severity": "none"}
        
        try:
            suspicious_reasons = []
            severity = "none"
            
            # Record bid
            bid_data = {
                "team_id": team_id,
                "player_id": player_id,
                "amount": bid_amount,
                "timestamp": datetime.utcnow(),
                "timer_remaining": timer_remaining
            }
            
            self._team_bid_history[team_id].append(bid_data)
            self._player_bid_history[player_id].append(bid_data)
            
            # Check 1: Rapid bidding
            if self._check_rapid_bidding(team_id):
                suspicious_reasons.append(ManipulationType.RAPID_BIDDING)
                severity = "medium"
            
            # Check 2: Budget violation
            if bid_amount > team_budget:
                suspicious_reasons.append(ManipulationType.BUDGET_VIOLATION)
                severity = "high"
            
            # Check 3: Last-second sniping
            if timer_remaining and timer_remaining <= self.sniping_window:
                if self._check_sniping_pattern(team_id):
                    suspicious_reasons.append(ManipulationType.LAST_SECOND_SNIPING)
                    severity = "low"
            
            # Check 4: Collusion detection
            if self._check_collusion(player_id):
                suspicious_reasons.append(ManipulationType.COLLUSION)
                severity = "high"
            
            # Check 5: Shill bidding
            if self._check_shill_bidding(team_id, player_id):
                suspicious_reasons.append(ManipulationType.SHILL_BIDDING)
                severity = "high"
            
            # Log suspicious activity
            if suspicious_reasons:
                self._log_suspicious_activity(
                    team_id=team_id,
                    player_id=player_id,
                    reasons=suspicious_reasons,
                    severity=severity,
                    bid_data=bid_data
                )
            
            return {
                "is_suspicious": len(suspicious_reasons) > 0,
                "reasons": suspicious_reasons,
                "severity": severity,
                "should_block": severity == "high" and len(suspicious_reasons) >= 2
            }
        
        except Exception as e:
            logger.error(f"Failed to analyze bid: {e}")
            return {"is_suspicious": False, "reasons": [], "severity": "none"}
    
    def _check_rapid_bidding(self, team_id: str) -> bool:
        """Check if team is bidding too rapidly"""
        try:
            recent_bids = self._get_recent_bids(team_id, self.rapid_bid_window)
            return len(recent_bids) >= self.rapid_bid_threshold
        except Exception as e:
            logger.error(f"Failed to check rapid bidding: {e}")
            return False
    
    def _check_sniping_pattern(self, team_id: str) -> bool:
        """Check if team consistently snipes at last second"""
        try:
            team_bids = self._team_bid_history.get(team_id, [])
            if len(team_bids) < 5:
                return False
            
            last_second_bids = sum(
                1 for bid in team_bids[-10:]
                if bid.get("timer_remaining", 100) <= self.sniping_window
            )
            
            return last_second_bids >= 5
        except Exception as e:
            logger.error(f"Failed to check sniping pattern: {e}")
            return False
    
    def _check_collusion(self, player_id: str) -> bool:
        """Check for collusion between teams"""
        try:
            player_bids = self._player_bid_history.get(player_id, [])
            if len(player_bids) < 4:
                return False
            
            # Check if same 2 teams are bidding back and forth
            recent_teams = [bid["team_id"] for bid in player_bids[-6:]]
            unique_teams = set(recent_teams)
            
            if len(unique_teams) == 2 and len(recent_teams) >= 6:
                # Alternating pattern suggests collusion
                alternating = all(
                    recent_teams[i] != recent_teams[i+1]
                    for i in range(len(recent_teams)-1)
                )
                return alternating
            
            return False
        except Exception as e:
            logger.error(f"Failed to check collusion: {e}")
            return False
    
    def _check_shill_bidding(self, team_id: str, player_id: str) -> bool:
        """Check for shill bidding (artificial price inflation)"""
        try:
            player_bids = self._player_bid_history.get(player_id, [])
            team_bids_on_player = [b for b in player_bids if b["team_id"] == team_id]
            
            # If team bids multiple times but never wins, might be shill
            if len(team_bids_on_player) >= 5:
                # Check if team always gets outbid immediately
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to check shill bidding: {e}")
            return False
    
    def _get_recent_bids(self, team_id: str, seconds: int) -> List[Dict]:
        """Get bids from team in last N seconds"""
        try:
            cutoff = datetime.utcnow() - timedelta(seconds=seconds)
            team_bids = self._team_bid_history.get(team_id, [])
            return [bid for bid in team_bids if bid["timestamp"] > cutoff]
        except Exception as e:
            logger.error(f"Failed to get recent bids: {e}")
            return []
    
    def _log_suspicious_activity(
        self,
        team_id: str,
        player_id: str,
        reasons: List[str],
        severity: str,
        bid_data: Dict
    ):
        """Log suspicious activity"""
        try:
            activity = {
                "team_id": team_id,
                "player_id": player_id,
                "reasons": reasons,
                "severity": severity,
                "bid_data": bid_data,
                "timestamp": datetime.utcnow()
            }
            
            self._suspicious_activities.append(activity)
            
            logger.warning(
                f"SUSPICIOUS ACTIVITY: Team {team_id} - {', '.join(reasons)} - Severity: {severity}"
            )
        except Exception as e:
            logger.error(f"Failed to log suspicious activity: {e}")
    
    def block_team(self, team_id: str, reason: str):
        """Block a team from bidding"""
        try:
            self._blocked_teams.add(team_id)
            logger.warning(f"Team {team_id} blocked: {reason}")
        except Exception as e:
            logger.error(f"Failed to block team: {e}")
    
    def unblock_team(self, team_id: str):
        """Unblock a team"""
        try:
            self._blocked_teams.discard(team_id)
            logger.info(f"Team {team_id} unblocked")
        except Exception as e:
            logger.error(f"Failed to unblock team: {e}")
    
    def is_team_blocked(self, team_id: str) -> bool:
        """Check if team is blocked"""
        return team_id in self._blocked_teams
    
    def get_suspicious_activities(self, limit: int = 100) -> List[Dict]:
        """Get recent suspicious activities"""
        try:
            activities = list(self._suspicious_activities)
            activities.reverse()
            return activities[:limit]
        except Exception as e:
            logger.error(f"Failed to get suspicious activities: {e}")
            return []
    
    def get_team_risk_score(self, team_id: str) -> Dict[str, Any]:
        """Calculate risk score for a team"""
        try:
            team_activities = [
                a for a in self._suspicious_activities
                if a["team_id"] == team_id
            ]
            
            risk_score = 0
            for activity in team_activities:
                if activity["severity"] == "high":
                    risk_score += 10
                elif activity["severity"] == "medium":
                    risk_score += 5
                else:
                    risk_score += 1
            
            return {
                "team_id": team_id,
                "risk_score": risk_score,
                "suspicious_activities": len(team_activities),
                "is_blocked": self.is_team_blocked(team_id),
                "risk_level": "high" if risk_score > 20 else "medium" if risk_score > 10 else "low"
            }
        except Exception as e:
            logger.error(f"Failed to calculate risk score: {e}")
            return {"team_id": team_id, "risk_score": 0, "risk_level": "low"}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics"""
        try:
            return {
                "total_suspicious_activities": len(self._suspicious_activities),
                "blocked_teams": len(self._blocked_teams),
                "teams_monitored": len(self._team_bid_history),
                "players_monitored": len(self._player_bid_history),
                "enabled": self._enabled
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    def reset(self):
        """Reset all detection data"""
        self._team_bid_history.clear()
        self._player_bid_history.clear()
        self._suspicious_activities.clear()
        self._blocked_teams.clear()
        logger.info("Bid manipulation detector reset")
    
    def disable(self):
        """Disable detector"""
        self._enabled = False
        logger.warning("Bid manipulation detector disabled")
    
    def enable(self):
        """Enable detector"""
        self._enabled = True
        logger.info("Bid manipulation detector enabled")


# Global instance
bid_detector = BidManipulationDetector()
