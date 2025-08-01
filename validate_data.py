import json
import os
from datetime import datetime

def validate_json_file(file_path, required_fields=None):
    """Validate a JSON file exists and has required structure"""
    try:
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check for last_updated field
        if 'last_updated' not in data:
            return False, f"Missing last_updated field in {file_path}"
        
        # Check for data field (if required)
        if required_fields:
            if 'data' not in data:
                return False, f"Missing data field in {file_path}"
            
            if not isinstance(data['data'], list):
                return False, f"Data field is not a list in {file_path}"
            
            if len(data['data']) == 0:
                return False, f"Data field is empty in {file_path}"
        
        return True, f"✅ {file_path} is valid"
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in {file_path}: {e}"
    except Exception as e:
        return False, f"Error reading {file_path}: {e}"

def validate_teams_data():
    """Validate teams.json"""
    required_fields = ['id', 'name', 'short_name', 'code']
    
    is_valid, message = validate_json_file('data/teams.json', required_fields)
    if not is_valid:
        return False, message
    
    with open('data/teams.json', 'r') as f:
        data = json.load(f)
    
    # Check for required fields in each team
    for i, team in enumerate(data['data']):
        for field in required_fields:
            if field not in team:
                return False, f"Team {i} missing required field: {field}"
    
    return True, f"✅ Teams data valid: {len(data['data'])} teams"

def validate_players_data():
    """Validate players.json"""
    required_fields = ['id', 'web_name', 'element_type', 'team_id']
    
    is_valid, message = validate_json_file('data/players.json', required_fields)
    if not is_valid:
        return False, message
    
    with open('data/players.json', 'r') as f:
        data = json.load(f)
    
    # Check for required fields in each player
    for i, player in enumerate(data['data']):
        for field in required_fields:
            if field not in player:
                return False, f"Player {i} missing required field: {field}"
    
    return True, f"✅ Players data valid: {len(data['data'])} players"

def validate_fixtures_data():
    """Validate fixtures.json"""
    required_fields = ['id', 'event', 'team_h', 'team_a']
    
    is_valid, message = validate_json_file('data/fixtures.json', required_fields)
    if not is_valid:
        return False, message
    
    with open('data/fixtures.json', 'r') as f:
        data = json.load(f)
    
    # Check for required fields in each fixture
    for i, fixture in enumerate(data['data']):
        for field in required_fields:
            if field not in fixture:
                return False, f"Fixture {i} missing required field: {field}"
    
    return True, f"✅ Fixtures data valid: {len(data['data'])} fixtures"

def validate_team_stats_data():
    """Validate team-stats.json"""
    is_valid, message = validate_json_file('data/team-stats.json')
    if not is_valid:
        return False, message
    
    with open('data/team-stats.json', 'r') as f:
        data = json.load(f)
    
    # Check for required locations
    required_locations = ['home', 'away', 'overall']
    for location in required_locations:
        if location not in data:
            return False, f"Missing {location} stats in team-stats.json"
        
        if not isinstance(data[location], list):
            return False, f"{location} stats is not a list"
        
        if len(data[location]) == 0:
            return False, f"{location} stats is empty"
    
    return True, f"✅ Team stats valid: {len(data['home'])} home, {len(data['away'])} away, {len(data['overall'])} overall"

def validate_team_rankings_data():
    """Validate team-rankings.json"""
    is_valid, message = validate_json_file('data/team-rankings.json')
    if not is_valid:
        return False, message
    
    with open('data/team-rankings.json', 'r') as f:
        data = json.load(f)
    
    # Check for required ranking types
    required_types = ['attack', 'defense']
    for ranking_type in required_types:
        if ranking_type not in data:
            return False, f"Missing {ranking_type} rankings in team-rankings.json"
        
        if not isinstance(data[ranking_type], list):
            return False, f"{ranking_type} rankings is not a list"
        
        if len(data[ranking_type]) == 0:
            return False, f"{ranking_type} rankings is empty"
    
    return True, f"✅ Team rankings valid: {len(data['attack'])} attack, {len(data['defense'])} defense"

def check_data_freshness():
    """Check if data is recent (within last 24 hours)"""
    data_files = [
        'data/teams.json',
        'data/players.json',
        'data/fixtures.json',
        'data/team-stats.json',
        'data/team-rankings.json'
    ]
    
    current_time = datetime.now()
    freshness_issues = []
    
    for file_path in data_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                last_updated_str = data.get('last_updated', '')
                if last_updated_str:
                    last_updated = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))
                    time_diff = current_time - last_updated.replace(tzinfo=None)
                    
                    if time_diff.days > 1:
                        freshness_issues.append(f"{file_path}: {time_diff.days} days old")
                else:
                    freshness_issues.append(f"{file_path}: No last_updated field")
            except Exception as e:
                freshness_issues.append(f"{file_path}: Error checking freshness - {e}")
        else:
            freshness_issues.append(f"{file_path}: File not found")
    
    return freshness_issues

def main():
    """Main validation function"""
    print("🔍 Validating FPL data files...")
    print("=" * 50)
    
    # Check if data directory exists
    if not os.path.exists('data'):
        print("❌ Data directory not found!")
        return False
    
    # Validate each data file
    validations = [
        validate_teams_data,
        validate_players_data,
        validate_fixtures_data,
        validate_team_stats_data,
        validate_team_rankings_data
    ]
    
    all_valid = True
    for validation in validations:
        is_valid, message = validation()
        print(message)
        if not is_valid:
            all_valid = False
    
    # Check data freshness
    print("\n📅 Checking data freshness...")
    freshness_issues = check_data_freshness()
    if freshness_issues:
        print("⚠️  Data freshness issues:")
        for issue in freshness_issues:
            print(f"   - {issue}")
    else:
        print("✅ All data files are recent")
    
    # Summary
    print("\n" + "=" * 50)
    if all_valid and not freshness_issues:
        print("🎉 All data validation passed!")
        return True
    else:
        print("❌ Data validation failed!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 