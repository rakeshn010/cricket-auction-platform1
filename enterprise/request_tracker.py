"""
Request Tracking Middleware
Assigns unique IDs to all requests and tracks performance
"""
import uuid
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from collections import deque
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestTracker:
    """Tracks request metrics and performance"""
    
    def __init__(self, max_requests: int = 1000):
        self._requests: deque = deque(maxlen=max_requests)
        self._active_requests: Dict[str, Dict] = {}
        self._enabled = True
        logger.info("✅ Request Tracker initialized")
    
    def start_request(self, request_id: str, method: str, path: str, client_ip: str):
        """Start tracking a request"""
        if not self._enabled:
            return
        
        try:
            self._active_requests[request_id] = {
                "request_id": request_id,
                "method": method,
                "path": path,
                "client_ip": client_ip,
                "start_time": time.time(),
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Failed to start request tracking: {e}")
    
    def end_request(
        self,
        request_id: str,
        status_code: int,
        response_size: Optional[int] = None
    ):
        """End tracking a request"""
        if not self._enabled:
            return
        
        try:
            if request_id in self._active_requests:
                request_data = self._active_requests.pop(request_id)
                request_data["end_time"] = time.time()
                request_data["duration_ms"] = (request_data["end_time"] - request_data["start_time"]) * 1000
                request_data["status_code"] = status_code
                request_data["response_size"] = response_size
                
                self._requests.append(request_data)
        except Exception as e:
            logger.error(f"Failed to end request tracking: {e}")
    
    def get_active_requests(self) -> list:
        """Get currently active requests"""
        try:
            return list(self._active_requests.values())
        except Exception as e:
            logger.error(f"Failed to get active requests: {e}")
            return []
    
    def get_recent_requests(self, limit: int = 100) -> list:
        """Get recent completed requests"""
        try:
            requests = list(self._requests)
            requests.reverse()
            return requests[:limit]
        except Exception as e:
            logger.error(f"Failed to get recent requests: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get request statistics"""
        try:
            if not self._requests:
                return {
                    "total_requests": 0,
                    "active_requests": len(self._active_requests)
                }
            
            durations = [r["duration_ms"] for r in self._requests if "duration_ms" in r]
            status_codes = {}
            methods = {}
            
            for req in self._requests:
                status = req.get("status_code", 0)
                method = req.get("method", "UNKNOWN")
                status_codes[status] = status_codes.get(status, 0) + 1
                methods[method] = methods.get(method, 0) + 1
            
            return {
                "total_requests": len(self._requests),
                "active_requests": len(self._active_requests),
                "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0,
                "min_duration_ms": min(durations) if durations else 0,
                "status_codes": status_codes,
                "methods": methods,
                "enabled": self._enabled
            }
        except Exception as e:
            logger.error(f"Failed to get request stats: {e}")
            return {}
    
    def get_slow_requests(self, threshold_ms: float = 1000, limit: int = 50) -> list:
        """Get requests slower than threshold"""
        try:
            slow_requests = [
                r for r in self._requests
                if r.get("duration_ms", 0) > threshold_ms
            ]
            slow_requests.sort(key=lambda x: x.get("duration_ms", 0), reverse=True)
            return slow_requests[:limit]
        except Exception as e:
            logger.error(f"Failed to get slow requests: {e}")
            return []
    
    def disable(self):
        """Disable request tracking"""
        self._enabled = False
        logger.warning("Request tracking disabled")
    
    def enable(self):
        """Enable request tracking"""
        self._enabled = True
        logger.info("Request tracking enabled")


# Global instance
request_tracker = RequestTracker()


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track all requests with unique IDs
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Start tracking
        request_tracker.start_request(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=client_ip
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # End tracking
            response_size = response.headers.get("content-length")
            request_tracker.end_request(
                request_id=request_id,
                status_code=response.status_code,
                response_size=int(response_size) if response_size else None
            )
            
            return response
        
        except Exception as e:
            # End tracking with error
            request_tracker.end_request(
                request_id=request_id,
                status_code=500
            )
            raise e


# Export for easy import
__all__ = ["RequestTrackingMiddleware", "request_tracker"]
