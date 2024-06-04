'''
#import json
import pandas as pd
import requests
import logging
import config
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO)

def load_data(holes_data_file, odds_data_file):
    try:
        if holes_data_file.startswith('http'):
            logging.info(f"Fetching live data from {holes_data_file}")
            holes_response = requests.get(holes_data_file, timeout=10)
            holes_response.raise_for_status()
            holes_data = holes_response.json()
            logging.info(f"Live holes data fetched successfully: {len(holes_data['courses'])} courses")
        else:
            with open(holes_data_file, 'r') as f:
                holes_data = json.load(f)
            logging.info("Local holes data loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading holes data: {e}")
        holes_data = None

    try:
        if odds_data_file.startswith('http'):
            logging.info(f"Fetching live data from {odds_data_file}")
            odds_response = requests.get(odds_data_file, timeout=10)
            odds_response.raise_for_status()
            odds_data = odds_response.json()
            logging.info(f"Live odds data fetched successfully: {len(odds_data['eventGroup']['offerCategories'])} categories")
        else:
            with open(odds_data_file, 'r') as f:
                odds_data = json.load(f)
            logging.info("Local odds data loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading odds data: {e}")
        odds_data = None

    return holes_data, odds_data

def flatten_data(holes_data):
    flattened_data = []
    for course in holes_data['courses']:
        for round in course['rounds']:
            for hole in round['holes']:
                hole_flat = hole.copy()
                hole_flat.update({
                    'course_code': course.get('course_code'),
                    'course_key': course.get('course_key'),
                    'round_num': round.get('round_num')
                })
                for wave_key, wave_value in list(hole_flat.items()):
                    if isinstance(wave_value, dict):
                        for key, value in wave_value.items():
                            hole_flat[f"{wave_key}_{key}"] = value
                        del hole_flat[wave_key]
                flattened_data.append(hole_flat)
    return flattened_data

def create_holes_df(holes_data):
    logging.info("Creating holes DataFrame...")
    flattened_data = flatten_data(holes_data)
    holesdf = pd.DataFrame(flattened_data)
    holesdf['afternoon_wave_score_to_par'] = holesdf['afternoon_wave_avg_score'] - holesdf['par']
    holesdf['morning_wave_score_to_par'] = holesdf['morning_wave_avg_score'] - holesdf['par']
    holesdf['total_avg_score_to_par'] = holesdf['total_avg_score'] - holesdf['par']
    for prefix in ['morning_wave', 'afternoon_wave', 'total']:
        holesdf[f'{prefix}_birdie_%'] = (holesdf[f'{prefix}_birdies'] / holesdf[f'{prefix}_players_thru']) * 100
        holesdf[f'{prefix}_par_%'] = (holesdf[f'{prefix}_pars'] / holesdf[f'{prefix}_players_thru']) * 100
        holesdf[f'{prefix}_bogey_%'] = (holesdf[f'{prefix}_bogeys'] / holesdf[f'{prefix}_players_thru']) * 100
    holesdf = holesdf.round(2)
    column_order = [
        'round_num', 'hole', 'par', 'yardage', 'morning_wave_avg_score', 'morning_wave_score_to_par',
        'afternoon_wave_avg_score', 'afternoon_wave_score_to_par', 'total_avg_score', 'total_avg_score_to_par',
        'morning_wave_birdies', 'morning_wave_pars', 'morning_wave_bogeys', 'morning_wave_doubles_or_worse', 'morning_wave_players_thru',
        'afternoon_wave_birdies', 'afternoon_wave_pars', 'afternoon_wave_bogeys', 'afternoon_wave_doubles_or_worse', 'afternoon_wave_players_thru',
        'total_birdies', 'total_pars', 'total_bogeys', 'total_doubles_or_worse', 'total_players_thru',
        'morning_wave_birdie_%', 'morning_wave_par_%', 'morning_wave_bogey_%', 'afternoon_wave_birdie_%', 'afternoon_wave_par_%', 'afternoon_wave_bogey_%',
        'total_birdie_%', 'total_par_%', 'total_bogey_%'
    ]
    holesdf = holesdf[column_order]
    logging.info(f"holesdf created: {holesdf.head()}")
    return holesdf

# Add print_json_structure function here
def print_json_structure(data, indent=0):
    """Print the structure of a JSON object"""
    for key, value in data.items():
        logging.info(f"{' ' * indent}{key}: {type(value).__name__}")
        if isinstance(value, dict):
            print_json_structure(value, indent + 2)
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            logging.info(f"{' ' * (indent + 2)}[0]: {type(value[0]).__name__}")
            print_json_structure(value[0], indent + 4)
            
def flatten_live_hole_winner_3way(data):
    flattened_data = []

    try:
        for offer_category in data.get('eventGroup', {}).get('offerCategories', []):
            logging.info(f"Processing offerCategory: {offer_category.get('name', 'Unnamed Category')}")
            for subcategory in offer_category.get('offerSubcategoryDescriptors', []):
                logging.info(f"Processing subcategory: {subcategory.get('name', 'Unnamed Subcategory')}")
                offer_subcategory = subcategory.get('offerSubcategory')

                # Check if offer_subcategory is a list or a dict
                if isinstance(offer_subcategory, dict):
                    offers = offer_subcategory.get('offers', [])
                elif isinstance(offer_subcategory, list):
                    offers = offer_subcategory
                else:
                    offers = []

                for offer in offers:
                    logging.info(f"Processing offer: {offer.get('label', 'Unnamed Offer')}")
                    for outcome in offer.get('outcomes', []):
                        flattened_data.append({
                            'event_id': offer.get('eventId'),
                            'event_label': offer.get('label'),
                            'provider_outcome_id': outcome.get('providerOutcomeId'),
                            'provider_id': outcome.get('providerId'),
                            'provider_offer_id': outcome.get('providerOfferId'),
                            'outcome_label': outcome.get('label'),
                            'odds_american': outcome.get('oddsAmerican'),
                            'odds_decimal': outcome.get('oddsDecimal'),
                            'odds_fractional': outcome.get('oddsFractional'),
                            'participant': outcome.get('participant')
                        })

        df = pd.DataFrame(flattened_data)
        logging.info(f"Flattened DataFrame created with shape: {df.shape}")
        logging.info(f"Flattened DataFrame:\n{df.head()}")
        return df

    except Exception as e:
        logging.error(f"Error while flattening data: {e}")
        raise e

def create_odds_df(flattened_data_odds):
    logging.info("Creating odds DataFrame...")
    oddsdf = pd.DataFrame(flattened_data_odds)
    oddsdf['event_label_parts'] = oddsdf['event_label'].str.split(' - ')
    oddsdf['hole'] = oddsdf['event_label_parts'].apply(lambda x: int(x[1].split(' ')[1]) if len(x) > 1 else None)
    oddsdf['round_num'] = oddsdf['event_label_parts'].apply(lambda x: int(x[2].split(' ')[1]) if len(x) > 2 else None)
    oddsdf = oddsdf.drop(columns=['event_label_parts'])
    oddsdf['oddsDecimal'] = pd.to_numeric(oddsdf['oddsDecimal'], errors='coerce')
    oddsdf['implied_probability'] = ((1 / oddsdf['oddsDecimal']) * 100).round(2)
    oddsdf_new_column_order = ['round_num', 'hole', 'label', 'oddsAmerican', 'oddsDecimal', 'oddsFractional', 'implied_probability']
    oddsdf = oddsdf[oddsdf_new_column_order]
    logging.info(f"oddsdf created: {oddsdf.head()}")
    return oddsdf

def merge_data(holesdf, oddsdf):
    logging.info("Merging holes and odds data...")
    merged_data = pd.merge(oddsdf, holesdf, on=['round_num', 'hole'], how='left')
    merged_data['stat_column'] = merged_data['label'].apply(get_stat_column)
    merged_data['actual_implied_probability'] = merged_data.apply(get_stat_value, axis=1).round(2)
    merged_data['Implied_Probability_Delta'] = (merged_data['actual_implied_probability'] - merged_data['implied_probability']).round(2)
    logging.info(f"Merged data: {merged_data.head()}")
    return merged_data

def get_stat_column(label):
    label = label.lower()
    if 'birdie' in label:
        return 'total_birdie_%'
    elif 'par' in label:
        return 'total_par_%'
    elif 'bogey' in label:
        return 'total_bogey_%'
    else:
        return None

def get_stat_value(row):
    if pd.isnull(row['stat_column']):
        return None
    else:
        return row[row['stat_column']]

def fetch_live_stats(num_rounds=4):
    logging.info("Fetching live stats...")
    base_url = config.LIVE_STATS_BASE_URL
    rounds = [str(i) for i in range(1, num_rounds + 1)] + ["event_avg"]

    live_stats = {}
    for round in rounds:
        url = base_url.format(round)
        logging.info(f"Fetching data for round: {round} from {url}")
        response = requests.get(url)
        try:
            response.raise_for_status()
            data = response.json()
            if data:
                df = pd.json_normalize(data, record_path=['live_stats'])
                df = df.round(2)
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
        local_file = f'live_stats_data_round_{round}.json'
        try:
            with open(local_file, 'r') as f:
                round_data = json.load(f)
                live_stats_df = pd.json_normalize(round_data, record_path=['live_stats'])
                live_stats[round] = live_stats_df
            logging.info(f"Local data for round {round} loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading local data for round {round}: {e}")
            live_stats[round] = pd.DataFrame()

    logging.info("Local live stats data loaded successfully.")
    return live_stats

def load_and_prepare_data(holes_data_file, odds_data_file, live=False):
    logging.info("Loading and preparing data...")
    holes_data, odds_data = load_data(holes_data_file, odds_data_file)
    holesdf = create_holes_df(holes_data)
    logging.info(f"holesdf: {holesdf.head()}")
    
    flattened_data_odds = flatten_live_hole_winner_3way(odds_data)
    oddsdf = create_odds_df(flattened_data_odds)
    logging.info(f"oddsdf: {oddsdf.head()}")
    
    merged_df = merge_data(holesdf, oddsdf)
    logging.info(f"merged_df: {merged_df.head()}")
    merged_df['Vegas Odds/Implied Probability'] = merged_df.get('Vegas Odds/Implied Probability')
    merged_df['actual_implied_probability'] = merged_df.get('actual_implied_probability')
    filtered_merged_df = merged_df.dropna(subset=["hole", "participant", "label", "oddsDecimal", "actual_implied_probability", "Implied_Probability_Delta"])
    
    live_stats_data = fetch_live_stats() if live else load_local_stats_data()
    return holesdf, filtered_merged_df, live_stats_data, oddsdf
'''