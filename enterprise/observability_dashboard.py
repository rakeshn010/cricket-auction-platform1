"""
Health Check & Observability Dashboard
Comprehensive system health monitoring
"""
import logging
import platform
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/enterprise", tags=["Enterprise"])


@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        from enterprise.event_manager import event_manager
        from enterprise.analytics_engine import analytics_engine
        from enterprise.audit_logger import audit_logger
        from enterprise.request_tracker import request_tracker
        from enterprise.bid_manipulation_detector import bid_detector
        from enterprise.redis_cache import cache_layer
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "event_manager": "healthy" if event_manager._enabled else "disabled",
                "analytics_engine": "healthy" if analytics_engine._enabled else "disabled",
                "audit_logger": "healthy" if audit_logger._enabled else "disabled",
                "request_tracker": "healthy" if request_tracker._enabled else "disabled",
                "bid_detector": "healthy" if bid_detector._enabled else "disabled",
                "cache_layer": "healthy" if cache_layer._enabled else "disabled"
            }
        }
        
        return JSONResponse(content=health_status)
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=500
        )


@router.get("/metrics")
async def system_metrics():
    """Get system metrics"""
    try:
        # Try to import psutil, but don't fail if unavailable
        try:
            import psutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                network_stats = {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            except:
                network_stats = {}
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "platform": platform.system(),
                    "platform_release": platform.release(),
                    "platform_version": platform.version(),
                    "architecture": platform.machine(),
                    "processor": platform.processor()
                },
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "network": network_stats
            }
        
        except ImportError:
            # psutil not available, return basic info
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "platform": platform.system(),
                    "platform_release": platform.release(),
                    "architecture": platform.machine()
                },
                "message": "psutil not available - limited metrics"
            }
    
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@router.get("/stats")
async def enterprise_stats():
    """Get all enterprise module statistics"""
    try:
        from enterprise.event_manager import event_manager
        from enterprise.analytics_engine import analytics_engine
        from enterprise.audit_logger import audit_logger
        from enterprise.request_tracker import request_tracker
        from enterprise.bid_manipulation_detector import bid_detector
        from enterprise.redis_cache import cache_layer
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "event_manager": event_manager.get_stats(),
            "analytics_engine": analytics_engine.get_auction_summary(),
            "audit_logger": audit_logger.get_stats(),
            "request_tracker": request_tracker.get_stats(),
            "bid_detector": bid_detector.get_stats(),
            "cache_layer": cache_layer.get_stats()
        }
    
    except Exception as e:
        logger.error(f"Failed to get enterprise stats: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@router.get("/dashboard", response_class=HTMLResponse)
async def observability_dashboard(request: Request):
    """Observability dashboard UI"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enterprise Observability Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0f172a;
                color: #e2e8f0;
                padding: 20px;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            h1 {
                font-size: 2rem;
                margin-bottom: 2rem;
                color: #fbbf24;
                text-align: center;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .card {
                background: #1e293b;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #334155;
            }
            .card h2 {
                font-size: 1.2rem;
                margin-bottom: 15px;
                color: #fbbf24;
            }
            .metric {
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #334155;
            }
            .metric:last-child { border-bottom: none; }
            .metric-label { color: #94a3b8; }
            .metric-value {
                font-weight: 600;
                color: #10b981;
            }
            .status-healthy { color: #10b981; }
            .status-warning { color: #f59e0b; }
            .status-error { color: #ef4444; }
            .refresh-btn {
                background: #fbbf24;
                color: #000;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                margin: 20px auto;
                display: block;
            }
            .refresh-btn:hover { background: #f59e0b; }
            .timestamp {
                text-align: center;
                color: #64748b;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Enterprise Observability Dashboard</h1>
            
            <div class="grid">
                <div class="card">
                    <h2>System Health</h2>
                    <div id="health-status">Loading...</div>
                </div>
                
                <div class="card">
                    <h2>System Metrics</h2>
                    <div id="system-metrics">Loading...</div>
                </div>
                
                <div class="card">
                    <h2>Request Tracker</h2>
                    <div id="request-stats">Loading...</div>
                </div>
                
                <div class="card">
                    <h2>Analytics Engine</h2>
                    <div id="analytics-stats">Loading...</div>
                </div>
                
                <div class="card">
                    <h2>Audit Logger</h2>
                    <div id="audit-stats">Loading...</div>
                </div>
                
                <div class="card">
                    <h2>Bid Detector</h2>
                    <div id="bid-detector-stats">Loading...</div>
                </div>
            </div>
            
            <button class="refresh-btn" onclick="loadAllData()">🔄 Refresh Data</button>
            <div class="timestamp" id="last-updated"></div>
        </div>
        
        <script>
            async function loadAllData() {
                try {
                    // Load health status
                    const health = await fetch('/enterprise/health').then(r => r.json());
                    displayHealth(health);
                    
                    // Load system metrics
                    const metrics = await fetch('/enterprise/metrics').then(r => r.json());
                    displayMetrics(metrics);
                    
                    // Load enterprise stats
                    const stats = await fetch('/enterprise/stats').then(r => r.json());
                    displayStats(stats);
                    
                    document.getElementById('last-updated').textContent = 
                        'Last updated: ' + new Date().toLocaleString();
                } catch (error) {
                    console.error('Failed to load data:', error);
                }
            }
            
            function displayHealth(health) {
                const html = Object.entries(health.components).map(([key, value]) => {
                    const statusClass = value === 'healthy' ? 'status-healthy' : 'status-warning';
                    return `<div class="metric">
                        <span class="metric-label">${key}</span>
                        <span class="metric-value ${statusClass}">${value}</span>
                    </div>`;
                }).join('');
                document.getElementById('health-status').innerHTML = html;
            }
            
            function displayMetrics(metrics) {
                const html = `
                    <div class="metric">
                        <span class="metric-label">CPU Usage</span>
                        <span class="metric-value">${metrics.cpu.percent.toFixed(1)}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Memory Usage</span>
                        <span class="metric-value">${metrics.memory.percent.toFixed(1)}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Disk Usage</span>
                        <span class="metric-value">${metrics.disk.percent.toFixed(1)}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Platform</span>
                        <span class="metric-value">${metrics.system.platform}</span>
                    </div>
                `;
                document.getElementById('system-metrics').innerHTML = html;
            }
            
            function displayStats(stats) {
                // Request tracker
                const reqStats = stats.request_tracker;
                document.getElementById('request-stats').innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Total Requests</span>
                        <span class="metric-value">${reqStats.total_requests || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Active Requests</span>
                        <span class="metric-value">${reqStats.active_requests || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Avg Duration</span>
                        <span class="metric-value">${(reqStats.avg_duration_ms || 0).toFixed(2)}ms</span>
                    </div>
                `;
                
                // Analytics
                const analyticsStats = stats.analytics_engine;
                document.getElementById('analytics-stats').innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Total Bids</span>
                        <span class="metric-value">${analyticsStats.total_bids || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Players Sold</span>
                        <span class="metric-value">${analyticsStats.players_sold || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Spent</span>
                        <span class="metric-value">₹${(analyticsStats.total_spent || 0).toLocaleString()}</span>
                    </div>
                `;
                
                // Audit logger
                const auditStats = stats.audit_logger;
                document.getElementById('audit-stats').innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Total Entries</span>
                        <span class="metric-value">${auditStats.total_entries || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Unique Users</span>
                        <span class="metric-value">${auditStats.unique_users || 0}</span>
                    </div>
                `;
                
                // Bid detector
                const bidStats = stats.bid_detector;
                document.getElementById('bid-detector-stats').innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Suspicious Activities</span>
                        <span class="metric-value">${bidStats.total_suspicious_activities || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Blocked Teams</span>
                        <span class="metric-value">${bidStats.blocked_teams || 0}</span>
                    </div>
                `;
            }
            
            // Load data on page load
            loadAllData();
            
            // Auto-refresh every 30 seconds
            setInterval(loadAllData, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# Export router
__all__ = ["router"]
