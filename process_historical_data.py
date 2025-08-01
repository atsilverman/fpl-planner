import csv
import json
import os
from collections import defaultdict

def load_player_mappings():
    """Load and create mappings between historical and current player IDs"""
    
    # Load historical players (2024)
    historical_players = {}
    with open(os.path.expanduser('~/Desktop/players.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            historical_players[row['id']] = {
                'web_name': row['web_name'],
                'first_name': row['first_name'],
                'second_name': row['second_name'],
                'team_id': row['team_id'],
                'element_type': row['element_type']
            }
    
    # Load current players (2025)
    current_players = {}
    with open(os.path.expanduser('~/Desktop/players_2025.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            current_players[row['id']] = {
                'web_name': row['web_name'],
                'first_name': row['first_name'],
                'second_name': row['second_name'],
                'team_id': row['team_id'],
                'element_type': row['element_type']
            }
    
    # Create name-based mapping
    name_mapping = {}
    for hist_id, hist_player in historical_players.items():
        hist_name = hist_player['web_name'].lower().strip()
        hist_team = hist_player['team_id']
        
        # Find matching current player by name and team
        for curr_id, curr_player in current_players.items():
            curr_name = curr_player['web_name'].lower().strip()
            curr_team = curr_player['team_id']
            
            # Exact match
            if hist_name == curr_name and hist_team == curr_team:
                name_mapping[hist_id] = curr_id
                break
            
            # Fuzzy match for common variations
            elif (hist_name in curr_name or curr_name in hist_name) and hist_team == curr_team:
                name_mapping[hist_id] = curr_id
                break
    
    return historical_players, current_players, name_mapping

def process_gameweek_stats():
    """Process the historical gameweek stats with current player IDs"""
    
    historical_players, current_players, name_mapping = load_player_mappings()
    
    # Load team mappings
    with open('data/teams.json', 'r') as f:
        teams_data = json.load(f)
    
    team_id_to_name = {}
    for team in teams_data['data']:
        team_id_to_name[str(team['id'])] = team['short_name']
    
    # Process historical gameweek stats
    processed_stats = defaultdict(list)
    unmatched_count = 0
    matched_count = 0
    
    with open(os.path.expanduser('~/Desktop/player_gameweek_stats.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            historical_player_id = row['player_id']
            opponent_team_id = row['opponent_team']
            
            # Try to find current player ID
            current_player_id = name_mapping.get(historical_player_id)
            
            if current_player_id:
                # Get current player info
                current_player = current_players.get(current_player_id)
                if current_player:
                    # Create processed record
                    processed_record = {
                        'player_id': current_player_id,
                        'player_name': current_player['web_name'],
                        'team_id': current_player['team_id'],
                        'team_name': team_id_to_name.get(str(current_player['team_id']), f"Team_{current_player['team_id']}"),
                        'gameweek': int(row['gameweek']),
                        'opponent_team_id': int(opponent_team_id),
                        'opponent_team_name': team_id_to_name.get(str(opponent_team_id), f"Team_{opponent_team_id}"),
                        'was_home': row['was_home'].lower() == 'true',
                        'total_points': int(row['total_points']) if row['total_points'] else 0,
                        'minutes': int(row['minutes']) if row['minutes'] else 0,
                        'goals_scored': int(row['goals_scored']) if row['goals_scored'] else 0,
                        'assists': int(row['assists']) if row['assists'] else 0,
                        'clean_sheets': int(row['clean_sheets']) if row['clean_sheets'] else 0,
                        'goals_conceded': int(row['goals_conceded']) if row['goals_conceded'] else 0,
                        'bonus': int(row['bonus']) if row['bonus'] else 0,
                        'saves': int(row['saves']) if row['saves'] else 0,
                        'expected_goals': float(row['expected_goals']) if row['expected_goals'] else 0.0,
                        'expected_assists': float(row['expected_assists']) if row['expected_assists'] else 0.0,
                        'expected_goals_conceded': float(row['expected_goals_conceded']) if row['expected_goals_conceded'] else 0.0
                    }
                    
                    # Group by player and opponent
                    key = (current_player_id, opponent_team_id)
                    processed_stats[key].append(processed_record)
                    matched_count += 1
                else:
                    unmatched_count += 1
            else:
                unmatched_count += 1
    
    print(f"✅ Processed {matched_count} records")
    print(f"❌ Unmatched {unmatched_count} records")
    
    return processed_stats

def create_player_history_json():
    """Create the player history JSON file for the website"""
    
    processed_stats = process_gameweek_stats()
    
    # Create the structure for the API
    player_history_data = {}
    
    for (player_id, opponent_team_id), fixtures in processed_stats.items():
        # Get player name from first record
        player_name = fixtures[0]['player_name']
        
        # Create fixtures list for this player vs this opponent
        fixtures_list = []
        for fixture in fixtures:
            fixtures_list.append({
                'gameweek': fixture['gameweek'],
                'total_points': fixture['total_points'],
                'minutes': fixture['minutes'],
                'goals_scored': fixture['goals_scored'],
                'assists': fixture['assists'],
                'clean_sheets': fixture['clean_sheets'],
                'goals_conceded': fixture['goals_conceded'],
                'bonus': fixture['bonus'],
                'saves': fixture['saves'],
                'expected_goals': fixture['expected_goals'],
                'expected_assists': fixture['expected_assists'],
                'expected_goals_conceded': fixture['expected_goals_conceded'],
                'was_home': fixture['was_home']
            })
        
        # Store in the data structure
        if player_name not in player_history_data:
            player_history_data[player_name] = {}
        
        player_history_data[player_name][str(opponent_team_id)] = {
            'fixtures': fixtures_list,
            'is_new_player': False
        }
    
    # Save to JSON file
    output_data = {
        'last_updated': datetime.now().isoformat(),
        'data': player_history_data
    }
    
    with open('data/player-history.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✅ Created player history data for {len(player_history_data)} players")
    print(f"📁 Saved to data/player-history.json")
    
    return player_history_data

def update_backend_api():
    """Update the backend API to use real historical data"""
    
    # Read the current app.py
    with open('app.py', 'r') as f:
        app_content = f.read()
    
    # Replace the hardcoded sample data with real data loading
    new_api_code = '''@app.route('/api/player-fixture-history')
def get_player_fixture_history():
    """Serve player fixture history data from real historical data"""
    try:
        player_name = request.args.get('player_name', '')
        opponent_team_id = request.args.get('opponent_team_id', '')
        
        if not player_name or not opponent_team_id:
            return jsonify({'error': 'Missing player_name or opponent_team_id parameter'}), 400
        
        # Load real historical data
        with open('data/player-history.json', 'r') as f:
            history_data = json.load(f)
        
        # Find the player's data
        if player_name in history_data['data']:
            player_data = history_data['data'][player_name]
            
            # Find the opponent's data
            if opponent_team_id in player_data:
                return jsonify(player_data[opponent_team_id])
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
        return jsonify({'error': str(e)}), 500'''
    
    # Replace the old API code
    import re
    pattern = r'@app\.route\(\'/api/player-fixture-history\'\)\s*def get_player_fixture_history\(\):.*?return jsonify\(sample_data\)'
    replacement = new_api_code
    
    updated_content = re.sub(pattern, replacement, app_content, flags=re.DOTALL)
    
    # Write the updated content
    with open('app.py', 'w') as f:
        f.write(updated_content)
    
    print("✅ Updated backend API to use real historical data")

def main():
    """Main processing function"""
    print("🚀 Processing Historical Data...")
    
    # Create the player history JSON
    player_history_data = create_player_history_json()
    
    # Update the backend API
    update_backend_api()
    
    print("\n🎉 Historical data processing complete!")
    print("📊 The website will now show real historical data in matchup popups")
    
    # Show some sample data
    print("\n📋 Sample historical data:")
    sample_count = 0
    for player_name, opponents in player_history_data.items():
        if sample_count < 3:
            for opponent_id, data in opponents.items():
                if data['fixtures']:
                    fixture = data['fixtures'][0]
                    print(f"  {player_name} vs Team {opponent_id}: {fixture['total_points']} points (GW{fixture['gameweek']})")
                    sample_count += 1
                    break

if __name__ == "__main__":
    from datetime import datetime
    main() 