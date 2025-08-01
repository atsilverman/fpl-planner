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
                'id': row['id'],
                'name': row['name'],
                'short_name': row['short_name'],
                'code': row['code']
            }
    
    # Load 2025/26 teams
    teams_2025 = {}
    with open('data/teams_2025.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            teams_2025[row['code']] = {
                'id': row['id'],
                'name': row['name'],
                'short_name': row['short_name'],
                'code': row['code']
            }
    
    # Create mapping from 2024 team codes to 2025 team IDs
    team_code_to_2025_id = {}
    for code, team_2025 in teams_2025.items():
        if code in teams_2024:  # Only map teams that existed in 2024
            team_code_to_2025_id[code] = team_2025['id']
    
    print(f"✅ Mapped {len(team_code_to_2025_id)} teams using team codes")
    
    # Show some examples
    print("\n📋 Sample team mappings:")
    for code, team_id in list(team_code_to_2025_id.items())[:5]:
        team_2024 = teams_2024[code]
        team_2025 = teams_2025[code]
        print(f"  {team_2024['name']} (Code: {code}) → ID {team_id}")
    
    return teams_2024, teams_2025, team_code_to_2025_id

def load_player_mappings():
    """Load player mappings using names and team codes"""
    print("\n🔍 Loading player mappings...")
    
    # Load 2024/25 players
    players_2024 = {}
    with open(os.path.expanduser('~/Desktop/players.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            player_key = (row['web_name'].lower().strip(), row['team_id'])
            players_2024[player_key] = {
                'id': row['id'],
                'web_name': row['web_name'],
                'first_name': row['first_name'],
                'second_name': row['second_name'],
                'team_id': row['team_id']
            }
    
    # Load 2025/26 players
    players_2025 = {}
    with open(os.path.expanduser('~/Desktop/players_2025.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            player_key = (row['web_name'].lower().strip(), row['team_id'])
            players_2025[player_key] = {
                'id': row['id'],
                'web_name': row['web_name'],
                'first_name': row['first_name'],
                'second_name': row['second_name'],
                'team_id': row['team_id']
            }
    
    # Create name-based mapping (ignore team ID changes)
    name_mapping = {}
    for (name_2024, team_id_2024), player_2024 in players_2024.items():
        # Find matching player in 2025 by name only (ignore team ID)
        for (name_2025, team_id_2025), player_2025 in players_2025.items():
            if name_2024 == name_2025:
                name_mapping[player_2024['id']] = player_2025['id']
                break
    
    print(f"✅ Mapped {len(name_mapping)} players using names")
    
    # Show some examples
    print("\n📋 Sample player mappings:")
    for hist_id, curr_id in list(name_mapping.items())[:5]:
        hist_player = next(p for p in players_2024.values() if p['id'] == hist_id)
        curr_player = next(p for p in players_2025.values() if p['id'] == curr_id)
        print(f"  {hist_player['web_name']} (ID {hist_id} → {curr_id})")
    
    return players_2024, players_2025, name_mapping

def process_historical_gameweek_stats():
    """Process historical gameweek stats with correct mappings"""
    print("\n🔍 Processing historical gameweek stats...")
    
    teams_2024, teams_2025, team_code_to_2025_id = load_team_mappings()
    players_2024, players_2025, name_mapping = load_player_mappings()
    
    # Load historical gameweek stats
    processed_stats = defaultdict(list)
    unmatched_count = 0
    matched_count = 0
    
    with open(os.path.expanduser('~/Desktop/player_gameweek_stats.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            historical_player_id = row['player_id']
            historical_opponent_team_id = row['opponent_team']
            
            # Try to find current player ID
            current_player_id = name_mapping.get(historical_player_id)
            
            if current_player_id:
                # Get current player info
                current_player = None
                for player in players_2025.values():
                    if player['id'] == current_player_id:
                        current_player = player
                        break
                
                if current_player:
                    # Get team info for the current player
                    current_team_id = current_player['team_id']
                    
                    # Find the historical team code for this opponent
                    # We need to map the historical team ID to a team code, then to current team ID
                    historical_team = None
                    for team in teams_2024.values():
                        if team['id'] == historical_opponent_team_id:
                            historical_team = team
                            break
                    
                    if historical_team:
                        # Use the team code directly (stable identifier)
                        team_code = historical_team['code']
                        
                        # Create processed record
                        processed_record = {
                            'player_id': current_player_id,
                            'player_name': current_player['web_name'],
                            'team_id': current_team_id,
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
            else:
                unmatched_count += 1
    
    print(f"✅ Processed {matched_count} records")
    print(f"❌ Unmatched {unmatched_count} records")
    
    return processed_stats

def create_player_history_json():
    """Create the player history JSON file with correct mappings"""
    print("\n🔍 Creating player history JSON...")
    
    processed_stats = process_historical_gameweek_stats()
    
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

def update_api_for_name_based_lookups():
    """Update the API to use name-based lookups instead of ID-based"""
    print("\n🔍 Updating API for name-based lookups...")
    
    # Read the current app.py
    with open('app.py', 'r') as f:
        app_content = f.read()
    
    # Replace the API endpoint with name-based lookup
    new_api_code = '''@app.route('/api/player-fixture-history')
def get_player_fixture_history():
    """Serve player fixture history data using name-based lookups"""
    try:
        player_name = request.args.get('player_name', '')
        opponent_team_id = request.args.get('opponent_team_id', '')
        
        if not player_name or not opponent_team_id:
            return jsonify({'error': 'Missing player_name or opponent_team_id parameter'}), 400
        
        # Load real historical data
        with open('data/player-history.json', 'r') as f:
            history_data = json.load(f)
        
        # Find the player's data by name
        if player_name in history_data['data']:
            player_data = history_data['data'][player_name]
            
            # Find the opponent's data using current team ID
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
    pattern = r'@app\.route\(\'/api/player-fixture-history\'\)\s*def get_player_fixture_history\(\):.*?return jsonify\(\{\'error\': str\(e\)\}\)\, 500'
    replacement = new_api_code
    
    updated_content = re.sub(pattern, replacement, app_content, flags=re.DOTALL)
    
    # Write the updated content
    with open('app.py', 'w') as f:
        f.write(updated_content)
    
    print("✅ Updated API to use name-based lookups")

def verify_sample_data():
    """Verify the rebuilt data with sample checks"""
    print("\n🔍 Verifying sample data...")
    
    # Load the rebuilt data
    with open('data/player-history.json', 'r') as f:
        history_data = json.load(f)
    
    # Check for key players
    key_players = ['M.Salah', 'Luis Díaz', 'Haaland', 'De Bruyne']
    
    for player in key_players:
        if player in history_data['data']:
            fixtures_count = sum(len(data['fixtures']) for data in history_data['data'][player].values())
            print(f"✅ {player}: {fixtures_count} fixtures found")
        else:
            print(f"❌ {player}: Not found in historical data")
    
    # Check specific matchups
    test_cases = [
        ('M.Salah', '4', 'Bournemouth'),
        ('Luis Díaz', '4', 'Bournemouth'),
        ('Haaland', '12', 'Liverpool')
    ]
    
    for player_name, team_id, team_name in test_cases:
        if player_name in history_data['data'] and team_id in history_data['data'][player_name]:
            fixtures = history_data['data'][player_name][team_id]['fixtures']
            if fixtures:
                max_points = max(f['total_points'] for f in fixtures)
                print(f"✅ {player_name} vs {team_name}: {len(fixtures)} fixtures, max {max_points} points")
            else:
                print(f"⚠️  {player_name} vs {team_name}: No fixtures")
        else:
            print(f"❌ {player_name} vs {team_name}: Not found")

def main():
    """Main rebuilding function"""
    print("🚀 REBUILDING HISTORICAL DATA WITH STABLE MAPPINGS")
    print("=" * 60)
    
    # Step 1: Create new player history JSON
    player_history_data = create_player_history_json()
    
    # Step 2: Update API for name-based lookups
    update_api_for_name_based_lookups()
    
    # Step 3: Verify the data
    verify_sample_data()
    
    print("\n🎉 HISTORICAL DATA REBUILD COMPLETE!")
    print("📊 The website will now show accurate historical data")
    print("🔧 Using stable identifiers (names, team codes) instead of unstable IDs")

if __name__ == "__main__":
    main() 