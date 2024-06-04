import json
import pandas as pd
import logging
from sqlalchemy import create_engine
from data_import import flatten_live_hole_winner_3way
import config

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_db_connection():
    try:
        engine = create_engine(f'postgresql://{config.DB_CONFIG["user"]}:{config.DB_CONFIG["password"]}@{config.DB_CONFIG["host"]}:{config.DB_CONFIG["port"]}/{config.DB_CONFIG["database"]}')
        logging.info("Database connection successful")
        return engine
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        return None

def fetch_and_store_live_hole_winner_3way_data(local_file):
    try:
        # Load local JSON file
        logging.info(f"Loading data from local file: {local_file}")
        with open(local_file, 'r') as file:
            data = json.load(file)

        # Flatten the JSON data
        logging.info("Flattening live hole winner 3-way data...")
        df = flatten_live_hole_winner_3way(data)
        logging.info(f"Flattened DataFrame:\n{df.head()}")

        # Store data in the database
        engine = get_db_connection()
        if engine is None:
            return

        df.to_sql('live_hole_winner_3way_odds_data', engine, if_exists='replace', index=False)
        logging.info("Data stored in the database successfully")
    except Exception as e:
        logging.error(f"Error fetching or saving live hole winner 3-way odds data: {e}")

# Update config to use local file
config.LIVE_HOLE_WINNER_3WAY_ODDS_DATA_SOURCE = 'local'
config.LOCAL_LIVE_HOLE_WINNER_3WAY_ODDS_DATA_FILE = 'live_hole_winner_3way_odds_data.json'

# Run the function
fetch_and_store_live_hole_winner_3way_data(config.LOCAL_LIVE_HOLE_WINNER_3WAY_ODDS_DATA_FILE)
