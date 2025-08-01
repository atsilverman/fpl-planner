import csv
import json
import os
from collections import defaultdict
from datetime import datetime

def load_team_mappings():
    """Load team mappings using stable team codes"""
    print("🔍 Loading team mappings...")
    
    # Load 2024/25 teams
    teams_2024 = {}
    with open('data/teams_2024.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            teams_2024[row['id']] = {
                'code': row['code'],
                'name': row['name'],
                'short_name': row['short_name']
            }
    
    # Load 2025/26 teams
    teams_2025 = {}
    with open('data/teams_2025.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            teams_2025[row['code']] = {
                'id': row['id'],
                'name': row['name'],
                'short_name': row['short_name']
            }
    
    print(f"✅ Loaded {len(teams_2024)} 2024 teams and {len(teams_2025)} 2025 teams")
    
    return teams_2024, teams_2025

def load_player_mappings():
    """Load player mappings using names"""
    print("\n🔍 Loading player mappings...")
    
    # Load 2024/25 players
    players_2024 = {}
    with open(os.path.expanduser('~/Desktop/players.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            players_2024[row['id']] = {
                'web_name': row['web_name'],
                'team_id': row['team_id']
            }
    
    # Load 2025/26 players
    players_2025 = {}
    with open(os.path.expanduser('~/Desktop/players_2025.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            players_2025[row['id']] = {
                'web_name': row['web_name'],
                'team_id': row['team_id']
            }
    
    # Create name-based mapping
    name_mapping = {}
    for hist_id, hist_player in players_2024.items():
        hist_name = hist_player['web_name'].lower().strip()
        
        # Find matching player in 2025 by name only
        for curr_id, curr_player in players_2025.items():
            curr_name = curr_player['web_name'].lower().strip()
            if hist_name == curr_name:
                name_mapping[hist_id] = curr_id
                break
    
    print(f"✅ Mapped {len(name_mapping)} players using names")
    
    return players_2024, players_2025, name_mapping

def process_historical_data():
    """Process historical data using team codes"""
    print("\n🔍 Processing historical data...")
    
    teams_2024, teams_2025 = load_team_mappings()
    players_2024, players_2025, name_mapping = load_player_mappings()
    
    # Process historical gameweek stats
    processed_stats = defaultdict(list)
    matched_count = 0
    unmatched_count = 0
    
    with open(os.path.expanduser('~/Desktop/player_gameweek_stats.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            historical_player_id = row['player_id']
            historical_opponent_team_id = row['opponent_team']
            
            # Try to find current player ID
            current_player_id = name_mapping.get(historical_player_id)
            
            if current_player_id:
                # Get current player info
                current_player = players_2025.get(current_player_id)
                
                if current_player:
                    # Get historical team info
                    historical_team = teams_2024.get(historical_opponent_team_id)
                    
                    if historical_team:
                        # Use team code (stable identifier)
                        team_code = historical_team['code']
                        
                        # Debug: Check if team code exists in 2025
                        if team_code not in teams_2025:
                            print(f"⚠️  Missing team code {team_code} in 2025 teams")
                            unmatched_count += 1
                            continue
                        
                        # Create processed record
                        processed_record = {
                            'player_id': current_player_id,
                            'player_name': current_player['web_name'],
                            'team_id': current_player['team_id'],
                            'gameweek': int(row['gameweek']),
                            'opponent_team_code': team_code,
                            'opponent_team_name': teams_2025[team_code]['short_name'],
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
                        
                        # Group by player and opponent team code
                        key = (current_player_id, team_code)
                        processed_stats[key].append(processed_record)
                        matched_count += 1
                    else:
                        unmatched_count += 1
                else:
                    unmatched_count += 1
            else:
                unmatched_count += 1
    
    print(f"✅ Processed {matched_count} records")
    print(f"❌ Unmatched {unmatched_count} records")
    
    return processed_stats

def create_player_history_json():
    """Create the player history JSON file"""
    print("\n🔍 Creating player history JSON...")
    
    processed_stats = process_historical_data()
    
    # Create the structure for the API
    player_history_data = {}
    
    for (player_id, team_code), fixtures in processed_stats.items():
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
        
        # Store in the data structure using team code
        if player_name not in player_history_data:
            player_history_data[player_name] = {}
        
        player_history_data[player_name][team_code] = {
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

def update_api_for_team_codes():
    """Update the API to use team codes"""
    print("\n🔍 Updating API for team codes...")
    
    # Read the current app.py
    with open('app.py', 'r') as f:
        app_content = f.read()
    
    # Replace the API endpoint with team code lookup
    new_api_code = '''@app.route('/api/player-fixture-history')
def get_player_fixture_history():
    """Serve player fixture history data using team codes"""
    try:
        player_name = request.args.get('player_name', '')
        opponent_team_id = request.args.get('opponent_team_id', '')
        
        if not player_name or not opponent_team_id:
            return jsonify({'error': 'Missing player_name or opponent_team_id parameter'}), 400
        
        # Map current team ID to team code
        team_id_to_code = {
            '1': '3',   # Arsenal
            '2': '7',   # Aston Villa
            '4': '91',  # Bournemouth
            '5': '94',  # Brentford
            '6': '36',  # Brighton
            '7': '8',   # Chelsea
            '8': '31',  # Crystal Palace
            '9': '11',  # Everton
            '10': '54', # Fulham
            '11': '2',  # Leeds
            '12': '14', # Liverpool
            '13': '43', # Man City
            '14': '1',  # Man Utd
            '15': '4',  # Newcastle
            '16': '17', # Nott'm Forest
            '17': '56', # Sunderland
            '18': '6',  # Spurs
            '19': '21', # West Ham
            '20': '39', # Wolves
        }
        
        team_code = team_id_to_code.get(opponent_team_id)
        
        if not team_code:
            return jsonify({
                'fixtures': [],
                'is_new_player': False
            })
        
        # Load real historical data
        with open('data/player-history.json', 'r') as f:
            history_data = json.load(f)
        
        # Find the player's data by name
        if player_name in history_data['data']:
            player_data = history_data['data'][player_name]
            
            # Find the opponent's data using team code
            if team_code in player_data:
                return jsonify(player_data[team_code])
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
    pattern = r'@app\.route\(\'/api/player-fixture-history\'\)\s*def get_player_fixture_history\(\):.*?return jsonify\(\{\'error\': str\(e\)\}\)\, 500'
    replacement = new_api_code
    
    updated_content = re.sub(pattern, replacement, app_content, flags=re.DOTALL)
    
    # Write the updated content
    with open('app.py', 'w') as f:
        f.write(updated_content)
    
    print("✅ Updated API to use team codes")

def verify_data():
    """Verify the rebuilt data"""
    print("\n🔍 Verifying data...")
    
    # Load the rebuilt data
    with open('data/player-history.json', 'r') as f:
        history_data = json.load(f)
    
    # Check key players
    key_players = ['M.Salah', 'Luis Díaz', 'Haaland']
    
    for player in key_players:
        if player in history_data['data']:
            fixtures_count = sum(len(data['fixtures']) for data in history_data['data'][player].values())
            print(f"✅ {player}: {fixtures_count} fixtures found")
        else:
            print(f"❌ {player}: Not found")
    
    # Check specific matchups using team codes
    test_cases = [
        ('M.Salah', '91', 'Bournemouth'),
        ('Luis Díaz', '91', 'Bournemouth'),
        ('Haaland', '14', 'Liverpool')
    ]
    
    for player_name, team_code, team_name in test_cases:
        if player_name in history_data['data'] and team_code in history_data['data'][player_name]:
            fixtures = history_data['data'][player_name][team_code]['fixtures']
            if fixtures:
                max_points = max(f['total_points'] for f in fixtures)
                print(f"✅ {player_name} vs {team_name}: {len(fixtures)} fixtures, max {max_points} points")
            else:
                print(f"⚠️  {player_name} vs {team_name}: No fixtures")
        else:
            print(f"❌ {player_name} vs {team_name}: Not found")

def main():
    """Main rebuilding function"""
    print("🚀 REBUILDING HISTORICAL DATA WITH TEAM CODES")
    print("=" * 60)
    
    # Step 1: Create new player history JSON
    player_history_data = create_player_history_json()
    
    # Step 2: Update API for team codes
    update_api_for_team_codes()
    
    # Step 3: Verify the data
    verify_data()
    
    print("\n🎉 HISTORICAL DATA REBUILD COMPLETE!")
    print("📊 Using team codes (stable) instead of team IDs (unstable)")

if __name__ == "__main__":
    main() 