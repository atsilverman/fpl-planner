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
    """Serve players data from static JSON file"""
    try:
        with open('data/players.json', 'r') as f:
            data = json.load(f)
        return jsonify(data['data'])
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
    """Serve player fixture history from static JSON file"""
    try:
        with open('data/player-history.json', 'r') as f:
            data = json.load(f)
        
        # For now, return default data for all players
        # In the future, this could be expanded with actual player-specific data
        return jsonify(data['data']['default'])
            
    except FileNotFoundError:
        return jsonify({'fixtures': [], 'is_new_player': False})
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