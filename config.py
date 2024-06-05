# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'livegolfbetting',
    'user': 'root',
    'password': 'Password123'
}

# Data sources configuration
HOLES_DATA_SOURCE = 'local'  # Can be 'local' or 'live'
LIVE_HOLE_SCORE_ODDS_DATA_SOURCE = 'local'  # Can be 'local' or 'live'
LIVE_HOLE_WINNER_2WAY_ODDS_DATA_SOURCE = 'local'  # Can be 'local' or 'live'
LIVE_HOLE_WINNER_3WAY_ODDS_DATA_SOURCE = 'local'  # Can be 'local' or 'live'
LIVE_FINISHING_POSITION_ODDS_DATA_SOURCE = 'local'  # Can be 'local' or 'live'
LIVE_MATCHUPS_ODDS_DATA_SOURCE = 'local'  # Can be 'local' or 'live'
LIVE_STATS_DATA_SOURCE = 'local'  # Can be 'local' or 'live'

# URLs for live data
HOLES_DATA_URL = 'https://api.example.com/holes'
LIVE_HOLE_SCORE_ODDS_DATA_URL_TEMPLATE = 'https://api.example.com/live_hole_score_odds/{eventgroup}'
LIVE_HOLE_WINNER_2WAY_ODDS_DATA_URL_TEMPLATE = 'https://api.example.com/live_hole_winner_2way_odds/{eventgroup}'
LIVE_HOLE_WINNER_3WAY_ODDS_DATA_URL_TEMPLATE = 'https://api.example.com/live_hole_winner_3way_odds/{eventgroup}'
LIVE_FINISHING_POSITION_ODDS_DATA_URL_TEMPLATE = 'https://api.example.com/live_finishing_position_odds/{eventgroup}'
LIVE_MATCHUPS_ODDS_DATA_URL_TEMPLATE = 'https://api.example.com/live_matchups_odds/{eventgroup}'
LIVE_STATS_BASE_URL = 'https://api.example.com/live_stats_round_{round}'

# Paths for local data
LOCAL_HOLES_DATA_FILE = 'holes_data.json'
LOCAL_LIVE_HOLE_SCORE_ODDS_DATA_FILE = 'live_hole_score_odds_data.json'
LOCAL_LIVE_HOLE_WINNER_2WAY_ODDS_DATA_FILE = 'live_hole_winner_2way_odds_data.json'
LOCAL_LIVE_HOLE_WINNER_3WAY_ODDS_DATA_FILE = 'live_hole_winner_3way_odds_data.json'
LOCAL_LIVE_FINISHING_POSITION_ODDS_DATA_FILE = 'live_finishing_position_odds_data.json'
LOCAL_LIVE_MATCHUPS_ODDS_DATA_FILE = 'live_matchups_odds_data.json'
LOCAL_LIVE_STATS_DATA_FILES_TEMPLATE = 'live_stats_data_round_{round}.json'

# Other configurations
EVENTGROUP = '44878'
ROUNDS_COMPLETED = 4  # Number of completed rounds, adjust as needed

# Colors
COLORS = {
    "primary": "#374785",
    "secondary": "#F76C6C",
    "tertiary": "#F8E9A1",
    "quaternary": "#A8D0E6",
    "background": "#f4f5f7",
    "header_background": "#24305E",
    "text": "#ffffff",
    "border": "#ddd",
    "box_shadow": "rgba(0, 0, 0, 0.1)"
}
