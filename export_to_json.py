import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
from datetime import datetime
from decimal import Decimal

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

def export_teams():
    """Export teams data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT
                t.id,
                t.name,
                t.short_name,
                t.code,
                t.strength,
                0 as atk_h,
                0 as atk_a,
                0 as def_h,
                0 as def_a,
                COALESCE(home_stats.attack_rank, 10) as atk_h_rank,
                COALESCE(away_stats.attack_rank, 10) as atk_a_rank,
                COALESCE(home_stats.defense_rank, 10) as def_h_rank,
                COALESCE(away_stats.defense_rank, 10) as def_a_rank
            FROM teams_2025 t
            LEFT JOIN (
                SELECT 
                    team_id,
                    ROW_NUMBER() OVER (ORDER BY (goals_scored * 0.7 + expected_goals * 0.3) / NULLIF(games_played, 0) DESC) as attack_rank,
                    ROW_NUMBER() OVER (ORDER BY (goals_conceded * 0.6 + expected_goals_conceded * 0.2) / NULLIF(games_played, 0) - (clean_sheets * 0.2) ASC) as defense_rank
                FROM team_stats_home
                WHERE games_played > 0
            ) home_stats ON t.id = home_stats.team_id
            LEFT JOIN (
                SELECT 
                    team_id,
                    ROW_NUMBER() OVER (ORDER BY (goals_scored * 0.7 + expected_goals * 0.3) / NULLIF(games_played, 0) DESC) as attack_rank,
                    ROW_NUMBER() OVER (ORDER BY (goals_conceded * 0.6 + expected_goals_conceded * 0.2) / NULLIF(games_played, 0) - (clean_sheets * 0.2) ASC) as defense_rank
                FROM team_stats_away
                WHERE games_played > 0
            ) away_stats ON t.id = away_stats.team_id
            ORDER BY t.short_name
        """)
        
        teams = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert to list of dictionaries and handle Decimal types
        teams_data = []
        for team in teams:
            team_dict = dict(team)
            # Convert Decimal to float
            for key, value in team_dict.items():
                if isinstance(value, Decimal):
                    team_dict[key] = float(value)
            teams_data.append(team_dict)
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Save to JSON file
        with open('data/teams.json', 'w') as f:
            json.dump({
                'last_updated': datetime.now().isoformat(),
                'data': teams_data
            }, f, indent=2)
        
        print(f"✅ Exported {len(teams_data)} teams to data/teams.json")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting teams: {e}")
        return False

def export_players():
    """Export players data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT p.id, p.web_name, p.element_type, p.now_cost, p.team_id, 
                   t.short_name as team_name, p.total_points,
                   p.goals_scored, p.assists, p.expected_goals, p.expected_assists,
                   p.clean_sheets, p.goals_conceded, p.bonus, p.saves, p.minutes,
                   CASE 
                       WHEN p_old.now_cost > 0 AND p_old.now_cost < 20 THEN p_old.now_cost 
                       ELSE 0 
                   END as last_cost,
                   t.strength as team_rank
            FROM players_2025 p
            JOIN teams_2025 t ON p.team_id = t.id
            LEFT JOIN players p_old ON p.id = p_old.id
            WHERE p.element_type != 5
            ORDER BY t.name, p.web_name
        """)
        
        players = cursor.fetchall()
        cursor.close()
        conn.close()
        
        players_data = []
        for player in players:
            player_dict = dict(player)
            # Convert Decimal to float
            for key, value in player_dict.items():
                if isinstance(value, Decimal):
                    player_dict[key] = float(value)
            players_data.append(player_dict)
        
        with open('data/players.json', 'w') as f:
            json.dump({
                'last_updated': datetime.now().isoformat(),
                'data': players_data
            }, f, indent=2)
        
        print(f"✅ Exported {len(players_data)} players to data/players.json")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting players: {e}")
        return False

def export_fixtures():
    """Export fixtures data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, event, team_h, team_a, team_h_difficulty, team_a_difficulty, kickoff_time
            FROM fixtures_2025 
            ORDER BY event, kickoff_time
        """)
        
        fixtures = cursor.fetchall()
        cursor.close()
        conn.close()
        
        fixtures_data = []
        for fixture in fixtures:
            fixture_dict = dict(fixture)
            # Convert datetime to string
            for key, value in fixture_dict.items():
                if isinstance(value, datetime):
                    fixture_dict[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    fixture_dict[key] = float(value)
            fixtures_data.append(fixture_dict)
        
        with open('data/fixtures.json', 'w') as f:
            json.dump({
                'last_updated': datetime.now().isoformat(),
                'data': fixtures_data
            }, f, indent=2)
        
        print(f"✅ Exported {len(fixtures_data)} fixtures to data/fixtures.json")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting fixtures: {e}")
        return False

def export_team_stats():
    """Export team stats for all locations"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Export home stats
        cursor.execute("""
            SELECT 
                ts.team_id,
                ts.team_name,
                ts.games_played,
                ts.goals_scored,
                ts.goals_conceded,
                ts.clean_sheets,
                ts.expected_goals,
                ts.expected_goals_conceded,
                ts.wins,
                ts.draws,
                ts.losses,
                ts.points,
                ROW_NUMBER() OVER (ORDER BY (ts.goals_scored * 0.7 + ts.expected_goals * 0.3) / NULLIF(ts.games_played, 0) DESC) as attack_rank,
                ROW_NUMBER() OVER (ORDER BY (ts.goals_conceded * 0.6 + ts.expected_goals_conceded * 0.2) / NULLIF(ts.games_played, 0) - (ts.clean_sheets * 0.2) ASC) as defense_rank,
                COALESCE(team_saves.total_saves, 0) as saves
            FROM team_stats_home ts
            JOIN teams_2025 t ON ts.team_id = t.id
            LEFT JOIN (
                SELECT 
                    p.team_id,
                    SUM(p.saves) as total_saves
                FROM players_2025 p
                WHERE p.element_type = 1
                GROUP BY p.team_id
            ) team_saves ON ts.team_id = team_saves.team_id
            ORDER BY ts.team_name
        """)
        
        home_stats = []
        for stat in cursor.fetchall():
            stat_dict = dict(stat)
            # Convert Decimal to float
            for key, value in stat_dict.items():
                if isinstance(value, Decimal):
                    stat_dict[key] = float(value)
            home_stats.append(stat_dict)
        
        # Export away stats
        cursor.execute("""
            SELECT 
                ts.team_id,
                ts.team_name,
                ts.games_played,
                ts.goals_scored,
                ts.goals_conceded,
                ts.clean_sheets,
                ts.expected_goals,
                ts.expected_goals_conceded,
                ts.wins,
                ts.draws,
                ts.losses,
                ts.points,
                ROW_NUMBER() OVER (ORDER BY (ts.goals_scored * 0.7 + ts.expected_goals * 0.3) / NULLIF(ts.games_played, 0) DESC) as attack_rank,
                ROW_NUMBER() OVER (ORDER BY (ts.goals_conceded * 0.6 + ts.expected_goals_conceded * 0.2) / NULLIF(ts.games_played, 0) - (ts.clean_sheets * 0.2) ASC) as defense_rank,
                COALESCE(team_saves.total_saves, 0) as saves
            FROM team_stats_away ts
            JOIN teams_2025 t ON ts.team_id = t.id
            LEFT JOIN (
                SELECT 
                    p.team_id,
                    SUM(p.saves) as total_saves
                FROM players_2025 p
                WHERE p.element_type = 1
                GROUP BY p.team_id
            ) team_saves ON ts.team_id = team_saves.team_id
            ORDER BY ts.team_name
        """)
        
        away_stats = []
        for stat in cursor.fetchall():
            stat_dict = dict(stat)
            # Convert Decimal to float
            for key, value in stat_dict.items():
                if isinstance(value, Decimal):
                    stat_dict[key] = float(value)
            away_stats.append(stat_dict)
        
        # Export overall stats
        cursor.execute("""
            SELECT 
                ts.team_id,
                ts.team_name,
                ts.games_played,
                ts.goals_scored,
                ts.goals_conceded,
                ts.clean_sheets,
                ts.expected_goals,
                ts.expected_goals_conceded,
                ts.wins,
                ts.draws,
                ts.losses,
                ts.points,
                ROW_NUMBER() OVER (ORDER BY (ts.goals_scored * 0.7 + ts.expected_goals * 0.3) / NULLIF(ts.games_played, 0) DESC) as attack_rank,
                ROW_NUMBER() OVER (ORDER BY (ts.goals_conceded * 0.6 + ts.expected_goals_conceded * 0.2) / NULLIF(ts.games_played, 0) - (ts.clean_sheets * 0.2) ASC) as defense_rank,
                COALESCE(team_saves.total_saves, 0) as saves
            FROM team_stats_overall ts
            JOIN teams_2025 t ON ts.team_id = t.id
            LEFT JOIN (
                SELECT 
                    p.team_id,
                    SUM(p.saves) as total_saves
                FROM players_2025 p
                WHERE p.element_type = 1
                GROUP BY p.team_id
            ) team_saves ON ts.team_id = team_saves.team_id
            ORDER BY ts.team_name
        """)
        
        overall_stats = []
        for stat in cursor.fetchall():
            stat_dict = dict(stat)
            # Convert Decimal to float
            for key, value in stat_dict.items():
                if isinstance(value, Decimal):
                    stat_dict[key] = float(value)
            overall_stats.append(stat_dict)
        
        cursor.close()
        conn.close()
        
        # Save all stats
        team_stats = {
            'last_updated': datetime.now().isoformat(),
            'home': home_stats,
            'away': away_stats,
            'overall': overall_stats
        }
        
        with open('data/team-stats.json', 'w') as f:
            json.dump(team_stats, f, indent=2)
        
        print(f"✅ Exported team stats to data/team-stats.json")
        print(f"   - Home: {len(home_stats)} teams")
        print(f"   - Away: {len(away_stats)} teams")
        print(f"   - Overall: {len(overall_stats)} teams")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting team stats: {e}")
        return False

def export_team_rankings():
    """Export team rankings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Calculate attack rankings
        cursor.execute("""
            SELECT 
                ts.team_id,
                ts.team_name,
                (0.7 * ts.goals_scored + 0.3 * ts.expected_goals) / NULLIF(ts.games_played, 0) as weighted_score
            FROM team_stats_overall ts
            WHERE ts.games_played > 0
            ORDER BY (0.7 * ts.goals_scored + 0.3 * ts.expected_goals) / NULLIF(ts.games_played, 0) DESC
        """)
        
        attack_rankings = []
        for i, stat in enumerate(cursor.fetchall()):
            attack_rankings.append({
                'team_id': stat['team_id'],
                'team_name': stat['team_name'],
                'rank': i + 1,
                'weighted_score': float(stat['weighted_score']) if stat['weighted_score'] else 0
            })
        
        # Calculate defense rankings
        cursor.execute("""
            SELECT 
                ts.team_id,
                ts.team_name,
                (0.6 * ts.goals_conceded + 0.2 * ts.expected_goals_conceded) / NULLIF(ts.games_played, 0) - (0.2 * ts.clean_sheets) as weighted_score
            FROM team_stats_overall ts
            WHERE ts.games_played > 0
            ORDER BY (0.6 * ts.goals_conceded + 0.2 * ts.expected_goals_conceded) / NULLIF(ts.games_played, 0) - (0.2 * ts.clean_sheets) ASC
        """)
        
        defense_rankings = []
        for i, stat in enumerate(cursor.fetchall()):
            defense_rankings.append({
                'team_id': stat['team_id'],
                'team_name': stat['team_name'],
                'rank': i + 1,
                'weighted_score': float(stat['weighted_score']) if stat['weighted_score'] else 0
            })
        
        cursor.close()
        conn.close()
        
        rankings = {
            'last_updated': datetime.now().isoformat(),
            'attack': attack_rankings,
            'defense': defense_rankings
        }
        
        with open('data/team-rankings.json', 'w') as f:
            json.dump(rankings, f, indent=2)
        
        print(f"✅ Exported team rankings to data/team-rankings.json")
        print(f"   - Attack rankings: {len(attack_rankings)} teams")
        print(f"   - Defense rankings: {len(defense_rankings)} teams")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting team rankings: {e}")
        return False

def main():
    """Main export function"""
    print("📊 Exporting FPL data to JSON files...")
    print("=" * 50)
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Export all data
    success_count = 0
    total_exports = 5
    
    if export_teams():
        success_count += 1
    
    if export_players():
        success_count += 1
    
    if export_fixtures():
        success_count += 1
    
    if export_team_stats():
        success_count += 1
    
    if export_team_rankings():
        success_count += 1
    
    print("=" * 50)
    print(f"✅ Export complete: {success_count}/{total_exports} successful")
    
    if success_count == total_exports:
        print("🎉 All data exported successfully!")
        print("📁 Check the 'data/' directory for JSON files")
    else:
        print("⚠️  Some exports failed. Check the errors above.")

if __name__ == "__main__":
    main() 