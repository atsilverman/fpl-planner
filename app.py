from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import json

app = Flask(__name__)

# Configure CORS for production
CORS(app, origins=[
    "https://your-vercel-domain.vercel.app",  # Replace with your actual Vercel domain
    "http://localhost:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000"
])

# Environment-based configuration
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:5001')

@app.route('/')
def index():
    return send_from_directory('static', 'fpl_draft_planner.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files including team badges"""
    # Handle URL-encoded filenames (spaces, apostrophes, etc.)
    import urllib.parse
    decoded_filename = urllib.parse.unquote(filename)
    return send_from_directory('static', decoded_filename)

@app.route('/team-badges/<path:filename>')
def serve_team_badges(filename):
    """Serve team badge files specifically"""
    import urllib.parse
    decoded_filename = urllib.parse.unquote(filename)
    return send_from_directory('static/team_badges_svg', decoded_filename)

@app.route('/api/teams')
def get_teams():
    """Serve teams data from static JSON file"""
    try:
        with open('data/teams.json', 'r') as f:
            data = json.load(f)
        return jsonify(data['data'])
    except FileNotFoundError:
        return jsonify({'error': 'Teams data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players')
def get_players():
    """Serve players data from static JSON file with optional filtering"""
    try:
        # Get filter parameters
        position_filter = request.args.get('position', '')
        location_filter = request.args.get('location', '')
        
        with open('data/players.json', 'r') as f:
            data = json.load(f)
        
        players = data['data']
        
        # Apply position filter if specified
        if position_filter:
            position_codes = position_filter.split(',')
            filtered_element_types = []
            
            for pos in position_codes:
                # Handle both position codes (GKP, DEF, MID, FWD) and element_type values (1, 2, 3, 4)
                if pos in ['GKP', 'DEF', 'MID', 'FWD']:
                    # Map position codes to element_type values
                    position_to_element_type = {
                        'GKP': 1,
                        'DEF': 2,
                        'MID': 3,
                        'FWD': 4
                    }
                    filtered_element_types.append(position_to_element_type[pos])
                elif pos in ['1', '2', '3', '4']:
                    # Direct element_type values
                    filtered_element_types.append(int(pos))
            
            if filtered_element_types:
                players = [p for p in players if p['element_type'] in filtered_element_types]
        
        # Apply location filter if specified
        if location_filter and location_filter != 'overall':
            # Load teams data to get team locations
            try:
                with open('data/teams.json', 'r') as f:
                    teams_data = json.load(f)
                teams = {team['id']: team for team in teams_data['data']}
                
                # Filter players by team location
                players = [p for p in players if teams.get(p['team_id'], {}).get('location') == location_filter]
            except Exception as e:
                print(f"Warning: Could not apply location filter: {e}")
        
        return jsonify(players)
    except FileNotFoundError:
        return jsonify({'error': 'Players data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fixtures')
def get_fixtures():
    """Serve fixtures data from static JSON file"""
    try:
        with open('data/fixtures.json', 'r') as f:
            data = json.load(f)
        return jsonify(data['data'])
    except FileNotFoundError:
        return jsonify({'error': 'Fixtures data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/team-stats')
def get_team_stats():
    """Serve team stats from static JSON file"""
    try:
        location = request.args.get('location', 'overall')
        
        with open('data/team-stats.json', 'r') as f:
            data = json.load(f)
        
        if location in data:
            return jsonify(data[location])
        else:
            return jsonify({'error': f'Location {location} not found'}), 404
            
    except FileNotFoundError:
        return jsonify({'error': 'Team stats data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/team-rankings-overall')
def get_team_rankings_overall():
    """Serve team rankings from static JSON file"""
    try:
        ranking_type = request.args.get('type', 'attack')
        
        with open('data/team-rankings.json', 'r') as f:
            data = json.load(f)
        
        if ranking_type in data:
            return jsonify(data[ranking_type])
        else:
            return jsonify({'error': f'Ranking type {ranking_type} not found'}), 404
            
    except FileNotFoundError:
        return jsonify({'error': 'Team rankings data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/team-rankings')
def get_team_rankings():
    """Serve team rankings from static JSON file (alias for team-rankings-overall)"""
    return get_team_rankings_overall()

@app.route('/api/player-fixture-history')
def get_player_fixture_history():
    """Serve player fixture history data"""
    try:
        player_name = request.args.get('player_name', '')
        opponent_team_id = request.args.get('opponent_team_id', '')
        
        if not player_name or not opponent_team_id:
            return jsonify({'error': 'Missing player_name or opponent_team_id parameter'}), 400
        
        # For now, return sample data that varies by player name to simulate different historical data
        # In a real implementation, this would query a database with actual historical data
        
        # Generate realistic sample data based on player name and opponent team
        import hashlib
        
        # Create a hash from both player name and opponent team ID for more realistic variation
        combined_hash = int(hashlib.md5(f"{player_name}_{opponent_team_id}".encode()).hexdigest()[:8], 16)
        
        # Determine player type based on name patterns (this would normally come from database)
        is_attacker = any(name in player_name.lower() for name in ['salah', 'haaland', 'kane', 'son', 'rashford', 'martinelli', 'saka', 'foden'])
        is_defender = any(name in player_name.lower() for name in ['dias', 'vvd', 'virgil', 'saliba', 'gabriel', 'white', 'walker', 'cancelo'])
        is_goalkeeper = any(name in player_name.lower() for name in ['alisson', 'ederson', 'ramsdale', 'pope', 'de gea', 'kepa'])
        
        # Generate realistic gameweek numbers (not always 1 and 2)
        home_gw = (combined_hash % 20) + 1  # Gameweek 1-20
        away_gw = ((combined_hash + 100) % 20) + 1  # Different gameweek 1-20
        
        if is_goalkeeper:
            # Goalkeeper stats
            home_points = 6 if combined_hash % 3 == 0 else 4 if combined_hash % 3 == 1 else 8
            away_points = 2 if combined_hash % 4 == 0 else 6 if combined_hash % 4 == 1 else 4
            sample_data = {
                'fixtures': [
                    {
                        'gameweek': home_gw,
                        'total_points': home_points,
                        'minutes': 90,
                        'goals_scored': 0,
                        'assists': 0,
                        'clean_sheets': 1 if home_points >= 6 else 0,
                        'bonus': 1 if home_points >= 8 else 0,
                        'saves': (combined_hash % 5) + 2,
                        'goals_conceded': 0 if home_points >= 6 else (combined_hash % 3) + 1,
                        'expected_goals': 0.0,
                        'expected_assists': 0.0,
                        'expected_goals_conceded': 1.2 if home_points < 6 else 0.8,
                        'was_home': True
                    },
                    {
                        'gameweek': away_gw,
                        'total_points': away_points,
                        'minutes': 90,
                        'goals_scored': 0,
                        'assists': 0,
                        'clean_sheets': 1 if away_points >= 6 else 0,
                        'bonus': 1 if away_points >= 8 else 0,
                        'saves': (combined_hash % 4) + 1,
                        'goals_conceded': 0 if away_points >= 6 else (combined_hash % 3) + 1,
                        'expected_goals': 0.0,
                        'expected_assists': 0.0,
                        'expected_goals_conceded': 1.5 if away_points < 6 else 1.0,
                        'was_home': False
                    }
                ],
                'is_new_player': False
            }
        elif is_defender:
            # Defender stats
            home_points = 7 if combined_hash % 4 == 0 else 3 if combined_hash % 4 == 1 else 6
            away_points = 2 if combined_hash % 3 == 0 else 5 if combined_hash % 3 == 1 else 4
            home_goals = 1 if home_points >= 7 else 0
            away_goals = 1 if away_points >= 7 else 0
            sample_data = {
                'fixtures': [
                    {
                        'gameweek': home_gw,
                        'total_points': home_points,
                        'minutes': 90,
                        'goals_scored': home_goals,
                        'assists': 1 if home_points >= 7 and home_goals == 0 else 0,
                        'clean_sheets': 1 if home_points >= 6 else 0,
                        'bonus': 1 if home_points >= 7 else 0,
                        'expected_goals': 0.3 if home_goals == 0 else 0.8,
                        'expected_assists': 0.2 if home_points >= 6 else 0.1,
                        'was_home': True
                    },
                    {
                        'gameweek': away_gw,
                        'total_points': away_points,
                        'minutes': 90,
                        'goals_scored': away_goals,
                        'assists': 1 if away_points >= 7 and away_goals == 0 else 0,
                        'clean_sheets': 1 if away_points >= 6 else 0,
                        'bonus': 1 if away_points >= 7 else 0,
                        'expected_goals': 0.2 if away_goals == 0 else 0.6,
                        'expected_assists': 0.1 if away_points >= 6 else 0.0,
                        'was_home': False
                    }
                ],
                'is_new_player': False
            }
        else:
            # Attacker/Midfielder stats
            home_points = 8 if combined_hash % 5 == 0 else 3 if combined_hash % 5 == 1 else 6
            away_points = 2 if combined_hash % 4 == 0 else 7 if combined_hash % 4 == 1 else 4
            home_goals = 1 if home_points >= 7 else 0
            away_goals = 1 if away_points >= 7 else 0
            home_assists = 1 if home_points >= 6 and home_goals == 0 else 0
            away_assists = 1 if away_points >= 6 and away_goals == 0 else 0
            sample_data = {
                'fixtures': [
                    {
                        'gameweek': home_gw,
                        'total_points': home_points,
                        'minutes': 90,
                        'goals_scored': home_goals,
                        'assists': home_assists,
                        'bonus': 1 if home_points >= 8 else 0,
                        'expected_goals': 0.8 if home_goals == 0 else 1.2,
                        'expected_assists': 0.6 if home_assists == 0 else 1.1,
                        'was_home': True
                    },
                    {
                        'gameweek': away_gw,
                        'total_points': away_points,
                        'minutes': 90,
                        'goals_scored': away_goals,
                        'assists': away_assists,
                        'bonus': 1 if away_points >= 8 else 0,
                        'expected_goals': 0.5 if away_goals == 0 else 1.0,
                        'expected_assists': 0.4 if away_assists == 0 else 0.9,
                        'was_home': False
                    }
                ],
                'is_new_player': False
            }
        
        return jsonify(sample_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/team-fixture-history')
def get_team_fixture_history():
    """Return empty data for team fixture history (not implemented in static version)"""
    return jsonify({'error': 'Team fixture history not available in static mode'})

@app.route('/api/team-saves')
def get_team_saves():
    """Return empty data for team saves (not implemented in static version)"""
    return jsonify([])

@app.route('/api/data-status')
def get_data_status():
    """Return status of all data files"""
    data_files = [
        'teams.json',
        'players.json', 
        'fixtures.json',
        'team-stats.json',
        'team-rankings.json'
    ]
    
    status = {}
    for file in data_files:
        file_path = f'data/{file}'
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    status[file] = {
                        'exists': True,
                        'last_updated': data.get('last_updated', 'Unknown'),
                        'size': os.path.getsize(file_path)
                    }
            except Exception as e:
                status[file] = {
                    'exists': True,
                    'error': str(e)
                }
        else:
            status[file] = {
                'exists': False
            }
    
    return jsonify(status)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False) 