import psycopg2
import csv
import os
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'silverman',
    'password': 'password'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def import_team_stats_from_csv():
    """Import team stats from CSV files if they exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if CSV files exist
        csv_files = {
            'team_stats_home.csv': 'team_stats_home',
            'team_stats_away.csv': 'team_stats_away', 
            'team_stats_overall.csv': 'team_stats_overall'
        }
        
        imported_count = 0
        
        for csv_file, table_name in csv_files.items():
            if os.path.exists(csv_file):
                print(f"📊 Importing {csv_file} to {table_name}...")
                
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        cursor.execute(f"""
                            INSERT INTO {table_name} (
                                team_id, team_name, games_played, goals_scored, goals_conceded,
                                clean_sheets, expected_goals, expected_goals_conceded,
                                wins, draws, losses, points
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            ) ON CONFLICT (team_id) DO UPDATE SET
                                games_played = EXCLUDED.games_played,
                                goals_scored = EXCLUDED.goals_scored,
                                goals_conceded = EXCLUDED.goals_conceded,
                                clean_sheets = EXCLUDED.clean_sheets,
                                expected_goals = EXCLUDED.expected_goals,
                                expected_goals_conceded = EXCLUDED.expected_goals_conceded,
                                wins = EXCLUDED.wins,
                                draws = EXCLUDED.draws,
                                losses = EXCLUDED.losses,
                                points = EXCLUDED.points,
                                updated_at = CURRENT_TIMESTAMP
                        """, (
                            int(row.get('team_id', 0)),
                            row.get('team_name', ''),
                            int(row.get('games_played', 0)),
                            int(row.get('goals_scored', 0)),
                            int(row.get('goals_conceded', 0)),
                            int(row.get('clean_sheets', 0)),
                            float(row.get('expected_goals', 0)),
                            float(row.get('expected_goals_conceded', 0)),
                            int(row.get('wins', 0)),
                            int(row.get('draws', 0)),
                            int(row.get('losses', 0)),
                            int(row.get('points', 0))
                        ))
                
                imported_count += 1
                print(f"✅ Imported {csv_file}")
            else:
                print(f"⚠️  {csv_file} not found, skipping...")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        if imported_count > 0:
            print(f"✅ Successfully imported {imported_count} CSV files")
        else:
            print("ℹ️  No CSV files found to import")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing CSV data: {e}")
        return False

def create_sample_csv_data():
    """Create sample CSV data for testing if no CSV files exist"""
    try:
        # Sample team stats data
        sample_data = {
            'team_stats_home.csv': [
                ['team_id', 'team_name', 'games_played', 'goals_scored', 'goals_conceded', 'clean_sheets', 'expected_goals', 'expected_goals_conceded', 'wins', 'draws', 'losses', 'points'],
                ['1', 'Arsenal', '5', '12', '4', '3', '11.5', '4.2', '4', '1', '0', '13'],
                ['2', 'Aston Villa', '5', '10', '6', '2', '9.8', '5.1', '3', '1', '1', '10'],
                ['3', 'Burnley', '5', '3', '12', '0', '4.2', '11.8', '0', '1', '4', '1']
            ],
            'team_stats_away.csv': [
                ['team_id', 'team_name', 'games_played', 'goals_scored', 'goals_conceded', 'clean_sheets', 'expected_goals', 'expected_goals_conceded', 'wins', 'draws', 'losses', 'points'],
                ['1', 'Arsenal', '5', '8', '5', '2', '7.8', '5.3', '2', '2', '1', '8'],
                ['2', 'Aston Villa', '5', '7', '8', '1', '6.9', '7.2', '2', '1', '2', '7'],
                ['3', 'Burnley', '5', '2', '15', '0', '3.1', '13.5', '0', '0', '5', '0']
            ],
            'team_stats_overall.csv': [
                ['team_id', 'team_name', 'games_played', 'goals_scored', 'goals_conceded', 'clean_sheets', 'expected_goals', 'expected_goals_conceded', 'wins', 'draws', 'losses', 'points'],
                ['1', 'Arsenal', '10', '20', '9', '5', '19.3', '9.5', '6', '3', '1', '21'],
                ['2', 'Aston Villa', '10', '17', '14', '3', '16.7', '12.3', '5', '2', '3', '17'],
                ['3', 'Burnley', '10', '5', '27', '0', '7.3', '25.3', '0', '1', '9', '1']
            ]
        }
        
        for filename, data in sample_data.items():
            if not os.path.exists(filename):
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(data)
                print(f"📝 Created sample {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample CSV data: {e}")
        return False

def main():
    """Main function"""
    print("📥 Importing custom CSV data...")
    print("=" * 50)
    
    # Create sample data if no CSV files exist
    if not any(os.path.exists(f) for f in ['team_stats_home.csv', 'team_stats_away.csv', 'team_stats_overall.csv']):
        print("📝 No CSV files found, creating sample data...")
        create_sample_csv_data()
    
    # Import CSV data
    if import_team_stats_from_csv():
        print("\n✅ CSV import complete!")
    else:
        print("\n❌ CSV import failed!")

if __name__ == "__main__":
    main()
