from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import json
import csv

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
    """Serve player fixture history data from real historical data"""
    try:
        player_name = request.args.get('player_name', '')
        opponent_team_id = request.args.get('opponent_team_id', '')
        
        if not player_name or not opponent_team_id:
            return jsonify({'error': 'Missing player_name or opponent_team_id parameter'}), 400
        
        # Load team mappings to convert current team ID to historical team ID
        team_mapping = {}
        try:
            # Load current teams (2025)
            current_teams = {}
            with open(os.path.expanduser('~/Desktop/teams_2025.csv'), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    current_teams[row['id']] = {
                        'name': row['name'],
                        'short_name': row['short_name'],
                        'code': row['code']
                    }
            
            # Load historical teams (2024)
            historical_teams = {}
            with open(os.path.expanduser('~/Desktop/teams_2024.csv'), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    historical_teams[row['id']] = {
                        'name': row['name'],
                        'short_name': row['short_name'],
                        'code': row['code']
                    }
            
            # Create mapping from current team ID to historical team ID using codes
            code_to_historical_id = {}
            for hist_id, hist_team in historical_teams.items():
                code_to_historical_id[hist_team['code']] = hist_id
            
            # Map current team ID to historical team ID
            current_team = current_teams.get(opponent_team_id)
            if current_team and current_team['code'] in code_to_historical_id:
                historical_team_id = code_to_historical_id[current_team['code']]
            else:
                # Team not in historical data (newly promoted team)
                return jsonify({
                    'fixtures': [],
                    'is_new_player': False
                })
                
        except Exception as e:
            return jsonify({'error': f'Team mapping error: {str(e)}'}), 500
        
        # Load real historical data
        with open('data/player-history.json', 'r') as f:
            history_data = json.load(f)
        
        # Find the player's data
        if player_name in history_data['data']:
            player_data = history_data['data'][player_name]
            
            # Find the opponent's data using historical team ID
            if str(historical_team_id) in player_data:
                return jsonify(player_data[str(historical_team_id)])
            else:
                # No historical data for this opponent
                return jsonify({
                    'fixtures': [],
                    'is_new_player': False
                })
        else:
            # Player not found in historical data
            return jsonify({
                'fixtures': [],
                'is_new_player': True
            })
        
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