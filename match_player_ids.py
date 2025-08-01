import csv
import json
import os
from collections import defaultdict

def load_current_players():
    """Load current player data from JSON"""
    with open('data/players.json', 'r') as f:
        data = json.load(f)
    
    # Create a mapping of (name, team) -> current_id
    player_mapping = {}
    name_variations = defaultdict(list)
    
    for player in data['data']:
        name = player['web_name'].lower().strip()
        team = player['team_name'].lower().strip()
        current_id = player['id']
        
        # Store the mapping
        key = (name, team)
        player_mapping[key] = current_id
        
        # Also store variations for fuzzy matching
        name_variations[name].append((team, current_id))
        
        # Handle common name variations
        if ' ' in name:
            # Store first name only
            first_name = name.split(' ')[0]
            name_variations[first_name].append((team, current_id))
            
            # Store last name only
            last_name = name.split(' ')[-1]
            name_variations[last_name].append((team, current_id))
    
    return player_mapping, name_variations

def find_player_match(historical_name, historical_team, player_mapping, name_variations):
    """Find the current player ID for a historical player"""
    historical_name = historical_name.lower().strip()
    historical_team = historical_team.lower().strip()
    
    # Try exact match first
    key = (historical_name, historical_team)
    if key in player_mapping:
        return player_mapping[key]
    
    # Try fuzzy matching
    if historical_name in name_variations:
        candidates = name_variations[historical_name]
        for team, player_id in candidates:
            if team == historical_team:
                return player_id
    
    # Try matching by first name + team
    if ' ' in historical_name:
        first_name = historical_name.split(' ')[0]
        if first_name in name_variations:
            candidates = name_variations[first_name]
            for team, player_id in candidates:
                if team == historical_team:
                    return player_id
    
    # Try matching by last name + team
    if ' ' in historical_name:
        last_name = historical_name.split(' ')[-1]
        if last_name in name_variations:
            candidates = name_variations[last_name]
            for team, player_id in candidates:
                if team == historical_team:
                    return player_id
    
    return None

def process_historical_data():
    """Process the historical CSV and match with current player IDs"""
    csv_path = os.path.expanduser('~/Desktop/player_gameweek_stats.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found at {csv_path}")
        return
    
    # Load current player data
    player_mapping, name_variations = load_current_players()
    
    # Load team mapping for historical team IDs
    with open('data/teams.json', 'r') as f:
        teams_data = json.load(f)
    
    team_id_to_name = {}
    for team in teams_data['data']:
        team_id_to_name[str(team['id'])] = team['short_name']
    
    # Process the CSV
    matched_records = []
    unmatched_records = []
    match_count = 0
    
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            historical_player_id = row['player_id']
            historical_team_id = row['opponent_team']
            
            # We need to get the player name and team from somewhere
            # For now, let's assume we need to look this up
            # You might need to provide a mapping or additional data
            
            # For demonstration, let's create a sample mapping
            # In reality, you'd need the historical player names and teams
            
            # This is a placeholder - you'll need to provide the actual historical player data
            historical_player_name = f"Player_{historical_player_id}"  # Placeholder
            historical_team_name = team_id_to_name.get(historical_team_id, f"Team_{historical_team_id}")
            
            # Try to find a match
            current_player_id = find_player_match(historical_player_name, historical_team_name, player_mapping, name_variations)
            
            if current_player_id:
                # Update the record with current player ID
                row['current_player_id'] = current_player_id
                row['matched'] = 'YES'
                matched_records.append(row)
                match_count += 1
            else:
                # Keep original record but mark as unmatched
                row['current_player_id'] = ''
                row['matched'] = 'NO'
                unmatched_records.append(row)
    
    # Save the processed data
    output_path = 'data/player_gameweek_stats_matched.csv'
    
    if matched_records:
        fieldnames = list(matched_records[0].keys())
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write matched records first
            for record in matched_records:
                writer.writerow(record)
            
            # Write unmatched records
            for record in unmatched_records:
                writer.writerow(record)
        
        print(f"✅ Processed {len(matched_records) + len(unmatched_records)} records")
        print(f"✅ Matched {match_count} players")
        print(f"❌ Unmatched {len(unmatched_records)} players")
        print(f"📁 Output saved to {output_path}")
        
        # Show some examples of matches
        print("\n📋 Sample matches:")
        for i, record in enumerate(matched_records[:5]):
            print(f"  Historical ID {record['player_id']} -> Current ID {record['current_player_id']}")
        
        if unmatched_records:
            print(f"\n⚠️  Sample unmatched records:")
            for i, record in enumerate(unmatched_records[:5]):
                print(f"  Historical ID {record['player_id']} (Team {record['opponent_team']}) - No match found")
    
    else:
        print("❌ No records processed. Check the CSV format and data.")

def create_player_name_mapping():
    """Create a mapping file to help with manual matching"""
    csv_path = os.path.expanduser('~/Desktop/player_gameweek_stats.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found at {csv_path}")
        return
    
    # Get unique player IDs from historical data
    historical_player_ids = set()
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            historical_player_ids.add(row['player_id'])
    
    # Load current players
    with open('data/players.json', 'r') as f:
        current_players = json.load(f)
    
    # Create a mapping file for manual review
    mapping_path = 'data/player_id_mapping.csv'
    
    with open(mapping_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['historical_player_id', 'suggested_current_name', 'suggested_current_team', 'suggested_current_id', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for historical_id in sorted(historical_player_ids, key=int):
            writer.writerow({
                'historical_player_id': historical_id,
                'suggested_current_name': '',
                'suggested_current_team': '',
                'suggested_current_id': '',
                'notes': 'Fill in the current player name and team for this historical ID'
            })
    
    print(f"📁 Created mapping template at {mapping_path}")
    print(f"📝 Please fill in the current player names for {len(historical_player_ids)} historical player IDs")

if __name__ == "__main__":
    print("🔍 Player ID Matching Tool")
    print("1. Create mapping template")
    print("2. Process with automatic matching")
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        create_player_name_mapping()
    elif choice == "2":
        process_historical_data()
    else:
        print("Invalid choice. Please run again and choose 1 or 2.") 