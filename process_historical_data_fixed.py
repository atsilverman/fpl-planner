import csv
import json
import os
from collections import defaultdict

def load_team_mappings():
    """Load and create mappings between historical and current team IDs using team codes"""
    
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
    
    # Create team ID mapping using codes
    team_id_mapping = {}
    code_to_current_id = {}
    
    # Create mapping from code to current team ID
    for curr_id, curr_team in current_teams.items():
        code_to_current_id[curr_team['code']] = curr_id
    
    # Map historical team IDs to current team IDs
    for hist_id, hist_team in historical_teams.items():
        if hist_team['code'] in code_to_current_id:
            team_id_mapping[hist_id] = code_to_current_id[hist_team['code']]
    
    print(f"✅ Created team mappings for {len(team_id_mapping)} teams")
    
    # Show some examples
    print("\n📋 Sample team mappings:")
    for hist_id, curr_id in list(team_id_mapping.items())[:5]:
        hist_team = historical_teams[hist_id]
        curr_team = current_teams[curr_id]
        print(f"  {hist_team['name']} (ID {hist_id} → {curr_id}) - Code: {hist_team['code']}")
    
    return historical_teams, current_teams, team_id_mapping

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
    """Process the historical gameweek stats with correct team and player mappings"""
    
    historical_teams, current_teams, team_id_mapping = load_team_mappings()
    historical_players, current_players, name_mapping = load_player_mappings()
    
    # Process historical gameweek stats
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
            
            # Try to find current team ID using team mapping
            current_opponent_team_id = team_id_mapping.get(historical_opponent_team_id)
            
            if current_player_id and current_opponent_team_id:
                # Get current player info
                current_player = current_players.get(current_player_id)
                current_team = current_teams.get(current_opponent_team_id)
                
                if current_player and current_team:
                    # Create processed record
                    processed_record = {
                        'player_id': current_player_id,
                        'player_name': current_player['web_name'],
                        'team_id': current_player['team_id'],
                        'gameweek': int(row['gameweek']),
                        'opponent_team_id': int(current_opponent_team_id),
                        'opponent_team_name': current_team['short_name'],
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
                    key = (current_player_id, current_opponent_team_id)
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

def verify_luis_diaz_bournemouth():
    """Verify Luis Díaz's performance against Bournemouth"""
    
    # Load the processed data
    with open('data/player-history.json', 'r') as f:
        history_data = json.load(f)
    
    # Find Luis Díaz
    luis_diaz_name = None
    for player_name in history_data['data'].keys():
        if 'díaz' in player_name.lower() or 'diaz' in player_name.lower():
            luis_diaz_name = player_name
            break
    
    if luis_diaz_name:
        print(f"\n🔍 Found Luis Díaz: {luis_diaz_name}")
        
        # Find Bournemouth's current team ID
        current_teams = {}
        with open(os.path.expanduser('~/Desktop/teams_2025.csv'), 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'bournemouth' in row['name'].lower():
                    bournemouth_id = row['id']
                    print(f"📍 Bournemouth current ID: {bournemouth_id}")
                    break
        
        # Check Luis Díaz's performance against Bournemouth
        if bournemouth_id in history_data['data'][luis_diaz_name]:
            fixtures = history_data['data'][luis_diaz_name][bournemouth_id]['fixtures']
            print(f"📊 Luis Díaz vs Bournemouth - {len(fixtures)} fixtures:")
            
            for fixture in fixtures:
                home_away = "HOME" if fixture['was_home'] else "AWAY"
                print(f"  GW{fixture['gameweek']} ({home_away}): {fixture['total_points']} points")
                
                if fixture['total_points'] == 16:
                    print(f"    🎯 FOUND 16 POINTS! GW{fixture['gameweek']} ({home_away})")
        else:
            print("❌ No fixtures found against Bournemouth")
    else:
        print("❌ Luis Díaz not found in processed data")

def main():
    """Main processing function"""
    print("🚀 Processing Historical Data with Correct Team Mappings...")
    
    # Create the player history JSON
    player_history_data = create_player_history_json()
    
    # Verify Luis Díaz's performance
    verify_luis_diaz_bournemouth()
    
    print("\n🎉 Historical data processing complete!")
    print("📊 The website will now show real historical data with correct team mappings")

if __name__ == "__main__":
    from datetime import datetime
    main() 