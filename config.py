import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the NFL Prediction API"""
    
    # Tank01 API Configuration (via RapidAPI)
    TANK01_API_KEY = os.getenv("TANK01_API_KEY")  # This should be your RapidAPI key
    TANK01_BASE_URL = os.getenv("TANK01_BASE_URL", "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Prediction Model Configuration
    MODEL_CONFIDENCE_THRESHOLD = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.6"))
    
    # Tank01 RapidAPI Endpoints
    TANK01_ENDPOINTS = {
        "nfl_games_for_week": "/getNFLGamesForWeek",
        "nfl_teams": "/getNFLTeams",
        "nfl_standings": "/getNFLStandings"
    }
    
    # NFL Season Configuration
    NFL_SEASON_START = "2025-09-04"  # Approximate start date for 2025 season
    NFL_REGULAR_SEASON_WEEKS = 18
    NFL_PLAYOFF_WEEKS = 4
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.TANK01_API_KEY:
            print("Warning: TANK01_API_KEY not set. API will use mock data.")
            print("To get real data, set TANK01_API_KEY to your RapidAPI key")
            return False
        return True
    
    @classmethod
    def get_tank01_url(cls, endpoint: str, **kwargs) -> str:
        """Get full Tank01 API URL for an endpoint"""
        endpoint_path = cls.TANK01_ENDPOINTS.get(endpoint, endpoint)
        if kwargs:
            endpoint_path = endpoint_path.format(**kwargs)
        return f"{cls.TANK01_BASE_URL}{endpoint_path}"
    
    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get headers for Tank01 API requests"""
        if cls.TANK01_API_KEY:
            return {
                "X-RapidAPI-Key": cls.TANK01_API_KEY,
                "X-RapidAPI-Host": "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com",
                "User-Agent": "NFL-Prediction-API/1.0"
            }
        return {
            "User-Agent": "NFL-Prediction-API/1.0"
        }
