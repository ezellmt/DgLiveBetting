import json
import pandas as pd
import requests
import logging
import config
from tenacity import retry, stop_after_attempt, wait_fixed
from sqlalchemy import create_engine
import re

logging.basicConfig(level=logging.INFO)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_data(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

def load_local_data(holes_data_file, odds_data_file):
    holes_data, odds_data = None, None

    try:
        holes_data = fetch_data(holes_data_file) if holes_data_file.startswith('http') else json.load(open(holes_data_file))
        logging.info("Holes data loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading holes data: {e}")

    try:
        odds_data = fetch_data(odds_data_file) if odds_data_file.startswith('http') else json.load(open(odds_data_file))
        logging.info("Odds data loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading odds data: {e}")

    return holes_data, odds_data

def flatten_data(holes_data):
    flattened_data = []
    for course in holes_data['courses']:
        for round in course['rounds']:
            for hole in round['holes']:
                hole_flat = {**hole, 'course_code': course.get('course_code'), 'course_key': course.get('course_key'), 'round_num': round.get('round_num')}
                hole_flat.update({f"{wave_key}_{key}": value for wave_key, wave_value in hole_flat.items() if isinstance(wave_value, dict) for key, value in wave_value.items()})
                flattened_data.append(hole_flat)
    return flattened_data

def create_holes_df(holes_data):
    logging.info("Creating holes DataFrame...")
    flattened_data = flatten_data(holes_data)
    holesdf = pd.DataFrame(flattened_data)

    # Ensure the columns are created
    holesdf['afternoon_wave_score_to_par'] = holesdf['afternoon_wave_avg_score'] - holesdf['par']
    holesdf['morning_wave_score_to_par'] = holesdf['morning_wave_avg_score'] - holesdf['par']
    holesdf['total_avg_score_to_par'] = holesdf['total_avg_score'] - holesdf['par']

    # Create percentage columns
    holesdf['morning_wave_birdie_percent'] = (holesdf['morning_wave_birdies'] / holesdf['morning_wave_players_thru']) * 100
    holesdf['morning_wave_par_percent'] = (holesdf['morning_wave_pars'] / holesdf['morning_wave_players_thru']) * 100
    holesdf['morning_wave_bogey_percent'] = (holesdf['morning_wave_bogeys'] / holesdf['morning_wave_players_thru']) * 100

    holesdf['afternoon_wave_birdie_percent'] = (holesdf['afternoon_wave_birdies'] / holesdf['afternoon_wave_players_thru']) * 100
    holesdf['afternoon_wave_par_percent'] = (holesdf['afternoon_wave_pars'] / holesdf['afternoon_wave_players_thru']) * 100
    holesdf['afternoon_wave_bogey_percent'] = (holesdf['afternoon_wave_bogeys'] / holesdf['afternoon_wave_players_thru']) * 100

    holesdf['total_birdie_percent'] = (holesdf['total_birdies'] / holesdf['total_players_thru']) * 100
    holesdf['total_par_percent'] = (holesdf['total_pars'] / holesdf['total_players_thru']) * 100
    holesdf['total_bogey_percent'] = (holesdf['total_bogeys'] / holesdf['total_players_thru']) * 100

    holesdf = holesdf.round(2)

    column_order = [
        'round_num', 'hole', 'par', 'yardage', 'morning_wave_avg_score', 'morning_wave_score_to_par',
        'afternoon_wave_avg_score', 'afternoon_wave_score_to_par', 'total_avg_score', 'total_avg_score_to_par',
        'morning_wave_birdies', 'morning_wave_pars', 'morning_wave_bogeys', 'morning_wave_doubles_or_worse', 'morning_wave_players_thru',
        'afternoon_wave_birdies', 'afternoon_wave_pars', 'afternoon_wave_bogeys', 'afternoon_wave_doubles_or_worse', 'afternoon_wave_players_thru',
        'total_birdies', 'total_pars', 'total_bogeys', 'total_doubles_or_worse', 'total_players_thru',
        'morning_wave_birdie_percent', 'morning_wave_par_percent', 'morning_wave_bogey_percent', 
        'afternoon_wave_birdie_percent', 'afternoon_wave_par_percent', 'afternoon_wave_bogey_percent',
        'total_birdie_percent', 'total_par_percent', 'total_bogey_percent'
    ]
    holesdf = holesdf[column_order]
    logging.info(f"holesdf created: {holesdf.head()}")
    return holesdf

def flatten_live_hole_score(data):
    flattened_data = []
    try:
        offer_categories = data.get('eventGroup', {}).get('offerCategories', [])
        for offer_category in offer_categories:
            offer_subcategory_descriptors = offer_category.get('offerSubcategoryDescriptors', [])
            for subcategory_descriptor in offer_subcategory_descriptors:
                subcategory_id = subcategory_descriptor.get('subcategoryId')
                if subcategory_id == 15278:
                    offer_subcategory = subcategory_descriptor.get('offerSubcategory')
                    if offer_subcategory is None:
                        continue
                    if isinstance(offer_subcategory, dict):
                        offers = offer_subcategory.get('offers', [])
                        for offer_group in offers:
                            for offer in offer_group:
                                event_label = offer.get('label', '')
                                round_num = extract_round_number(event_label) or 'Unknown'
                                hole = extract_hole_number(event_label) or 'Unknown'
                                participant = extract_participant(event_label) or 'Unknown Participant'
                                
                                for outcome in offer.get('outcomes', []):
                                    flattened_data.append({
                                        'event_id': offer.get('eventId'),
                                        'event_label': event_label,
                                        'provider_outcome_id': outcome.get('providerOutcomeId'),
                                        'provider_id': outcome.get('providerId'),
                                        'provider_offer_id': outcome.get('providerOfferId'),
                                        'outcome_label': outcome.get('label'),
                                        'odds_american': outcome.get('oddsAmerican'),
                                        'odds_decimal': outcome.get('oddsDecimal'),
                                        'odds_fractional': outcome.get('oddsFractional'),
                                        'round_num': round_num,
                                        'hole': hole,
                                        'participant': participant
                                    })
        df = pd.DataFrame(flattened_data)
        logging.info(f"flatten_live_hole_score output columns: {df.columns}")
        logging.info(f"flatten_live_hole_score sample data: {df.head()}")
        return df
    except Exception as e:
        logging.error(f"Error while flattening data: {e}")
        raise e

def flatten_live_hole_winner_3way(data):
    flattened_data = []

    logging.info(f"Initial data structure: {json.dumps(data, indent=2)[:1000]}")

    try:
        offer_categories = data.get('eventGroup', {}).get('offerCategories', [])
        for offer_category in offer_categories:
            logging.info(f"Processing offerCategory: {offer_category.get('name', 'Unnamed Category')}")
            offer_subcategory_descriptors = offer_category.get('offerSubcategoryDescriptors', [])
            for subcategory_descriptor in offer_subcategory_descriptors:
                subcategory_id = subcategory_descriptor.get('subcategoryId')
                subcategory_name = subcategory_descriptor.get('name')
                logging.info(f"Found subcategory with ID: {subcategory_id}, Name: {subcategory_name}")

                if subcategory_id == 11733:  # This ID should match the relevant subcategory for 3-way winner
                    offer_subcategory = subcategory_descriptor.get('offerSubcategory')
                    logging.info(f"Offer subcategory: {json.dumps(offer_subcategory, indent=2)[:1000]}")

                    if offer_subcategory is None:
                        logging.warning(f"Offer subcategory for ID 11733 is None")
                        continue

                    if isinstance(offer_subcategory, dict):
                        offers = offer_subcategory.get('offers', [])
                        for offer_group in offers:
                            for offer in offer_group:
                                event_label = offer.get('label', '')
                                round_num = extract_round_number(event_label)
                                hole = extract_hole_number(event_label)
                                participant = extract_participant_from_next_label(event_label, offer.get('outcomes', []))

                                for outcome in offer.get('outcomes', []):
                                    flattened_data.append({
                                        'event_id': offer.get('eventId'),
                                        'event_label': event_label,
                                        'provider_outcome_id': outcome.get('providerOutcomeId'),
                                        'provider_id': outcome.get('providerId'),
                                        'provider_offer_id': outcome.get('providerOfferId'),
                                        'outcome_label': outcome.get('label'),
                                        'odds_american': outcome.get('oddsAmerican'),
                                        'odds_decimal': outcome.get('oddsDecimal'),
                                        'odds_fractional': outcome.get('oddsFractional'),
                                        'round_num': round_num,
                                        'hole': hole,
                                        'participant': participant
                                    })

        df = pd.DataFrame(flattened_data)
        logging.info(f"Flattened DataFrame created with shape: {df.shape}")
        logging.info(f"Flattened DataFrame:\n{df.head()}")
        return df

    except Exception as e:
        logging.error(f"Error while flattening data: {e}")
        raise e

def extract_round_number(event_label):
    try:
        match = re.search(r'Round\s(\d+)', event_label, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    except Exception as e:
        logging.error(f"Error extracting round number from event_label: {event_label}, {e}")
        return None

def extract_hole_number(event_label):
    try:
        match = re.search(r'Hole\s(\d+)', event_label, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    except Exception as e:
        logging.error(f"Error extracting hole number from event_label: {event_label}, {e}")
        return None

def extract_participant(event_label):
    # Assuming the format "Participant Hole Score - Hole X - Round Y"
    try:
        pattern = re.compile(r'(.+?)\s-\sHole\s\d+\s-\sRound\s\d+')
        match = pattern.match(event_label)
        if match:
            return match.group(1).strip()
        raise ValueError(f"Error extracting participant from event_label: {event_label}")
    except ValueError as e:
        logging.error(e)
        return 'Unknown Participant'

def extract_participant_from_next_label(event_label, outcomes):
    # Assuming the participant is in the next label for "Hole 18 Winner (3 Way) - Round 4"
    try:
        for outcome in outcomes:
            if outcome.get('label'):
                return outcome.get('label').strip()
        return 'Unknown Participant'
    except Exception as e:
        logging.error(f"Error extracting participant from next label: {e}")
        return 'Unknown Participant'

def create_odds_df(flattened_data_odds):
    logging.info("Creating odds DataFrame...")
    oddsdf = pd.DataFrame(flattened_data_odds).assign(
        round_num=lambda df: df['round_num'],
        odds_decimal=lambda df: pd.to_numeric(df['odds_decimal'], errors='coerce'),
        implied_probability=lambda df: ((1 / df['odds_decimal']) * 100).round(2)
    )

    if 'participant' not in oddsdf.columns:
        oddsdf['participant'] = 'Unknown'

    column_order = ['round_num', 'hole', 'outcome_label', 'odds_american', 'odds_decimal', 'odds_fractional', 'implied_probability', 'participant']
    oddsdf = oddsdf[column_order]
    logging.info(f"oddsdf created: {oddsdf.head()}")
    return oddsdf


def merge_data(holes_df, odds_df):
    logging.info("Merging holes and odds data...")

    # Convert columns to the same type and ensure they exist
    if 'hole' in holes_df.columns and 'hole' in odds_df.columns:
        holes_df['hole'] = holes_df['hole'].astype(str)
        odds_df['hole'] = odds_df['hole'].astype(str)
    else:
        logging.error("Hole column missing in one of the dataframes.")
        raise KeyError("Hole column missing in one of the dataframes.")

    if 'round_num' in holes_df.columns and 'round_num' in odds_df.columns:
        holes_df['round_num'] = holes_df['round_num'].astype(str)
        odds_df['round_num'] = odds_df['round_num'].astype(str)
    else:
        logging.error("Round_num column missing in one of the dataframes.")
        raise KeyError("Round_num column missing in one of the dataframes.")

    # Use outer join to retain all rows from both dataframes
    merged_data = pd.merge(odds_df, holes_df, on=['round_num', 'hole'], how='outer')

    # Log merged dataframe sample
    logging.info(f"Merged DataFrame columns: {merged_data.columns.tolist()}")
    logging.info(f"Merged DataFrame sample:\n{merged_data.head()}")

    # Handle missing values in 'outcome_label'
    merged_data['outcome_label'] = merged_data['outcome_label'].fillna('unknown')

    # Ensure 'participant' column exists
    if 'participant' not in merged_data.columns:
        merged_data['participant'] = 'Unknown'

    # Fill None values in 'implied_probability' with 0
    merged_data['implied_probability'] = merged_data['implied_probability'].fillna(0)

    # Convert 'implied_probability' to numeric
    merged_data['implied_probability'] = pd.to_numeric(merged_data['implied_probability'], errors='coerce')

    # Assign new columns and log columns
    if 'outcome_label' in merged_data.columns:
        merged_data = merged_data.assign(
            stat_column=lambda df: df['outcome_label'].apply(get_stat_column),
            actual_implied_probability=lambda df: df.apply(get_stat_value, axis=1).round(2),
            Implied_Probability_Delta=lambda df: (df['actual_implied_probability'] - df['implied_probability']).round(2)
        )
        logging.info(f"Processed Merged DataFrame columns: {merged_data.columns.tolist()}")
    else:
        logging.error("'outcome_label' column not found in merged_data")
        raise KeyError("'outcome_label' column not found in merged_data")

    return merged_data

def get_stat_column(outcome_label):
    outcome_label = outcome_label.lower()
    if 'birdie' in outcome_label:
        return 'total_birdie_percent'
    elif 'par' in outcome_label:
        return 'total_par_percent'
    elif 'bogey' in outcome_label or 'bogey or worse' in outcome_label:
        return 'total_bogey_percent'
    else:
        return None

def get_stat_value(row):
    try:
        if pd.isnull(row['stat_column']):
            return 0
        stat_value = row.get(row['stat_column'], 0)
        return stat_value
    except Exception as e:
        logging.error(f"Error in get_stat_value: {e}")
        return 0


def fetch_live_stats(num_rounds=4):
    logging.info("Fetching live stats...")
    base_url = config.LIVE_STATS_BASE_URL
    rounds = [str(i) for i in range(1, num_rounds + 1)] + ["event_avg"]

    live_stats = {}
    for round in rounds:
        try:
            url = base_url.format(round)
            logging.info(f"Fetching data for round: {round} from {url}")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data:
                df = pd.json_normalize(data, record_path=['live_stats']).round(2)
                live_stats[round] = df
            else:
                logging.warning(f"No data returned for round {round}")
                live_stats[round] = pd.DataFrame()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for round {round}: {e}")
            live_stats[round] = pd.DataFrame()
        except ValueError as e:
            logging.error(f"Failed to decode JSON for round {round}: {e}")
            live_stats[round] = pd.DataFrame()

    logging.info("Live stats fetched successfully")
    return live_stats

def load_local_stats_data():
    logging.info("Loading local stats data...")
    rounds = [str(i) for i in range(1, 5)] + ["event_avg"]

    live_stats = {}
    for round in rounds:
        try:
            with open(f'live_stats_data_round_{round}.json', 'r') as f:
                round_data = json.load(f)
                live_stats_df = pd.json_normalize(round_data, record_path=['live_stats']).round(2)
                live_stats[round] = live_stats_df
            logging.info(f"Local data for round {round} loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading local data for round {round}: {e}")
            live_stats[round] = pd.DataFrame()

    logging.info("Local live stats data loaded successfully.")
    return live_stats

def load_and_prepare_score_data(holes_data_file, odds_data_file, live=False):
    logging.info("Loading and preparing score data...")
    holes_data, score_data = load_local_data(holes_data_file, odds_data_file)
    
    if holes_data is None or score_data is None:
        raise ValueError("Holes data or score data is None")
        
    logging.info(f"Holes data: {holes_data}")
    logging.info(f"Score data: {score_data}")
    
    holesdf = create_holes_df(holes_data)
    logging.info(f"holesdf: {holesdf.head()}")
    
    flattened_data_score = flatten_live_hole_score(score_data)
    logging.info(f"flattened_data_score: {flattened_data_score}")
    
    scoredf = create_odds_df(flattened_data_score)
    logging.info(f"scoredf: {scoredf.head()}")
    
    merged_df = merge_data(holesdf, scoredf)
    logging.info(f"merged_df: {merged_df.head()}")

    if live:
        live_stats_data = fetch_live_stats()
    else:
        live_stats_data = load_local_stats_data()

    required_columns = ["hole", "participant", "outcome_label", "odds_decimal", "actual_implied_probability", "Implied_Probability_Delta"]
    for col in required_columns:
        if col not in merged_df.columns:
            raise ValueError(f"Required column {col} is missing in merged_df")

    filtered_merged_df = merged_df.dropna(subset=required_columns)
    logging.info(f"filtered_merged_df: {filtered_merged_df.head()}")

    return holesdf, filtered_merged_df, live_stats_data, scoredf

def load_and_prepare_live_hole_winner_3way_data(holes_data_file, odds_data_file, live=False):
    logging.info("Loading and preparing live hole winner 3-way data...")
    holes_data, odds_data = load_local_data(holes_data_file, odds_data_file)
    if not holes_data or not odds_data:
        logging.error("Failed to load data.")
        return None, None, None, None

    try:
        holesdf = create_holes_df(holes_data)
        logging.info(f"Holes DataFrame:\n{holesdf.head()}")
        
        flattened_data_odds = flatten_live_hole_winner_3way(odds_data)
        
        # Log the flattened data
        logging.info(f"Flattened odds data: {json.dumps(flattened_data_odds, indent=2)[:1000]}")  # Log first 1000 characters

        oddsdf = create_odds_df(flattened_data_odds)
        logging.info(f"Odds DataFrame:\n{oddsdf.head()}")
        
        merged_df = merge_data(holesdf, oddsdf)
        filtered_merged_df = merged_df.dropna(subset=["hole", "participant", "outcome_label", "odds_decimal", "actual_implied_probability", "Implied_Probability_Delta"])
        
        if config.LIVE_STATS_DATA_SOURCE == 'live':
            live_stats_data = fetch_live_stats()
        else:
            live_stats_data = load_local_stats_data(config.ROUNDS_COMPLETED)

        # Store live stats data into the database
        engine = create_engine(f'postgresql://{config.DB_CONFIG["user"]}:{config.DB_CONFIG["password"]}@{config.DB_CONFIG["host"]}:{config.DB_CONFIG["port"]}/{config.DB_CONFIG["database"]}')
        store_live_stats_data(engine, live_stats_data)

        # Store holes data into the database
        holesdf.to_sql('holes_data', engine, if_exists='replace', index=False)
        oddsdf.to_sql('live_hole_winner_3way_odds_data', engine, if_exists='replace', index=False)
        logging.info("Data stored in the database successfully")

        return holesdf, filtered_merged_df, live_stats_data, oddsdf
    except Exception as e:
        logging.error(f"Error loading and preparing data: {e}")
        return None, None, None, None

def store_live_stats_data(engine, live_stats_data):
    try:
        for round, df in live_stats_data.items():
            table_name = f'live_stats_data_round_{round}'
            df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info("Live stats data stored in the database successfully")
    except Exception as e:
        logging.error(f"Error storing data in the database: {e}")
