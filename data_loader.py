import pandas as pd
import requests
import logging
from sqlalchemy import create_engine, text
from tenacity import retry, stop_after_attempt, wait_fixed
from data_import import (
    create_holes_df,
    flatten_live_hole_winner_3way,
    flatten_live_hole_score,
    create_odds_df,
    merge_data,
    load_local_data,
    fetch_live_stats,
    load_local_stats_data
)
import config
import json
import psycopg2

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=config.DB_CONFIG['host'],
            port=config.DB_CONFIG['port'],
            dbname=config.DB_CONFIG['database'],
            user=config.DB_CONFIG['user'],
            password=config.DB_CONFIG['password']
        )
        logging.info("Database connection successful")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        return None

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_url(url, timeout=10):
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()

def fetch_and_store_live_hole_score_data(holes_url, odds_url):
    try:
        logging.info(f"Fetching live data from {holes_url}")
        holes_data = fetch_url(holes_url)
        logging.info(f"Fetching live data from {odds_url}")
        odds_data = fetch_url(odds_url)

        # Connect to the database
        conn = get_db_connection()
        if conn is None:
            return

        # Store data in the database
        engine = create_engine(f'postgresql://{config.DB_CONFIG["user"]}:{config.DB_CONFIG["password"]}@{config.DB_CONFIG["host"]}:{config.DB_CONFIG["port"]}/{config.DB_CONFIG["database"]}')
        holes_df = create_holes_df(holes_data)
        odds_df = flatten_live_hole_score(odds_data)

        logging.info(f"Holes DataFrame:\n{holes_df.head()}")
        logging.info(f"Odds DataFrame:\n{odds_df.head()}")

        store_holes_data(engine, holes_df)
        odds_df.to_sql('live_hole_score_odds_data', engine, if_exists='replace', index=False)

        logging.info("Data stored in the database successfully")
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching or storing data: {e}")

def fetch_and_store_live_hole_winner_3way_data(holes_url, odds_url):
    try:
        logging.info(f"Fetching live data from {holes_url}")
        holes_data = fetch_url(holes_url)
        logging.info(f"Fetching live data from {odds_url}")
        odds_data = fetch_url(odds_url)

        # Connect to the database
        conn = get_db_connection()
        if conn is None:
            return

        # Store data in the database
        engine = create_engine(f'postgresql://{config.DB_CONFIG["user"]}:{config.DB_CONFIG["password"]}@{config.DB_CONFIG["host"]}:{config.DB_CONFIG["port"]}/{config.DB_CONFIG["database"]}')
        holes_df = create_holes_df(holes_data)
        odds_df = flatten_live_hole_winner_3way(odds_data)

        logging.info(f"Holes DataFrame:\n{holes_df.head()}")
        logging.info(f"Odds DataFrame:\n{odds_df.head()}")

        store_holes_data(engine, holes_df)
        odds_df.to_sql('live_hole_winner_3way_odds_data', engine, if_exists='replace', index=False)

        logging.info("Data stored in the database successfully")
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching or storing data: {e}")

def load_local_data(holes_file='holes_data.json', odds_file='live_hole_score_odds_data.json'):
    try:
        with open(holes_file, 'r') as f:
            holes_data = json.load(f)
        logging.info("Local holes data loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading local holes data: {e}")
        holes_data = None

    try:
        with open(odds_file, 'r') as f:
            odds_data = json.load(f)
        logging.info("Local odds data loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading local odds data: {e}")
        odds_data = None
    
    return holes_data, odds_data

def fetch_live_stats(rounds_completed=config.ROUNDS_COMPLETED):
    logging.info("Fetching live stats...")
    rounds = [str(i) for i in range(1, rounds_completed + 1)] + ["event_avg"]

    live_stats = {}
    for round in rounds:
        url = config.LIVE_STATS_BASE_URL.format(round)
        logging.info(f"Fetching data for round: {round} from {url}")
        response = requests.get(url)
        try:
            response.raise_for_status()  # Check if the request was successful
            data = response.json()  # Parse the JSON response
            if data:  # Ensure data is not empty
                df = pd.json_normalize(data, record_path=['live_stats'])
                df = df.round(2)  # Round the numerical values to two decimal places
                live_stats[round] = df
            else:
                logging.warning(f"No data returned for round {round}")
                live_stats[round] = pd.DataFrame()  # Create an empty DataFrame for consistency
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for round {round}: {e}")
            live_stats[round] = pd.DataFrame()  # Create an empty DataFrame for consistency
        except ValueError as e:
            logging.error(f"Failed to decode JSON for round {round}: {e}")
            live_stats[round] = pd.DataFrame()  # Create an empty DataFrame for consistency

    logging.info("Live stats fetched successfully")
    return live_stats

def load_local_stats_data(rounds_completed=config.ROUNDS_COMPLETED):
    logging.info("Loading local stats data...")
    rounds = [str(i) for i in range(1, rounds_completed + 1)] + ["event_avg"]

    live_stats = {}
    for round in rounds:
        local_file = f'live_stats_data_round_{round}.json'
        try:
            with open(local_file, 'r') as f:
                round_data = json.load(f)
                # Flatten live_stats
                live_stats_df = pd.json_normalize(round_data, record_path=['live_stats'])
                live_stats[round] = live_stats_df
            logging.info(f"Local data for round {round} loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading local data for round {round}: {e}")
            live_stats[round] = pd.DataFrame()  # Create an empty DataFrame for consistency

    logging.info("Local live stats data loaded successfully.")
    return live_stats

def store_live_stats_data(engine, live_stats_data):
    try:
        for round, df in live_stats_data.items():
            table_name = f'live_stats_data_round_{round}'
            df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info("Live stats data stored in the database successfully")
    except Exception as e:
        logging.error(f"Error storing data in the database: {e}")

def store_holes_data(engine, holesdf):
    try:
        with engine.connect() as conn:
            conn.execute(text('DROP TABLE IF EXISTS holes_data CASCADE'))
        holesdf.to_sql('holes_data', engine, if_exists='replace', index=False)
        logging.info("Holes data stored in the database successfully")
    except Exception as e:
        logging.error(f"Error storing holes data in the database: {e}")

def fetch_data_from_db(table_name):
    try:
        engine = create_engine(f'postgresql://{config.DB_CONFIG["user"]}:{config.DB_CONFIG["password"]}@{config.DB_CONFIG["host"]}:{config.DB_CONFIG["port"]}/{config.DB_CONFIG["database"]}')
        df = pd.read_sql_table(table_name, engine)
        logging.info(f"Fetched data from {table_name} successfully")
        return df
    except Exception as e:
        logging.error(f"Error fetching data from {table_name}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame for consistency

def load_and_prepare_score_data(holes_data_file, odds_data_file, live=False):
    logging.info("Loading and preparing score data...")
    holes_data, score_data = load_local_data(holes_data_file, odds_data_file)
    
    # Check if the data is correctly structured here
    if holes_data is None or score_data is None:
        raise ValueError("Holes data or score data is None")
        
    holesdf = create_holes_df(holes_data)
    logging.info(f"holesdf: {holesdf.head()}")

    flattened_data_score = flatten_live_hole_score(score_data)
    logging.info(f"flattened_data_score: {flattened_data_score}")

    scoredf = create_odds_df(flattened_data_score)
    logging.info(f"scoredf: {scoredf.head()}")

    # Inspect unique values of round_num and hole
    logging.info(f"holesdf round_num unique values: {holesdf['round_num'].unique()}")
    logging.info(f"holesdf hole unique values: {holesdf['hole'].unique()}")
    logging.info(f"scoredf round_num unique values: {scoredf['round_num'].unique()}")
    logging.info(f"scoredf hole unique values: {scoredf['hole'].unique()}")

    merged_df = merge_data(holesdf, scoredf)

    if live:
        live_stats_data = fetch_live_stats()
    else:
        live_stats_data = load_local_stats_data()

    # Check for key columns here, This helps before dropna is called
    required_columns = ["hole", "participant", "outcome_label", "odds_decimal", "actual_implied_probability", "Implied_Probability_Delta"]
    for col in required_columns:
        if col not in merged_df.columns:
            raise ValueError(f"Required column {col} is missing in merged_df")

    filtered_merged_df = merged_df.dropna(subset=required_columns)

    return holesdf, filtered_merged_df, live_stats_data, scoredf

def load_and_prepare_winner_3way_data(holes_data_file, odds_data_file, live=False):
    logging.info("Loading and preparing winner 3-way data...")
    holes_data, odds_data = load_local_data(holes_data_file, odds_data_file)
    holesdf = create_holes_df(holes_data)
    logging.info(f"holesdf: {holesdf.head()}")
    
    flattened_data_odds = flatten_live_hole_winner_3way(odds_data)
    oddsdf = create_odds_df(flattened_data_odds)
    logging.info(f"oddsdf: {oddsdf.head()}")
    
    merged_df = merge_data(holesdf, oddsdf)
    logging.info(f"Merged DataFrame:\n{merged_df.head()}")
    
    if live:
        live_stats_data = fetch_live_stats()
    else:
        live_stats_data = load_local_stats_data()
        
    required_columns = ["hole", "participant", "outcome_label", "odds_decimal", "actual_implied_probability", "Implied_Probability_Delta"]
    for col in required_columns:
        if col not in merged_df.columns:
            raise ValueError(f"Required column {col} is missing in merged_df")

    filtered_merged_df = merged_df.dropna(subset=required_columns)
    
    logging.info("Winner 3-way data loaded and prepared successfully.")
    return holesdf, filtered_merged_df, live_stats_data, oddsdf
