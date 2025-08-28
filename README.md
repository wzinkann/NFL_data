# NFL Data API

A clean, focused FastAPI application that provides real NFL data including game schedules and betting odds using the Tank01 API.

## Features

- **Weekly Game Schedules**: Get all NFL games for any week (1-18)
- **Live Betting Odds**: Real-time odds from multiple sportsbooks
- **Team Information**: Full team names, abbreviations, and venue details
- **Smart Caching**: Weekly cache (Tuesday to Tuesday) for optimal performance and API cost management
- **Clean Data**: No mock data - only real NFL information
- **Flexible Week Support**: Query any week of the NFL season

## API Endpoints

### Core Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check and API status
- `GET /games/week/{week}` - Get all games for a specific week (1-18)
- `GET /games/current-week` - Get all games for the current week
- `GET /games/available-weeks` - Get list of available weeks for a season
- `GET /odds/{game_id}` - Get betting odds for a specific game

### Utility Endpoints

- `GET /cache/info` - Cache information and status
- `POST /cache/clear` - Clear all cached data
- `GET /debug/config` - Debug configuration (development only)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/wzinkann/NFL_data.git
cd NFL_data
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy the example environment file and configure your Tank01 API key:

```bash
cp .env.example .env
```

Edit `.env` and add your Tank01 API key:

```env
TANK01_API_KEY=your_rapidapi_key_here
TANK01_BASE_URL=https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com
```

### 4. Run the API

```bash
python main.py
```

The API will start on `http://localhost:8000`

### 5. Access the API

- **API Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## Usage Examples

### Get Week 1 Games

```bash
curl http://localhost:8000/games/week/1
```

Response:
```json
[
  {
    "game_id": "20250904_DAL@PHI",
    "home_team": "Philadelphia Eagles",
    "away_team": "Dallas Cowboys",
    "away_abbreviation": "DAL",
    "home_abbreviation": "PHI",
    "game_time": "2025-09-04T20:20:00-04:00",
    "week": 1,
    "season": 2025,
    "status": "scheduled",
    "venue": "Lincoln Financial Field",
    "game_date": "20250904",
    "espn_id": "401772510",
    "neutral_site": false
  }
]
```

### Get Betting Odds for a Game

```bash
curl http://localhost:8000/odds/20250907_ARI@NO
```

Response:
```json
{
  "game_id": "20250907_ARI@NO",
  "odds": {
    "game_id": "20250907_ARI@NO",
    "last_updated": "1754949986.6076572",
    "game_date": "20250907",
    "away_team": "ARI",
    "home_team": "NO",
    "sportsbooks": {
      "betmgm": {
        "spread": {
          "away": "-6",
          "home": "+6",
          "away_odds": "-105",
          "home_odds": "-115"
        },
        "total": {
          "over": "42.5",
          "under": "42.5",
          "over_odds": "-110",
          "under_odds": "-110"
        },
        "moneyline": {
          "away": "-250",
          "home": "+200"
        },
        "implied_totals": {
          "awayTotal": "24.25",
          "homeTotal": "18.25"
        }
      }
    }
  }
}
```

### Get Available Weeks

```bash
curl http://localhost:8000/games/available-weeks
```

Response:
```json
{
  "season": 2025,
  "available_weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
  "note": "NFL regular season typically runs weeks 1-18"
}
```

## Data Sources

### Tank01 API Integration

The application integrates with Tank01 NFL API via RapidAPI:

- **Schedule Endpoint**: `/getNFLGamesForWeek` - Game schedules for any week
- **Betting Odds Endpoint**: `/getNFLBettingOdds` - Live odds from multiple sportsbooks

### Supported Sportsbooks

- BetMGM
- Bet365
- FanDuel
- BallyBet
- ESPN Bet
- BetRivers
- Caesars Sportsbook
- DraftKings

### Venue Information

Complete stadium mapping for all 32 NFL teams:
- **Home Games**: Actual stadium names (e.g., "Arrowhead Stadium" for KC)
- **Neutral Site Games**: Shows "Neutral Site"
- **Shared Stadiums**: Properly handled (e.g., NYG/NYJ both show "MetLife Stadium")

## Caching Strategy

### Cache Behavior

- **Cache TTL**: Weekly (Tuesday to Tuesday)
- **Cache Keys**: Unique per week and game ID
- **Smart Refresh**: Data automatically refreshes every Tuesday
- **Cost Optimization**: Minimizes Tank01 API calls
- **NFL Aligned**: Perfect for weekly schedule updates

### Cache Management

- **View Cache Status**: `GET /cache/info`
- **Clear All Cache**: `POST /cache/clear`
- **Force Fresh Data**: Clear cache to get latest information
- **Weekly Refresh**: Cache automatically expires every Tuesday
- **Smart TTL**: Duration adjusts based on current day of week

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TANK01_API_KEY` | Your RapidAPI key for Tank01 | Yes |
| `TANK01_BASE_URL` | Tank01 API base URL | Yes |
| `API_HOST` | API host address | No (default: 0.0.0.0) |
| `API_PORT` | API port | No (default: 8000) |
| `DEBUG` | Enable debug mode | No (default: False) |

## Project Structure

```
NFL_data/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── tank01_client.py     # Tank01 API client
├── requirements.txt     # Python dependencies
├── runtime.txt          # Python version specification
├── render.yaml          # Render deployment configuration
├── start.sh             # Development startup script
└── README.md            # This file
```

## Deployment

### Render (Recommended)

The project includes `render.yaml` for easy deployment on Render:

1. Connect your GitHub repository to Render
2. Render will automatically detect the configuration
3. Set your `TANK01_API_KEY` environment variable
4. Deploy

### Start Command

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
```

### Build Command

```bash
pip install --only-binary=all -r requirements.txt
```

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
python main.py

# Or use the start script
./start.sh
```

### Testing

Test the API endpoints using curl or Postman:

```bash
# Test root endpoint
curl http://localhost:8000/

# Test games endpoint
curl http://localhost:8000/games/week/1

# Test betting odds
curl http://localhost:8000/odds/20250907_ARI@NO
```

## API Response Format

### Game Object

```json
{
  "game_id": "20250904_DAL@PHI",
  "home_team": "Philadelphia Eagles",
  "away_team": "Dallas Cowboys",
  "away_abbreviation": "DAL",
  "home_abbreviation": "PHI",
  "game_time": "2025-09-04T20:20:00-04:00",
  "week": 1,
  "season": 2025,
  "status": "scheduled",
  "venue": "Lincoln Financial Field",
  "game_date": "20250904",
  "espn_id": "401772510",
  "neutral_site": false
}
```

### Betting Odds Object

```json
{
  "game_id": "20250907_ARI@NO",
  "odds": {
    "sportsbooks": {
      "betmgm": {
        "spread": {...},
        "total": {...},
        "moneyline": {...},
        "implied_totals": {...}
      }
    }
  }
}
```

## Error Handling

### HTTP Status Codes

- **200**: Success
- **400**: Bad Request (invalid week number, etc.)
- **404**: Not Found (invalid game ID, etc.)
- **500**: Internal Server Error

### Error Response Format

```json
{
  "detail": "Week must be between 1 and 18"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:

1. Check the API documentation at `/docs`
2. Review the logs for error messages
3. Verify your Tank01 API key
4. Check the cache status at `/cache/info`

## Disclaimer

This application provides real NFL data for informational purposes. Betting odds are for reference only and should not be used for gambling decisions. Always verify data accuracy and use at your own risk.
