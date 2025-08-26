#!/usr/bin/env python3
"""
Simple test script for the NFL Game Outcome Prediction API
Run this after starting the API to test basic functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code == 200:
            print(f"✅ {method} {endpoint} - Success")
            return response.json()
        else:
            print(f"❌ {method} {endpoint} - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Connection failed. Is the API running?")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🏈 NFL Game Outcome Prediction API - Test Suite")
    print("=" * 60)
    
    # Wait a moment for API to be ready
    print("Waiting for API to be ready...")
    time.sleep(2)
    
    # Test basic endpoints
    print("\n1. Testing Basic Endpoints")
    print("-" * 30)
    
    # Root endpoint
    root_data = test_endpoint("/")
    if root_data:
        print(f"   API Version: {root_data.get('version', 'Unknown')}")
        print(f"   Tank01 API Configured: {root_data.get('config', {}).get('tank01_api_configured', False)}")
    
    # Health check
    health_data = test_endpoint("/health")
    if health_data:
        print(f"   API Status: {health_data.get('status', 'Unknown')}")
        print(f"   Tank01 Status: {health_data.get('tank01_api_status', 'Unknown')}")
    
    # Test games endpoint
    print("\n2. Testing Games Endpoint")
    print("-" * 30)
    games_data = test_endpoint("/games/current-week")
    if games_data:
        print(f"   Found {len(games_data)} games this week")
        for game in games_data[:2]:  # Show first 2 games
            print(f"   - {game['away_team']} @ {game['home_team']} (Week {game['week']})")
    
    # Test predictions endpoint
    print("\n3. Testing Game Outcome Predictions")
    print("-" * 30)
    predictions_data = test_endpoint("/predictions/current-week")
    if predictions_data:
        print(f"   Generated {len(predictions_data['predictions'])} predictions")
        print(f"   Week {predictions_data['week']}, Season {predictions_data['season']}")
        
        # Show first prediction details
        if predictions_data['predictions']:
            pred = predictions_data['predictions'][0]
            print(f"   Sample Prediction:")
            print(f"     Game: {pred['away_team']} @ {pred['home_team']}")
            print(f"     Predicted Score: {pred['home_team']} {pred['predicted_scores']['home_score']}, {pred['away_team']} {pred['predicted_scores']['away_score']}")
            print(f"     Spread: {pred['spread']['formatted']} ({pred['spread']['favorite']} favored)")
            print(f"     Total: {pred['total']['formatted']}")
            print(f"     Win Probability: {pred['home_team']} {pred['win_probability']['home']:.1%}, {pred['away_team']} {pred['win_probability']['away']:.1%}")
            print(f"     Game Type: {pred['game_type']}")
            print(f"     Confidence: {pred['confidence_score']:.1%}")
            print(f"     Key Factors: {', '.join(pred['key_factors'][:2])}...")
            print(f"     Reasoning: {pred['reasoning'][:100]}...")
    
    # Test individual game prediction
    print("\n4. Testing Individual Game Prediction")
    print("-" * 30)
    if games_data:
        game_id = games_data[0]['game_id']
        game_pred = test_endpoint(f"/predictions/game/{game_id}")
        if game_pred:
            print(f"   Successfully predicted outcome for game {game_id}")
            print(f"   {game_pred['home_team']} {game_pred['predicted_scores']['home_score']} - {game_pred['away_team']} {game_pred['predicted_scores']['away_score']}")
    
    # Test additional endpoints
    print("\n5. Testing Additional Endpoints")
    print("-" * 30)
    
    # Standings
    standings_data = test_endpoint("/standings")
    if standings_data:
        print("   ✅ Standings endpoint working")
    
    # Team stats
    if games_data:
        team_name = games_data[0]['home_team']
        team_stats = test_endpoint(f"/teams/{team_name}/stats")
        if team_stats:
            print(f"   ✅ Team stats endpoint working for {team_name}")
    
    # Cache info
    cache_data = test_endpoint("/cache/info")
    if cache_data:
        print(f"   ✅ Cache endpoint working - {cache_data['total_items']} cached items")
    
    # Test cache clear
    clear_result = test_endpoint("/cache/clear", method="POST")
    if clear_result:
        print("   ✅ Cache clear endpoint working")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 Test Summary")
    print("=" * 60)
    
    if root_data and health_data and games_data and predictions_data:
        print("✅ All core endpoints are working!")
        print("✅ API is ready for use")
        print("\n📚 Next steps:")
        print("   - Visit http://localhost:8000/docs for interactive API documentation")
        print("   - Use the endpoints to get game outcome predictions")
        print("   - Customize the prediction algorithm in prediction_engine.py")
        print("   - Add your Tank01 API key to .env for real data")
        print("\n🎲 Prediction Features:")
        print("   - Game scores and spreads")
        print("   - Over/under totals")
        print("   - Win probabilities")
        print("   - Game type classification")
        print("   - Key factors analysis")
    else:
        print("❌ Some endpoints failed. Check the API logs for errors.")
        print("\n🔧 Troubleshooting:")
        print("   - Ensure the API is running (python main.py)")
        print("   - Check for error messages in the terminal")
        print("   - Verify all dependencies are installed")

if __name__ == "__main__":
    main()
