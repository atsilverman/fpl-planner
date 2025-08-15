import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import json
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

def fetch_fpl_api_data():
    """Fetch current FPL data from official API"""
    try:
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching FPL API data: {e}")
        return None

def create_players_2025_table():
    """Create the new players_2025 table with essential fields"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Drop table if it exists
        cursor.execute("DROP TABLE IF EXISTS players_2025")
        
        # Create new table with essential fields for draft planning
        cursor.execute("""
            CREATE TABLE players_2025 (
                id INTEGER PRIMARY KEY,
                web_name VARCHAR(100) NOT NULL,
                first_name VARCHAR(100),
                second_name VARCHAR(100),
                element_type INTEGER NOT NULL,
                now_cost INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                status VARCHAR(50),
                selected_by_percent DECIMAL(5,2),
                form DECIMAL(5,2),
                total_points INTEGER,
                points_per_game DECIMAL(5,2),
                minutes INTEGER,
                goals_scored INTEGER,
                assists INTEGER,
                clean_sheets INTEGER,
                goals_conceded INTEGER,
                yellow_cards INTEGER,
                red_cards INTEGER,
                saves INTEGER,
                bonus INTEGER,
                influence DECIMAL(8,2),
                creativity DECIMAL(8,2),
                threat DECIMAL(8,2),
                ict_index DECIMAL(8,2),
                starts INTEGER,
                expected_goals DECIMAL(5,2),
                expected_assists DECIMAL(5,2),
                expected_goal_involvements DECIMAL(5,2),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Created players_2025 table with essential fields")
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")

def sync_teams_2025():
    """Sync teams data to teams_2025 table"""
    try:
        fpl_data = fetch_fpl_api_data()
        if not fpl_data:
            return False
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Drop and recreate teams_2025 table
        cursor.execute("DROP TABLE IF EXISTS teams_2025")
        cursor.execute("""
            CREATE TABLE teams_2025 (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                short_name VARCHAR(50),
                code VARCHAR(10),
                strength INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert team data
        teams = fpl_data.get('teams', [])
        for team in teams:
            cursor.execute("""
                INSERT INTO teams_2025 (id, name, short_name, code, strength)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                team['id'], team['name'], team['short_name'], team['code'],
                team.get('strength')
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Synced {len(teams)} teams to teams_2025 table")
        return True
        
    except Exception as e:
        print(f"❌ Error syncing teams: {e}")
        return False

def sync_players_2025():
    """Sync players data to players_2025 table"""
    try:
        fpl_data = fetch_fpl_api_data()
        if not fpl_data:
            return False
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get players (exclude managers - element_type 5)
        players = [p for p in fpl_data.get('elements', []) if p['element_type'] != 5]
        
        # Insert player data with essential fields
        for player in players:
            cursor.execute("""
                INSERT INTO players_2025 (
                    id, web_name, first_name, second_name, element_type, now_cost,
                    team_id, status, selected_by_percent, form, total_points, points_per_game,
                    minutes, goals_scored, assists, clean_sheets, goals_conceded,
                    yellow_cards, red_cards, saves, bonus, influence, creativity,
                    threat, ict_index, starts, expected_goals, expected_assists,
                    expected_goal_involvements
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                player['id'], player['web_name'], player.get('first_name'), player.get('second_name'),
                player['element_type'], player['now_cost'], player['team'], player.get('status'),
                player.get('selected_by_percent'), player.get('form'), player.get('total_points'),
                player.get('points_per_game'), player.get('minutes'), player.get('goals_scored'),
                player.get('assists'), player.get('clean_sheets'), player.get('goals_conceded'),
                player.get('yellow_cards'), player.get('red_cards'), player.get('saves'),
                player.get('bonus'), player.get('influence'), player.get('creativity'),
                player.get('threat'), player.get('ict_index'), player.get('starts'),
                player.get('expected_goals'), player.get('expected_assists'),
                player.get('expected_goal_involvements')
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Synced {len(players)} players to players_2025 table")
        return True
        
    except Exception as e:
        print(f"❌ Error syncing players: {e}")
        return False

def sync_fixtures_2025():
    """Sync fixtures data to fixtures_2025 table"""
    try:
        fpl_data = fetch_fpl_api_data()
        if not fpl_data:
            return False
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get fixtures
        fixtures = fpl_data.get('events', [])
        
        # Insert fixture data
        for fixture in fixtures:
            cursor.execute("""
                INSERT INTO fixtures_2025 (
                    id, event, team_h, team_a, team_h_difficulty, team_a_difficulty, kickoff_time
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (id) DO UPDATE SET
                    event = EXCLUDED.event,
                    team_h = EXCLUDED.team_h,
                    team_a = EXCLUDED.team_a,
                    team_h_difficulty = EXCLUDED.team_h_difficulty,
                    team_a_difficulty = EXCLUDED.team_a_difficulty,
                    kickoff_time = EXCLUDED.kickoff_time,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                fixture['id'], fixture['id'], 
                fixture.get('team_h'), fixture.get('team_a'),
                fixture.get('team_h_difficulty', 3), fixture.get('team_a_difficulty', 3),
                fixture.get('deadline_time')
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Synced {len(fixtures)} fixtures to fixtures_2025 table")
        return True
        
    except Exception as e:
        print(f"❌ Error syncing fixtures: {e}")
        return False

def update_server_to_use_2025_tables():
    """Update the server.py to use the new 2025 tables"""
    try:
        with open('server.py', 'r') as f:
            content = f.read()
        
        # Replace old table references with new ones
        content = content.replace('FROM players p', 'FROM players_2025 p')
        content = content.replace('JOIN teams_2025 t ON p.team_id = t.id', 'JOIN teams_2025 t ON p.team_id = t.id')
        
        with open('server.py', 'w') as f:
            f.write(content)
            
        print("✅ Updated server.py to use players_2025 table")
        
    except Exception as e:
        print(f"❌ Error updating server.py: {e}")

def main():
    """Main sync function"""
    print("🔄 Starting FPL Data Sync (Simplified)...")
    print("=" * 50)
    
    # Step 1: Create new tables
    print("\n📋 Step 1: Creating new tables...")
    create_players_2025_table()
    
    # Step 2: Sync teams
    print("\n🏟️ Step 2: Syncing teams...")
    if not sync_teams_2025():
        print("❌ Failed to sync teams. Aborting.")
        return
    
    # Step 3: Sync players
    print("\n👥 Step 3: Syncing players...")
    if not sync_players_2025():
        print("❌ Failed to sync players. Aborting.")
        return
    
    # Step 4: Sync fixtures
    print("\n📅 Step 4: Syncing fixtures...")
    if not sync_fixtures_2025():
        print("❌ Failed to sync fixtures. Aborting.")
        return
    
    # Step 5: Update server
    print("\n🔧 Step 5: Updating server configuration...")
    update_server_to_use_2025_tables()
    
    print("\n✅ FPL Data Sync Complete!")
    print("=" * 50)
    print("📊 Summary:")
    print("• Created players_2025 table with current FPL data")
    print("• Updated teams_2025 table with current team data")
    print("• Updated fixtures_2025 table with current fixture data")
    print("• Updated server.py to use new tables")
    print("\n🚀 Your draft planner will now use the latest FPL data!")
    print("\n💡 Next steps:")
    print("• Restart your Flask server")
    print("• Test the draft planner with updated data")

if __name__ == "__main__":
    main() 