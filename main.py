from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Import our custom modules
from config import Config
from tank01_client import Tank01Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NFL Data API",
    description="API for fetching NFL game schedules, team statistics, and standings using Tank01 data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Authentication
security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the API key from the Authorization header"""
    if credentials.credentials != config.API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Pydantic models
class Game(BaseModel):
    game_id: str
    home_team: str
    away_team: str
    away_abbreviation: str
    home_abbreviation: str
    game_time: str
    week: int
    season: int
    status: Optional[str] = "scheduled"
    venue: Optional[str] = "Unknown"
    game_date: Optional[str] = ""
    espn_id: Optional[str] = ""
    neutral_site: Optional[bool] = False

class TeamStats(BaseModel):
    team: str
    stats: Dict[str, Any]

class Standings(BaseModel):
    AFC: Dict[str, List[str]]
    NFC: Dict[str, List[str]]

class CacheInfo(BaseModel):
    total_items: int
    cache_ttl: int
    cached_keys: List[str]

# Initialize configuration and clients
config = Config()
tank01_client = Tank01Client(config.TANK01_API_KEY, config.TANK01_BASE_URL)

# Validate configuration
config.validate_config()

# API endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NFL Data API",
        "version": "1.0.0",
                "endpoints": {
            "get_games_for_week": "/games/week/{week}",
            "get_current_week_games": "/games/current-week",
            "get_available_weeks": "/games/available-weeks",
            "get_betting_odds": "/odds/{game_id}",
            "cache_info": "/cache/info",
            "clear_cache": "/cache/clear",
            "health": "/health"
        },
        "config": {
            "tank01_api_configured": bool(config.TANK01_API_KEY),
            "using_mock_data": not bool(config.TANK01_API_KEY),
            "authentication_required": True
        },
        "data_sources": {
            "games": "Real-time NFL game schedules from Tank01 API",
            "betting_odds": "Live betting odds from multiple sportsbooks via Tank01 API"
        },
        "authentication": {
            "type": "Bearer Token",
            "header": "Authorization: Bearer YOUR_API_KEY"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint - no authentication required"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "tank01_api_status": "connected" if config.TANK01_API_KEY else "using_mock_data",
        "authentication_enabled": True
    }

@app.get("/games/week/{week}", response_model=List[Game])
async def get_games_for_week(
    week: int, 
    season: int = 2025, 
    season_type: str = "reg",
    api_key: str = Depends(verify_api_key)
):
    """Get all games for a specific week - requires API key"""
    try:
        # Validate week number (NFL regular season is weeks 1-18)
        if week < 1 or week > 18:
            raise HTTPException(status_code=400, detail="Week must be between 1 and 18")
        
        games = tank01_client.get_games_for_week(week, season, season_type)
        return [Game(**game) for game in games]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting games for week {week}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch games")

@app.get("/games/available-weeks")
async def get_available_weeks(
    season: int = 2025,
    api_key: str = Depends(verify_api_key)
):
    """Get list of available weeks for a season - requires API key"""
    try:
        weeks = tank01_client.get_available_weeks(season)
        return {
            "season": season,
            "available_weeks": weeks,
            "note": "NFL regular season typically runs weeks 1-18"
        }
    except Exception as e:
        logger.error(f"Error getting available weeks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch available weeks")

@app.get("/games/current-week", response_model=List[Game])
async def get_current_week_games(api_key: str = Depends(verify_api_key)):
    """Get all games for the current week - requires API key"""
    try:
        games = tank01_client.get_current_week_games()
        return [Game(**game) for game in games]
    except Exception as e:
        logger.error(f"Error getting current week games: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch games")







@app.get("/odds/{game_id}")
async def get_betting_odds(
    game_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get betting odds for a specific game - requires API key"""
    try:
        odds = tank01_client.get_betting_odds(game_id)
        return {
            "game_id": game_id,
            "odds": odds
        }
    except Exception as e:
        logger.error(f"Error fetching betting odds for game {game_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch betting odds")

@app.get("/cache/info", response_model=CacheInfo)
async def get_cache_info(api_key: str = Depends(verify_api_key)):
    """Get information about cached data - requires API key"""
    try:
        cache_info = tank01_client.get_cache_info()
        return CacheInfo(**cache_info)
    except Exception as e:
        logger.error(f"Error getting cache info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache info")

@app.post("/cache/clear")
async def clear_cache(api_key: str = Depends(verify_api_key)):
    """Clear all cached data - requires API key"""
    try:
        tank01_client.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

@app.get("/debug/config")
async def debug_config(api_key: str = Depends(verify_api_key)):
    """Debug endpoint to show current configuration - requires API key"""
    if not config.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "tank01_api_key_set": bool(config.TANK01_API_KEY),
        "tank01_base_url": config.TANK01_BASE_URL,
        "api_host": config.API_HOST,
        "api_port": config.API_PORT,
        "debug_mode": config.DEBUG,
        "api_secret_key_configured": bool(config.API_SECRET_KEY)
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=config.API_HOST, 
        port=config.API_PORT,
        log_level="info"
    )
