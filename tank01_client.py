import requests
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Tank01Client:
    """Client for interacting with Tank01 NFL API via RapidAPI"""
    
    def __init__(self, api_key: str, base_url: str = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com",
            "User-Agent": "NFL-Data-API/1.0"
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
        # Cache for API responses
        self.cache = {}
        self._update_weekly_cache_ttl()
    
    def _get_next_tuesday(self) -> datetime:
        """Get the next Tuesday at 12:00 AM"""
        today = datetime.now()
        days_ahead = 1 - today.weekday()  # Tuesday is 1, Monday is 0
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        next_tuesday = today + timedelta(days=days_ahead)
        return next_tuesday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def _update_weekly_cache_ttl(self):
        """Update cache TTL to expire on next Tuesday"""
        next_tuesday = self._get_next_tuesday()
        now = datetime.now()
        seconds_until_tuesday = (next_tuesday - now).total_seconds()
        self.cache_ttl = max(seconds_until_tuesday, 3600)  # Minimum 1 hour cache
        logger.info(f"Cache TTL set to expire on {next_tuesday.strftime('%Y-%m-%d %H:%M')} ({self.cache_ttl:.0f} seconds)")
        logger.info(f"Current cache duration: {self.cache_ttl/3600:.1f} hours")
    
    def _rate_limit(self):
        """Implement basic rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a rate-limited request to the Tank01 API"""
        self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            raise
    
    def _get_cached_data(self, key: str) -> Optional[Dict]:
        """Get cached data if still valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            
            if time.time() - timestamp < self.cache_ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def _cache_data(self, key: str, data: Dict):
        """Cache data with timestamp"""
        self.cache[key] = (data, time.time())
    
    def get_games_for_week(self, week: int, season: int = 2025, season_type: str = "reg") -> List[Dict]:
        """Get all games for a specific week using the Tank01 API"""
        cache_key = f"games_week_{week}_season_{season}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            if self.api_key:
                params = {
                    "week": week,
                    "seasonType": season_type,
                    "season": season
                }
                data = self._make_request("/getNFLGamesForWeek", params)
                games = self._parse_schedule_data(data)
                if games:
                    self._cache_data(cache_key, games)
                    return games
        except Exception as e:
            logger.warning(f"Failed to fetch from Tank01 API: {e}")
        
        logger.warning(f"No games data available for week {week}, season {season}")
        return []
    
    def get_current_week_games(self) -> List[Dict]:
        """Get all games for the current week"""
        # For now, default to week 1 of 2025 season since it's preseason
        # In a real app, you'd calculate the current NFL week based on date
        return self.get_games_for_week(1, 2025, "reg")
    
    def get_available_weeks(self, season: int = 2025) -> List[int]:
        """Get list of available weeks for a season"""
        # NFL regular season is typically weeks 1-18
        # You could also query the Tank01 API to see what weeks have data
        return list(range(1, 19))
    
    def get_betting_odds(self, game_id: str) -> Dict:
        """Get betting odds for a specific game"""
        cache_key = f"betting_odds_{game_id}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            if self.api_key:
                params = {
                    "gameID": game_id,
                    "itemFormat": "map",
                    "impliedTotals": "true"
                }
                data = self._make_request("/getNFLBettingOdds", params)
                odds = self._parse_betting_odds_data(data, game_id)
                if odds:
                    self._cache_data(cache_key, odds)
                    return odds
        except Exception as e:
            logger.warning(f"Failed to fetch betting odds from Tank01 API: {e}")
        
        logger.warning(f"No betting odds available for game {game_id}")
        return {}
    
    def _parse_schedule_data(self, data: Dict) -> List[Dict]:
        """Parse schedule data from Tank01 API response"""
        try:
            games = []
            
            # Handle different possible response formats
            if "body" in data and isinstance(data["body"], list):
                games_data = data["body"]
            elif isinstance(data, list):
                games_data = data
            else:
                logger.warning(f"Unexpected API response format: {data.keys()}")
                return []
            
            for game in games_data:
                try:
                    # Extract game information
                    game_id = game.get("gameID", "")
                    away_team = game.get("away", "")
                    home_team = game.get("home", "")
                    
                    # Parse the week number from "Week 1" format
                    week_str = game.get("gameWeek", "Week 1")
                    week = int(week_str.replace("Week ", "")) if "Week " in week_str else 1
                    
                    # Parse the season from string to int
                    season = int(game.get("season", "2025"))
                    
                    # Convert game time to proper format
                    game_time = self._format_game_time(game.get("gameTime", ""), game.get("gameDate", ""))
                    
                    game_info = {
                        "game_id": game_id,
                        "away_team": self._get_full_team_name(away_team),
                        "home_team": self._get_full_team_name(home_team),
                        "away_abbreviation": away_team,
                        "home_abbreviation": home_team,
                        "game_time": game_time,
                        "week": week,
                        "season": season,
                        "status": game.get("gameStatus", "Scheduled").lower(),
                        "game_date": game.get("gameDate", ""),
                        "espn_id": game.get("espnID", ""),
                        "neutral_site": game.get("neutralSite", "False") == "True",
                        "venue": self._get_venue_name(home_team, game.get("neutralSite", "False") == "True")
                    }
                    games.append(game_info)
                except Exception as e:
                    logger.error(f"Error parsing individual game: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(games)} games from API response")
            return games
            
        except Exception as e:
            logger.error(f"Error parsing schedule data: {e}")
            logger.error(f"Raw response: {data}")
            return []
    
    def _parse_betting_odds_data(self, data: Dict, game_id: str) -> Dict:
        """Parse betting odds data from Tank01 API response"""
        try:
            if "body" not in data or game_id not in data["body"]:
                logger.warning(f"Game {game_id} not found in betting odds response")
                return {}
            
            game_odds = data["body"][game_id]
            
            # Extract key betting information
            odds_data = {
                "game_id": game_id,
                "last_updated": game_odds.get("last_updated_e_time", ""),
                "game_date": game_odds.get("gameDate", ""),
                "away_team": game_odds.get("awayTeam", ""),
                "home_team": game_odds.get("homeTeam", ""),
                "sportsbooks": {}
            }
            
            # Process each sportsbook
            sportsbooks = ["betmgm", "bet365", "fanduel", "ballybet", "espnbet", "betrivers", "caesars_sportsbook", "draftkings"]
            
            for book in sportsbooks:
                if book in game_odds:
                    book_data = game_odds[book]
                    odds_data["sportsbooks"][book] = {
                        "spread": {
                            "away": book_data.get("awayTeamSpread", ""),
                            "home": book_data.get("homeTeamSpread", ""),
                            "away_odds": book_data.get("awayTeamSpreadOdds", ""),
                            "home_odds": book_data.get("homeTeamSpreadOdds", "")
                        },
                        "total": {
                            "over": book_data.get("totalOver", ""),
                            "under": book_data.get("totalUnder", ""),
                            "over_odds": book_data.get("totalOverOdds", ""),
                            "under_odds": book_data.get("totalUnderOdds", "")
                        },
                        "moneyline": {
                            "away": book_data.get("awayTeamMLOdds", ""),
                            "home": book_data.get("homeTeamMLOdds", "")
                        },
                        "implied_totals": book_data.get("impliedTotals", {})
                    }
            
            return odds_data
            
        except Exception as e:
            logger.error(f"Error parsing betting odds data: {e}")
            return {}
    
    def _get_full_team_name(self, abbreviation: str) -> str:
        """Convert team abbreviation to full team name"""
        team_names = {
            "ARI": "Arizona Cardinals",
            "ATL": "Atlanta Falcons", 
            "BAL": "Baltimore Ravens",
            "BUF": "Buffalo Bills",
            "CAR": "Carolina Panthers",
            "CHI": "Chicago Bears",
            "CIN": "Cincinnati Bengals",
            "CLE": "Cleveland Browns",
            "DAL": "Dallas Cowboys",
            "DEN": "Denver Broncos",
            "DET": "Detroit Lions",
            "GB": "Green Bay Packers",
            "HOU": "Houston Texans",
            "IND": "Indianapolis Colts",
            "JAX": "Jacksonville Jaguars",
            "KC": "Kansas City Chiefs",
            "LAC": "Los Angeles Chargers",
            "LAR": "Los Angeles Rams",
            "LV": "Las Vegas Raiders",
            "MIA": "Miami Dolphins",
            "MIN": "Minnesota Vikings",
            "NE": "New England Patriots",
            "NO": "New Orleans Saints",
            "NYG": "New York Giants",
            "NYJ": "New York Jets",
            "PHI": "Philadelphia Eagles",
            "PIT": "Pittsburgh Steelers",
            "SEA": "Seattle Seahawks",
            "SF": "San Francisco 49ers",
            "TB": "Tampa Bay Buccaneers",
            "TEN": "Tennessee Titans",
            "WSH": "Washington Commanders"
        }
        return team_names.get(abbreviation, abbreviation)
    
    def _get_venue_name(self, home_team: str, neutral_site: bool) -> str:
        """Get venue name for a game"""
        if neutral_site:
            return "Neutral Site"
        
        # Map team abbreviations to their home stadiums
        stadiums = {
            "ARI": "State Farm Stadium",
            "ATL": "Mercedes-Benz Stadium", 
            "BAL": "M&T Bank Stadium",
            "BUF": "Highmark Stadium",
            "CAR": "Bank of America Stadium",
            "CHI": "Soldier Field",
            "CIN": "Paycor Stadium",
            "CLE": "Cleveland Browns Stadium",
            "DAL": "AT&T Stadium",
            "DEN": "Empower Field at Mile High",
            "DET": "Ford Field",
            "GB": "Lambeau Field",
            "HOU": "NRG Stadium",
            "IND": "Lucas Oil Stadium",
            "JAX": "EverBank Stadium",
            "KC": "Arrowhead Stadium",
            "LAC": "SoFi Stadium",
            "LAR": "SoFi Stadium",
            "LV": "Allegiant Stadium",
            "MIA": "Hard Rock Stadium",
            "MIN": "U.S. Bank Stadium",
            "NE": "Gillette Stadium",
            "NO": "Caesars Superdome",
            "NYG": "MetLife Stadium",
            "NYJ": "MetLife Stadium",
            "PHI": "Lincoln Financial Field",
            "PIT": "Acrisure Stadium",
            "SEA": "Lumen Field",
            "SF": "Levi's Stadium",
            "TB": "Raymond James Stadium",
            "TEN": "Nissan Stadium",
            "WSH": "FedExField"
        }
        
        return stadiums.get(home_team, "Unknown Stadium")
    
    def _format_game_time(self, time_str: str, date_str: str) -> str:
        """Format game time from Tank01 API format to ISO format"""
        try:
            # Tank01 API returns time like "8:20p" and date like "20250904"
            if not time_str or not date_str:
                return "2025-01-01T00:00:00Z"
            
            # Parse date (YYYYMMDD format)
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            
            # Parse time (H:MMa/p format)
            if ":" in time_str:
                time_part, ampm = time_str.split(":")
                hour = int(time_part)
                minute = int(ampm[:-1])
                period = ampm[-1].lower()
                
                # Convert to 24-hour format
                if period == "p" and hour != 12:
                    hour += 12
                elif period == "a" and hour == 12:
                    hour = 0
                
                # Format as ISO string (assuming Eastern time)
                return f"{year}-{month}-{day}T{hour:02d}:{minute:02d}:00-04:00"
            else:
                return f"{year}-{month}-{day}T00:00:00-04:00"
        except Exception as e:
            logger.error(f"Error formatting game time: {e}")
            return "2025-01-01T00:00:00Z"
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def refresh_cache_ttl(self):
        """Manually refresh the cache TTL (useful for debugging)"""
        old_ttl = self.cache_ttl
        self._update_weekly_cache_ttl()
        logger.info(f"Cache TTL refreshed: {old_ttl/3600:.1f}h -> {self.cache_ttl/3600:.1f}h")
    

    
    def get_cache_info(self) -> Dict:
        """Get information about cached data"""
        next_tuesday = self._get_next_tuesday()
        cache_info = {
            "total_items": len(self.cache),
            "cache_ttl": self.cache_ttl,
            "cache_ttl_hours": round(self.cache_ttl / 3600, 1),
            "next_refresh": next_tuesday.strftime("%Y-%m-%d %H:%M"),
            "cached_keys": list(self.cache.keys())
        }
        return cache_info
