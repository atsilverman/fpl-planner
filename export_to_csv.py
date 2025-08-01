import json
import csv
import os
from datetime import datetime

def export_players_to_csv():
    """Export players data to CSV"""
    try:
        with open('data/players.json', 'r') as f:
            data = json.load(f)
        
        players = data['data']
        
        # Define CSV headers based on the data structure
        headers = [
            'id', 'web_name', 'element_type', 'now_cost', 'team_id', 'team_name',
            'total_points', 'goals_scored', 'assists', 'expected_goals', 'expected_assists',
            'clean_sheets', 'goals_conceded', 'bonus', 'saves', 'minutes', 'last_cost', 'team_rank'
        ]
        
        with open('data/players.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for player in players:
                # Create a row with all fields, using empty string for missing values
                row = {}
                for header in headers:
                    row[header] = player.get(header, '')
                writer.writerow(row)
        
        print(f"✅ Exported {len(players)} players to data/players.csv")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting players to CSV: {e}")
        return False

def export_teams_to_csv():
    """Export teams data to CSV"""
    try:
        with open('data/teams.json', 'r') as f:
            data = json.load(f)
        
        teams = data['data']
        
        headers = [
            'id', 'name', 'short_name', 'code', 'strength', 'atk_h', 'atk_a', 'def_h', 'def_a',
            'atk_h_rank', 'atk_a_rank', 'def_h_rank', 'def_a_rank'
        ]
        
        with open('data/teams.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for team in teams:
                row = {}
                for header in headers:
                    row[header] = team.get(header, '')
                writer.writerow(row)
        
        print(f"✅ Exported {len(teams)} teams to data/teams.csv")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting teams to CSV: {e}")
        return False

def export_fixtures_to_csv():
    """Export fixtures data to CSV"""
    try:
        with open('data/fixtures.json', 'r') as f:
            data = json.load(f)
        
        fixtures = data['data']
        
        headers = [
            'id', 'event', 'kickoff_time', 'team_h', 'team_a', 'team_h_difficulty', 'team_a_difficulty',
            'team_h_score', 'team_a_score', 'finished', 'minutes', 'provisional_start_time',
            'pulse_id', 'started', 'team_h_difficulty_rank', 'team_a_difficulty_rank'
        ]
        
        with open('data/fixtures.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for fixture in fixtures:
                row = {}
                for header in headers:
                    row[header] = fixture.get(header, '')
                writer.writerow(row)
        
        print(f"✅ Exported {len(fixtures)} fixtures to data/fixtures.csv")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting fixtures to CSV: {e}")
        return False

def export_team_stats_to_csv():
    """Export team stats data to CSV"""
    try:
        with open('data/team-stats.json', 'r') as f:
            data = json.load(f)
        
        # Export each location's stats
        for location in ['overall', 'home', 'away']:
            if location in data:
                stats = data[location]
                
                # Get headers from the first team's stats
                if stats:
                    first_team = list(stats.values())[0]
                    headers = list(first_team.keys())
                    headers.insert(0, 'team_id')  # Add team_id as first column
                    
                    filename = f'data/team-stats-{location}.csv'
                    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=headers)
                        writer.writeheader()
                        
                        for team_id, team_stats in stats.items():
                            row = {'team_id': team_id}
                            for header in headers[1:]:  # Skip team_id as it's already added
                                row[header] = team_stats.get(header, '')
                            writer.writerow(row)
                    
                    print(f"✅ Exported {len(stats)} team stats ({location}) to {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error exporting team stats to CSV: {e}")
        return False

def export_team_rankings_to_csv():
    """Export team rankings data to CSV"""
    try:
        with open('data/team-rankings.json', 'r') as f:
            data = json.load(f)
        
        # Export each type's rankings
        for ranking_type in ['attack', 'defense']:
            if ranking_type in data:
                rankings = data[ranking_type]
                
                headers = ['rank', 'team_id', 'team_name', 'short_name', 'value']
                
                filename = f'data/team-rankings-{ranking_type}.csv'
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=headers)
                    writer.writeheader()
                    
                    for rank, team_data in rankings.items():
                        row = {
                            'rank': rank,
                            'team_id': team_data.get('team_id', ''),
                            'team_name': team_data.get('team_name', ''),
                            'short_name': team_data.get('short_name', ''),
                            'value': team_data.get('value', '')
                        }
                        writer.writerow(row)
                
                print(f"✅ Exported {len(rankings)} team rankings ({ranking_type}) to {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error exporting team rankings to CSV: {e}")
        return False

def export_player_history_to_csv():
    """Export player history data to CSV (if available)"""
    try:
        with open('data/player-history.json', 'r') as f:
            data = json.load(f)
        
        # This is currently sample data, but we can export it for structure
        if 'data' in data and 'default' in data['data']:
            fixtures = data['data']['default']['fixtures']
            
            headers = [
                'gameweek', 'total_points', 'minutes', 'goals_scored', 'assists',
                'clean_sheets', 'bonus', 'expected_goals', 'expected_assists', 'was_home'
            ]
            
            with open('data/player-history-sample.csv', 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                for fixture in fixtures:
                    row = {}
                    for header in headers:
                        row[header] = fixture.get(header, '')
                    writer.writerow(row)
            
            print(f"✅ Exported {len(fixtures)} sample player history records to data/player-history-sample.csv")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error exporting player history to CSV: {e}")
        return False

def main():
    """Export all data to CSV format"""
    print("🚀 Starting CSV export...")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    success_count = 0
    total_exports = 6
    
    # Export each data type
    if export_players_to_csv():
        success_count += 1
    
    if export_teams_to_csv():
        success_count += 1
    
    if export_fixtures_to_csv():
        success_count += 1
    
    if export_team_stats_to_csv():
        success_count += 1
    
    if export_team_rankings_to_csv():
        success_count += 1
    
    if export_player_history_to_csv():
        success_count += 1
    
    print(f"\n📊 CSV Export Complete: {success_count}/{total_exports} successful")
    print(f"📁 CSV files saved in the 'data' directory")
    
    if success_count == total_exports:
        print("✅ All exports successful!")
    else:
        print("⚠️  Some exports failed. Check the error messages above.")

if __name__ == "__main__":
    main() 