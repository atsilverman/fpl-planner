import csv
import json
import os

def debug_team_mapping():
    """Debug the team mapping process"""
    print("🔍 DEBUGGING TEAM MAPPING")
    
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
            teams_2025[row['id']] = {
                'code': row['code'],
                'name': row['name'],
                'short_name': row['short_name']
            }
    
    print("\n📋 2024/25 Teams:")
    for team_id, team in teams_2024.items():
        print(f"  ID {team_id}: {team['name']} (Code: {team['code']})")
    
    print("\n📋 2025/26 Teams:")
    for team_id, team in teams_2025.items():
        print(f"  ID {team_id}: {team['name']} (Code: {team['code']})")
    
    # Test mapping
    print("\n🔍 Testing team mapping:")
    for hist_id, hist_team in teams_2024.items():
        # Find team with same code in 2025
        for curr_id, curr_team in teams_2025.items():
            if hist_team['code'] == curr_team['code']:
                print(f"  {hist_team['name']}: {hist_id} → {curr_id} (Code: {hist_team['code']})")
                break

def debug_player_mapping():
    """Debug the player mapping process"""
    print("\n🔍 DEBUGGING PLAYER MAPPING")
    
    # Load sample players
    players_2024 = {}
    with open(os.path.expanduser('~/Desktop/players.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['web_name'] in ['M.Salah', 'Luis Díaz', 'Haaland', 'De Bruyne']:
                players_2024[row['id']] = {
                    'web_name': row['web_name'],
                    'team_id': row['team_id']
                }
    
    players_2025 = {}
    with open(os.path.expanduser('~/Desktop/players_2025.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['web_name'] in ['M.Salah', 'Luis Díaz', 'Haaland', 'De Bruyne']:
                players_2025[row['id']] = {
                    'web_name': row['web_name'],
                    'team_id': row['team_id']
                }
    
    print("\n📋 2024/25 Key Players:")
    for player_id, player in players_2024.items():
        print(f"  ID {player_id}: {player['web_name']} (Team: {player['team_id']})")
    
    print("\n📋 2025/26 Key Players:")
    for player_id, player in players_2025.items():
        print(f"  ID {player_id}: {player['web_name']} (Team: {player['team_id']})")

def debug_historical_data():
    """Debug the historical data processing"""
    print("\n🔍 DEBUGGING HISTORICAL DATA")
    
    # Check a few records from the historical data
    with open(os.path.expanduser('~/Desktop/player_gameweek_stats.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            if count < 10:
                print(f"  Player {row['player_id']} vs Team {row['opponent_team']} in GW {row['gameweek']}: {row['total_points']} points")
                count += 1
            else:
                break

if __name__ == "__main__":
    debug_team_mapping()
    debug_player_mapping()
    debug_historical_data() 