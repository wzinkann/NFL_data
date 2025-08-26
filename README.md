# NFL Game Outcome Prediction API

A FastAPI-based application that predicts NFL game outcomes, scores, and spreads using data from the Tank01 API.

## Features

- 🏈 **Weekly Predictions**: Get game outcome predictions for all games in the current week
- 🎯 **Individual Game Predictions**: Predict scores, spreads, and totals for specific games
- 📊 **Advanced Algorithm**: Sophisticated prediction engine considering team strengths and matchups
- 🔄 **Caching**: Built-in caching for API responses to improve performance
- 📈 **Team Statistics**: Access to team offensive/defensive rankings and performance data
- 🚀 **Mock Data Fallback**: Works without API key using realistic mock data
- 📝 **Detailed Analysis**: Each prediction includes spreads, totals, win probabilities, and reasoning

## API Endpoints

### Core Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check and API status
- `GET /games/current-week` - Get all games for the current week
- `GET /predictions/current-week` - Get game outcome predictions for all games
- `GET /predictions/game/{game_id}` - Get prediction for a specific game

### Additional Endpoints

- `GET /standings` - Current NFL standings
- `GET /teams/{team}/stats` - Team statistics
- `GET /cache/info` - Cache information
- `POST /cache/clear` - Clear cache
- `GET /debug/config` - Debug configuration (development only)

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd NFL_data
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy the example environment file and configure your Tank01 API key:

```bash
cp env.example .env
```

Edit `.env` and add your Tank01 API key:

```env
TANK01_API_KEY=your_actual_api_key_here
TANK01_BASE_URL=https://api.tank01.com
MODEL_CONFIDENCE_THRESHOLD=0.6
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

### Get Weekly Predictions

```bash
curl http://localhost:8000/predictions/current-week
```

Response:
```json
{
  "week": 15,
  "season": 2024,
  "predictions": [
    {
      "game_id": "game_1",
      "home_team": "Kansas City Chiefs",
      "away_team": "Las Vegas Raiders",
      "predicted_scores": {
        "home_score": 28,
        "away_score": 21
      },
      "spread": {
        "value": 7,
        "formatted": "+7",
        "favorite": "home",
        "underdog": "away"
      },
      "total": {
        "value": 49,
        "formatted": "O/U 49"
      },
      "win_probability": {
        "home": 0.72,
        "away": 0.28
      },
      "game_type": "competitive",
      "key_factors": [
        "Home team has strong offense vs weak defense",
        "Divisional rivalry - expect close game"
      ],
      "confidence_score": 0.78,
      "reasoning": "Home team (Kansas City Chiefs) predicted to win 28-21. Moderate advantage for the favorite. Moderate scoring expected. Kansas City Chiefs has strong offense vs Las Vegas Raiders's weak defense. Divisional rivalry often produces unpredictable results."
    }
  ],
  "generated_at": "2024-01-15T10:30:00"
}
```

### Get Specific Game Prediction

```bash
curl http://localhost:8000/predictions/game/game_1
```

### Get Current Week Games

```bash
curl http://localhost:8000/games/current-week
```

## Prediction Algorithm

The prediction engine uses a sophisticated algorithm that considers:

### Team Strength Factors
- **Offensive Rankings**: Points per game and offensive efficiency
- **Defensive Rankings**: Points allowed and defensive performance
- **Team Consistency**: Performance stability and recent form
- **Historical Data**: Season-long trends and patterns

### Game Context
- **Home Field Advantage**: Standard 2.5-point home advantage
- **Divisional Games**: Rivalry intensity and familiarity
- **Matchup Analysis**: Offense vs defense strength comparisons
- **Weather Conditions**: Environmental factors (when available)

### Scoring Model
- **Base Scoring**: Team offensive and defensive averages
- **Realistic Variation**: Gaussian distribution around expected scores
- **Score Constraints**: Ensures scores stay within realistic NFL ranges (0-50)
- **Win Probability**: Logistic function converting score differences to win chances

### Game Classification
- **Close Game**: Spread ≤ 3 points
- **Competitive**: Spread 4-7 points
- **Moderate Blowout**: Spread 8-14 points
- **Blowout**: Spread > 14 points

## Tank01 API Integration

### Required Endpoints

The application expects these Tank01 API endpoints (you may need to adjust based on actual API documentation):

- `GET /nfl/schedule/current-week` - Current week's games
- `GET /nfl/teams/{team}/stats` - Team offensive/defensive statistics
- `GET /nfl/standings` - League standings
- `GET /nfl/schedule` - Full season schedule

### API Response Parsing

The `Tank01Client` includes parsing methods that you'll need to customize based on the actual API response format. Look for methods like:

- `_parse_schedule_data()`
- `_parse_team_stats_data()`
- `_parse_standings_data()`

### Fallback to Mock Data

If the Tank01 API is unavailable or you don't have an API key, the application will automatically use realistic mock data for demonstration purposes.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TANK01_API_KEY` | Your Tank01 API key | Required |
| `TANK01_BASE_URL` | Tank01 API base URL | `https://api.tank01.com` |
| `MODEL_CONFIDENCE_THRESHOLD` | Minimum confidence for predictions | `0.6` |
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `DEBUG` | Enable debug mode | `False` |

### Model Configuration

You can adjust the prediction algorithm by modifying:

- Team strength calculations in `prediction_engine.py`
- Home field advantage adjustments
- Scoring variation parameters
- Win probability calculations

## Development

### Project Structure

```
NFL_data/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── tank01_client.py     # Tank01 API client
├── prediction_engine.py # Game outcome prediction algorithm
├── requirements.txt     # Python dependencies
├── env.example         # Environment variables template
└── README.md           # This file
```

### Adding New Features

1. **New Endpoints**: Add to `main.py` with proper error handling
2. **Enhanced Predictions**: Modify `prediction_engine.py`
3. **Additional Data**: Extend `tank01_client.py`
4. **Configuration**: Update `config.py`

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Environment Variables

For production deployment, ensure all environment variables are properly set:

```bash
export TANK01_API_KEY="your_production_api_key"
export TANK01_BASE_URL="https://api.tank01.com"
export MODEL_CONFIDENCE_THRESHOLD="0.6"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the API documentation at `/docs`
2. Review the logs for error messages
3. Verify your Tank01 API key and endpoints
4. Check the cache status at `/cache/info`

## Disclaimer

This application is for entertainment and educational purposes. NFL predictions are inherently uncertain and should not be used for gambling or financial decisions. Always verify data accuracy and use at your own risk.
