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

def create_team_stats_tables():
    """Create team stats tables for home, away, and overall stats"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create team_stats_home table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_stats_home (
                id SERIAL PRIMARY KEY,
                team_id INTEGER NOT NULL UNIQUE,
                team_name VARCHAR(100) NOT NULL,
                games_played INTEGER DEFAULT 0,
                goals_scored INTEGER DEFAULT 0,
                goals_conceded INTEGER DEFAULT 0,
                clean_sheets INTEGER DEFAULT 0,
                expected_goals DECIMAL(5,2) DEFAULT 0,
                expected_goals_conceded DECIMAL(5,2) DEFAULT 0,
                wins INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create team_stats_away table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_stats_away (
                id SERIAL PRIMARY KEY,
                team_id INTEGER NOT NULL UNIQUE,
                team_name VARCHAR(100) NOT NULL,
                games_played INTEGER DEFAULT 0,
                goals_scored INTEGER DEFAULT 0,
                goals_conceded INTEGER DEFAULT 0,
                clean_sheets INTEGER DEFAULT 0,
                expected_goals DECIMAL(5,2) DEFAULT 0,
                expected_goals_conceded DECIMAL(5,2) DEFAULT 0,
                wins INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create team_stats_overall table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_stats_overall (
                id SERIAL PRIMARY KEY,
                team_id INTEGER NOT NULL UNIQUE,
                team_name VARCHAR(100) NOT NULL,
                games_played INTEGER DEFAULT 0,
                goals_scored INTEGER DEFAULT 0,
                goals_conceded INTEGER DEFAULT 0,
                clean_sheets INTEGER DEFAULT 0,
                expected_goals DECIMAL(5,2) DEFAULT 0,
                expected_goals_conceded DECIMAL(5,2) DEFAULT 0,
                wins INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create fixtures_2025 table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fixtures_2025 (
                id INTEGER PRIMARY KEY,
                event INTEGER,
                team_h INTEGER,
                team_a INTEGER,
                team_h_difficulty INTEGER,
                team_a_difficulty INTEGER,
                kickoff_time TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Drop and recreate fixtures_2025 table to ensure it has all columns
        cursor.execute("DROP TABLE IF EXISTS fixtures_2025")
        cursor.execute("""
            CREATE TABLE fixtures_2025 (
                id INTEGER PRIMARY KEY,
                event INTEGER,
                team_h INTEGER,
                team_a INTEGER,
                team_h_difficulty INTEGER,
                team_a_difficulty INTEGER,
                kickoff_time TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create players table (for historical cost data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                now_cost INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Created all required database tables:")
        print("   - team_stats_home")
        print("   - team_stats_away") 
        print("   - team_stats_overall")
        print("   - fixtures_2025")
        print("   - players")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def populate_initial_data():
    """Populate tables with initial data from FPL API"""
    try:
        import requests
        
        # Fetch FPL data
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        response = requests.get(url)
        response.raise_for_status()
        fpl_data = response.json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Populate fixtures
        fixtures = fpl_data.get('events', [])
        for fixture in fixtures:
            cursor.execute("""
                INSERT INTO fixtures_2025 (id, event, team_h, team_a, team_h_difficulty, team_a_difficulty, kickoff_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                fixture['id'], fixture['id'], 
                fixture.get('team_h'), fixture.get('team_a'),
                fixture.get('team_h_difficulty', 3), fixture.get('team_a_difficulty', 3),
                fixture.get('deadline_time')
            ))
        
        # Populate initial team stats with zeros
        teams = fpl_data.get('teams', [])
        for team in teams:
            # Home stats
            cursor.execute("""
                INSERT INTO team_stats_home (team_id, team_name)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (team['id'], team['name']))
            
            # Away stats
            cursor.execute("""
                INSERT INTO team_stats_away (team_id, team_name)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (team['id'], team['name']))
            
            # Overall stats
            cursor.execute("""
                INSERT INTO team_stats_overall (team_id, team_name)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (team['id'], team['name']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Populated initial data:")
        print(f"   - {len(fixtures)} fixtures")
        print(f"   - {len(teams)} teams with initial stats")
        
        return True
        
    except Exception as e:
        print(f"❌ Error populating initial data: {e}")
        return False

def main():
    """Main function"""
    print("🏗️ Creating team stats database tables...")
    print("=" * 50)
    
    if create_team_stats_tables():
        print("\n📊 Populating with initial data...")
        populate_initial_data()
        print("\n✅ Database setup complete!")
    else:
        print("\n❌ Failed to create tables")

if __name__ == "__main__":
    main()
