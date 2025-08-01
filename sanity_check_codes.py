import csv
import json
import os

def check_team_code_mappings():
    """Check team code mappings between 2024 and 2025"""
    print("🔍 TEAM CODE MAPPINGS (2024 → 2025)")
    print("=" * 50)
    
    # Load 2024/25 teams
    teams_2024 = {}
    with open('data/teams_2024.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            teams_2024[row['code']] = {
                'id': row['id'],
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
    
    print(f"{'Team Name':<20} {'2024 Code':<10} {'2025 Code':<10} {'2024 ID':<8} {'2025 ID':<8}")
    print("-" * 60)
    
    # Show all teams that exist in both years
    for code in sorted(teams_2024.keys()):
        if code in teams_2025:
            team_2024 = teams_2024[code]
            team_2025 = teams_2025[code]
            print(f"{team_2024['name']:<20} {code:<10} {code:<10} {team_2024['id']:<8} {team_2025['id']:<8}")

def check_sample_players():
    """Check sample high-value players and their team codes"""
    print("\n🔍 SAMPLE PLAYERS WITH TEAM CODES")
    print("=" * 50)
    
    # Load 2025/26 players (sorted by price)
    players_2025 = []
    with open(os.path.expanduser('~/Desktop/players_2025.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            players_2025.append({
                'web_name': row['web_name'],
                'team_id': row['team_id'],
                'now_cost': float(row['now_cost']) if row['now_cost'] else 0
            })
    
    # Sort by price (highest first) and take top 20
    players_2025.sort(key=lambda x: x['now_cost'], reverse=True)
    top_players = players_2025[:20]
    
    # Load team data to get codes
    teams_2025 = {}
    with open('data/teams_2025.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            teams_2025[row['id']] = {
                'code': row['code'],
                'name': row['name'],
                'short_name': row['short_name']
            }
    
    print(f"{'Player Name':<20} {'Team':<15} {'2025 Code':<10} {'2025 ID':<8} {'Price':<8}")
    print("-" * 65)
    
    for player in top_players:
        team_info = teams_2025.get(player['team_id'], {})
        team_name = team_info.get('name', 'Unknown')
        team_code = team_info.get('code', 'Unknown')
        print(f"{player['web_name']:<20} {team_name:<15} {team_code:<10} {player['team_id']:<8} {player['now_cost']:<8}")

def check_historical_data_structure():
    """Check what team codes are actually in the historical data"""
    print("\n🔍 HISTORICAL DATA TEAM CODES")
    print("=" * 50)
    
    # Load the historical data
    with open('data/player-history.json', 'r') as f:
        history_data = json.load(f)
    
    # Get all unique team IDs from the historical data
    all_team_ids = set()
    for player_name, player_data in history_data['data'].items():
        for team_id in player_data.keys():
            all_team_ids.add(team_id)
    
    print("Team IDs found in historical data:")
    for team_id in sorted(all_team_ids, key=int):
        print(f"  {team_id}")
    
    # Check what these team IDs represent
    teams_2024 = {}
    with open('data/teams_2024.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            teams_2024[row['id']] = {
                'code': row['code'],
                'name': row['name']
            }
    
    print("\nTeam ID to Code mapping in 2024:")
    for team_id in sorted(all_team_ids, key=int):
        if team_id in teams_2024:
            team = teams_2024[team_id]
            print(f"  ID {team_id}: {team['name']} (Code: {team['code']})")
        else:
            print(f"  ID {team_id}: Unknown")

if __name__ == "__main__":
    check_team_code_mappings()
    check_sample_players()
    check_historical_data_structure() 