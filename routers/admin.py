"""
Admin router.
Handles admin-specific operations like dashboard stats and player management.
"""
from fastapi import APIRouter, HTTPException, Depends, Form
from typing import Dict, Any
from bson import ObjectId
from datetime import datetime, timezone

from database import db
from core.security import require_admin
from schemas.player import SetBasePriceRequest
from websocket.manager import manager

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(require_admin)):
    """Get dashboard statistics for admin - optimized with aggregation."""
    # Get current auction round
    config = db.config.find_one({"key": "auction"}) or {}
    current_round = config.get("auction_round", 1)
    
    # Use aggregation pipeline for efficient stats calculation
    pipeline = [
        {
            "$facet": {
                "status_stats": [
                    {"$group": {
                        "_id": "$status",
                        "count": {"$sum": 1}
                    }}
                ],
                "round_stats": [
                    {"$match": {"auction_round": current_round}},
                    {"$group": {
                        "_id": "$status",
                        "count": {"$sum": 1}
                    }}
                ],
                "role_stats": [
                    {"$group": {
                        "_id": {"role": "$role", "status": "$status"},
                        "count": {"$sum": 1}
                    }}
                ],
                "revenue": [
                    {"$match": {"status": "sold"}},
                    {"$group": {
                        "_id": None,
                        "total": {"$sum": "$final_bid"}
                    }}
                ],
                "total_count": [
                    {"$count": "count"}
                ]
            }
        }
    ]
    
    result = list(db.players.aggregate(pipeline))[0]
    
    # Parse status stats
    status_counts = {item["_id"]: item["count"] for item in result["status_stats"]}
    total_players = result["total_count"][0]["count"] if result["total_count"] else 0
    sold_players = status_counts.get("sold", 0)
    unsold_players = status_counts.get("unsold", 0)
    available_players = status_counts.get("available", 0)
    in_auction_players = status_counts.get("in_auction", 0)
    
    # Parse round stats
    round_counts = {item["_id"]: item["count"] for item in result["round_stats"]}
    current_round_sold = round_counts.get("sold", 0)
    current_round_unsold = round_counts.get("unsold", 0)
    current_round_available = round_counts.get("available", 0)
    current_round_players = sum(round_counts.values())
    
    # Parse role stats
    role_stats = {}
    for role in ["Batsman", "Bowler", "All-Rounder", "Wicketkeeper"]:
        role_stats[role] = {"total": 0, "sold": 0, "unsold": 0}
    
    for item in result["role_stats"]:
        role = item["_id"]["role"]
        status = item["_id"]["status"]
        count = item["count"]
        if role in role_stats:
            role_stats[role]["total"] += count
            if status == "sold":
                role_stats[role]["sold"] = count
            elif status == "unsold":
                role_stats[role]["unsold"] = count
    
    # Get revenue
    total_revenue = result["revenue"][0]["total"] if result["revenue"] else 0
    
    # Get other counts (these are fast)
    total_teams = db.teams.count_documents({})
    total_bids = db.bid_history.count_documents({})
    
    return {
        "total_players": total_players,
        "sold_players": sold_players,
        "unsold_players": unsold_players,
        "available_players": available_players,
        "in_auction_players": in_auction_players,
        "total_teams": total_teams,
        "total_revenue": total_revenue,
        "total_bids": total_bids,
        "current_round": current_round,
        "current_round_stats": {
            "total": current_round_players,
            "sold": current_round_sold,
            "unsold": current_round_unsold,
            "available": current_round_available
        },
        "role_stats": role_stats
    }


@router.get("/dashboard/revenue_by_category")
async def get_revenue_by_category(current_user: dict = Depends(require_admin)):
    """Get revenue breakdown by player category."""
    pipeline = [
        {"$match": {"status": "sold"}},
        {
            "$group": {
                "_id": "$category",
                "total_revenue": {"$sum": "$final_bid"},
                "count": {"$sum": 1}
            }
        }
    ]
    
    results = list(db.players.aggregate(pipeline))
    
    return {
        "categories": [
            {
                "category": r["_id"] or "Uncategorized",
                "revenue": r["total_revenue"],
                "count": r["count"]
            }
            for r in results
        ]
    }


@router.get("/dashboard/team_spending")
async def get_team_spending(current_user: dict = Depends(require_admin)):
    """Get spending breakdown by team - optimized with aggregation."""
    # Use aggregation to calculate spending per team
    pipeline = [
        {"$match": {"status": "sold", "final_team": {"$exists": True, "$ne": None}}},
        {
            "$group": {
                "_id": "$final_team",
                "total_spent": {"$sum": "$final_bid"},
                "players_count": {"$sum": 1}
            }
        }
    ]
    
    spending_by_team = {item["_id"]: item for item in db.players.aggregate(pipeline)}
    
    # Get all teams
    teams = list(db.teams.find({}, {"_id": 1, "name": 1, "budget": 1}))
    
    team_data = []
    for team in teams:
        team_id = str(team["_id"])
        spending = spending_by_team.get(team_id, {"total_spent": 0, "players_count": 0})
        
        team_data.append({
            "team_id": team_id,
            "team_name": team.get("name"),
            "total_spent": spending["total_spent"],
            "remaining_budget": team.get("budget", 0),
            "players_count": spending["players_count"]
        })
    
    return {"teams": team_data}


@router.get("/players/pending")
async def get_pending_players(current_user: dict = Depends(require_admin)):
    """Get players with pending base price (excludes sold players)."""
    players = list(db.players.find({
        "base_price_status": "pending",
        "status": {"$ne": "sold"}  # Exclude sold players
    }))
    
    for p in players:
        p["_id"] = str(p["_id"])
    
    return {"ok": True, "players": players}


@router.patch("/player/{player_id}/base-price")
async def set_base_price(
    player_id: str,
    body: SetBasePriceRequest,
    current_user: dict = Depends(require_admin)
):
    """Set base price for a player."""
    try:
        pid = ObjectId(player_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid player ID")
    
    result = db.players.update_one(
        {"_id": pid},
        {
            "$set": {
                "base_price": body.price,
                "base_price_status": "set",
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return {"ok": True, "player_id": player_id, "base_price": body.price}


@router.post("/user/{user_id}/assign-team")
async def assign_user_to_team(
    user_id: str,
    team_id: str,
    current_user: dict = Depends(require_admin)
):
    """Assign a user to a team."""
    try:
        uid = ObjectId(user_id)
        tid = ObjectId(team_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Verify team exists
    team = db.teams.find_one({"_id": tid})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Update user
    result = db.users.update_one(
        {"_id": uid},
        {
            "$set": {
                "team_id": tid,
                "role": "team_member",
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"ok": True, "message": "User assigned to team"}


@router.get("/activity-logs")
async def get_activity_logs(
    limit: int = 100,
    current_user: dict = Depends(require_admin)
):
    """Get recent activity logs."""
    # Get recent bids
    bids = list(db.bid_history.find().sort("timestamp", -1).limit(limit))
    
    logs = []
    for bid in bids:
        player = db.players.find_one({"_id": ObjectId(bid["player_id"])})
        team = db.teams.find_one({"_id": ObjectId(bid["team_id"])})
        
        logs.append({
            "type": "bid",
            "timestamp": bid["timestamp"],
            "player_name": player.get("name") if player else "Unknown",
            "team_name": team.get("name") if team else "Unknown",
            "amount": bid["bid_amount"],
            "is_winning": bid.get("is_winning", False)
        })
    
    return {"logs": logs}


@router.post("/change-password")
async def change_admin_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    current_user: dict = Depends(require_admin)
):
    """Change admin password."""
    from core.security import verify_password, hash_password
    
    # Get current user
    user = db.users.find_one({"_id": ObjectId(current_user["user_id"])})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not verify_password(current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    
    # Update password
    db.users.update_one(
        {"_id": ObjectId(current_user["user_id"])},
        {
            "$set": {
                "password_hash": hash_password(new_password),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    return {"ok": True, "message": "Password changed successfully"}


# ============================================================
# PLAYER APPROVAL SYSTEM
# ============================================================

@router.get("/players/pending-approval")
async def get_pending_players(current_user: dict = Depends(require_admin)):
    """Get all players pending approval."""
    try:
        players = list(db.players.find({"is_approved": False}).sort("created_at", -1))
        
        for p in players:
            p["_id"] = str(p["_id"])
        
        return {
            "ok": True,
            "count": len(players),
            "players": players
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/players/{player_id}/approve")
async def approve_player(
    player_id: str,
    current_user: dict = Depends(require_admin)
):
    """Approve a player registration."""
    try:
        pid = ObjectId(player_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid player ID")
    
    # Check if player exists
    player = db.players.find_one({"_id": pid})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if player.get("is_approved"):
        raise HTTPException(status_code=400, detail="Player already approved")
    
    # Approve player
    result = db.players.update_one(
        {"_id": pid},
        {
            "$set": {
                "is_approved": True,
                "approval_date": datetime.now(timezone.utc),
                "approved_by": current_user.get("email")
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to approve player")
    
    return {
        "ok": True,
        "message": f"Player '{player.get('name')}' approved successfully"
    }


@router.post("/players/{player_id}/reject")
async def reject_player(
    player_id: str,
    current_user: dict = Depends(require_admin)
):
    """Reject a player registration (mark as rejected, don't delete)."""
    try:
        pid = ObjectId(player_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid player ID")
    
    # Check if player exists
    player = db.players.find_one({"_id": pid})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Mark as rejected instead of deleting
    result = db.players.update_one(
        {"_id": pid},
        {
            "$set": {
                "is_approved": False,
                "is_rejected": True,
                "rejection_date": datetime.now(timezone.utc),
                "rejected_by": current_user.get("email")
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to reject player")
    
    return {
        "ok": True,
        "message": f"Player '{player.get('name')}' rejected"
    }


# ============================================================
# LIVE AUCTION CONTROLLER
# ============================================================

@router.get("/auction/live-player")
async def get_live_player(current_user: dict = Depends(require_admin)):
    """Get currently live player in auction."""
    try:
        live_player = db.players.find_one({"is_live": True})
        
        if not live_player:
            return {"ok": True, "live_player": None}
        
        live_player["_id"] = str(live_player["_id"])
        
        return {
            "ok": True,
            "live_player": live_player
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auction/set-live-player/{player_id}")
async def set_live_player(
    player_id: str,
    current_user: dict = Depends(require_admin)
):
    """Set a player as live in auction (admin only)."""
    try:
        pid = ObjectId(player_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid player ID")
    
    # Check if player exists and is eligible
    player = db.players.find_one({"_id": pid})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Validation checks
    if not player.get("is_approved", False):
        raise HTTPException(status_code=400, detail="Player not approved yet")
    
    if player.get("status") == "sold":
        raise HTTPException(status_code=400, detail="Player already sold")
    
    if player.get("is_live"):
        raise HTTPException(status_code=400, detail="Player already live")
    
    # Check if another player is already live
    current_live = db.players.find_one({"is_live": True})
    if current_live:
        raise HTTPException(
            status_code=400,
            detail=f"Player '{current_live.get('name')}' is already live. End current auction first."
        )
    
    # Set player as live
    result = db.players.update_one(
        {"_id": pid},
        {
            "$set": {
                "is_live": True,
                "status": "in_auction",
                "live_start_time": datetime.now(timezone.utc)
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to set player live")
    
    # Update auction config with current player
    db.config.update_one(
        {"key": "auction"},
        {
            "$set": {
                "current_player_id": str(pid),
                "current_player_name": player.get("name")
            }
        },
        upsert=True
    )
    
    # Broadcast player live event to all clients
    await manager.broadcast({
        "type": "player_live",
        "data": {
            "player_id": str(pid),
            "player_name": player.get("name"),
            "base_price": player.get("base_price", 0),
            "role": player.get("role"),
            "category": player.get("category")
        }
    })
    
    # Define callback to auto-close auction when timer expires
    async def auto_close_auction():
        """Automatically close the auction when timer reaches 0."""
        try:
            # Get the current live player
            live_player = db.players.find_one({"is_live": True})
            if not live_player:
                return
            
            # Determine final status
            if live_player.get("final_bid") and live_player.get("final_bid") > 0:
                final_status = "sold"
                
                # Update player as sold
                db.players.update_one(
                    {"_id": live_player["_id"]},
                    {
                        "$set": {
                            "is_live": False,
                            "status": "sold",
                            "live_end_time": datetime.now(timezone.utc)
                        }
                    }
                )
                
                # Get team name
                team_name = None
                if live_player.get("final_team"):
                    team = db.teams.find_one({"_id": ObjectId(live_player.get("final_team"))})
                    if team:
                        team_name = team.get("name")
                        
                        # Update team's total spent and players count
                        db.teams.update_one(
                            {"_id": team["_id"]},
                            {
                                "$inc": {
                                    "total_spent": live_player.get("final_bid", 0),
                                    "players_count": 1
                                },
                                "$set": {
                                    "remaining_budget": team.get("budget", 0)
                                }
                            }
                        )
                
                # Broadcast player sold
                await manager.broadcast({
                    "type": "player_sold",
                    "data": {
                        "player_id": str(live_player["_id"]),
                        "player_name": live_player.get("name"),
                        "final_bid": live_player.get("final_bid"),
                        "team_id": live_player.get("final_team"),
                        "team_name": team_name,
                        "auto_closed": True
                    }
                })
            else:
                # No bids - mark as unsold
                db.players.update_one(
                    {"_id": live_player["_id"]},
                    {
                        "$set": {
                            "is_live": False,
                            "status": "unsold",
                            "live_end_time": datetime.now(timezone.utc)
                        }
                    }
                )
                
                # Broadcast player unsold
                await manager.broadcast({
                    "type": "player_unsold",
                    "data": {
                        "player_id": str(live_player["_id"]),
                        "player_name": live_player.get("name"),
                        "auto_closed": True
                    }
                })
            
            # Clear current player from auction config
            db.config.update_one(
                {"key": "auction"},
                {
                    "$set": {
                        "current_player_id": None,
                        "current_player_name": None
                    }
                }
            )
            
        except Exception as e:
            print(f"Error in auto-close auction: {e}")
    
    # Start auction timer with auto-close callback
    await manager.start_timer(30, on_complete_callback=auto_close_auction)
    
    return {
        "ok": True,
        "message": f"Player '{player.get('name')}' is now live in auction",
        "player_id": str(pid),
        "player_name": player.get("name")
    }


@router.post("/auction/end-live-player/{player_id}")
async def end_live_player(
    player_id: str,
    current_user: dict = Depends(require_admin)
):
    """End live auction for a player (admin only)."""
    try:
        pid = ObjectId(player_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid player ID")
    
    # Check if player exists
    player = db.players.find_one({"_id": pid})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if not player.get("is_live"):
        raise HTTPException(status_code=400, detail="Player is not live")
    
    # Determine final status based on bids
    final_status = "available"
    if player.get("final_bid") and player.get("final_bid") > 0:
        final_status = "sold"
    else:
        final_status = "unsold"
    
    # End live auction
    result = db.players.update_one(
        {"_id": pid},
        {
            "$set": {
                "is_live": False,
                "status": final_status,
                "live_end_time": datetime.now(timezone.utc)
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to end live auction")
    
    # Clear current player from auction config
    db.config.update_one(
        {"key": "auction"},
        {
            "$set": {
                "current_player_id": None,
                "current_player_name": None
            }
        }
    )
    
    # Get team name if sold
    team_name = None
    if final_status == "sold" and player.get("final_team"):
        team = db.teams.find_one({"_id": ObjectId(player.get("final_team"))})
        if team:
            team_name = team.get("name")
    
    # Broadcast player sold/unsold event to all clients
    if final_status == "sold":
        await manager.broadcast({
            "type": "player_sold",
            "data": {
                "player_id": str(pid),
                "player_name": player.get("name"),
                "final_bid": player.get("final_bid"),
                "team_id": player.get("final_team"),
                "team_name": team_name
            }
        })
    else:
        await manager.broadcast({
            "type": "player_unsold",
            "data": {
                "player_id": str(pid),
                "player_name": player.get("name")
            }
        })
    
    # Stop auction timer
    manager.stop_timer()
    await manager.broadcast_timer(0)
    
    return {
        "ok": True,
        "message": f"Live auction ended for '{player.get('name')}'",
        "final_status": final_status
    }


@router.get("/auction/eligible-players")
async def get_eligible_players(current_user: dict = Depends(require_admin)):
    """Get players eligible to be set live (approved, not sold, not currently live)."""
    try:
        players = list(db.players.find({
            "is_approved": True,
            "is_live": False,
            "status": {"$in": ["available", "unsold"]}
        }).sort("name", 1))
        
        for p in players:
            p["_id"] = str(p["_id"])
        
        return {
            "ok": True,
            "count": len(players),
            "players": players
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

