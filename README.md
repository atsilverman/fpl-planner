# FPL Draft Planner 2025/26

A lightweight web application to help plan your Fantasy Premier League draft by showing players and their upcoming fixtures.

## Features

- **Player Table**: View all FPL players with their position, team, and current price
- **Fixture Analysis**: See upcoming fixtures for each player with difficulty ratings
- **Filtering**: Filter by position (Goalkeeper, Defender, Midfielder, Forward) and team
- **Customizable View**: Choose how many gameweeks ahead to display (1-10)
- **Modern UI**: Clean, responsive design with light color theme
- **Real-time Stats**: Summary statistics for the filtered players

## Setup

### Prerequisites

- Python 3.7+
- PostgreSQL database with FPL data
- Required Python packages (see requirements.txt)

### Installation

1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure your PostgreSQL database is running with the FPL data tables:
   - `players` - Player information
   - `teams_2025` - Team information for 2025/26 season
   - `fixtures_2025` - Fixture information for 2025/26 season
   - `player_gameweek_stats` - Historical player performance data

4. Update the database configuration in `server.py` if needed:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'port': 5432,
       'database': 'postgres',
       'user': 'silverman',
       'password': 'password'
   }
   ```

### Running the Application

1. Start the Flask server:
   ```bash
   python3 server.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5001
   ```

## Usage

1. **Select Gameweeks**: Choose how many upcoming gameweeks to display (default: 5)
2. **Filter Players**: Use the position and team dropdowns to filter the player list
3. **View Fixtures**: Each player row shows their upcoming fixtures with:
   - Home (H) or Away (A) indicator
   - Opponent team abbreviation
   - Fixture difficulty rating (1-5, where 1 is easiest)
4. **Update View**: Click "Update View" to apply filters and refresh the data

## Fixture Difficulty Colors

- **Green (1-2)**: Easy fixtures
- **Yellow (3)**: Medium difficulty
- **Orange (4)**: Hard fixtures
- **Red (5)**: Very difficult fixtures

## Data Sources

The application uses your local PostgreSQL database containing:
- Current FPL player data
- 2025/26 season fixture information
- Historical player performance data (for future enhancements)

## Future Enhancements

- Player performance history vs specific opponents
- Form analysis and trends
- Draft strategy recommendations
- Export functionality
- Player comparison tools

## Technical Details

- **Frontend**: Pure HTML/CSS/JavaScript (no frameworks)
- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Port**: 5001 (configurable in server.py)

## Troubleshooting

- If port 5000 is in use (common on macOS due to AirPlay), the server will use port 5001
- Ensure your PostgreSQL server is running and accessible
- Check that all required database tables exist and contain data
- Verify database connection credentials in server.py # Test auto-deploy
