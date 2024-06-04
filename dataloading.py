import json
import pandas as pd
import logging
logging.basicConfig(level=logging.INFO)

# Load the JSON files

def load_data(file1, file2):
    with open(file1) as f1:
        holes_data = json.load(f1)
    with open(file2) as f2:
        odds_data = json.load(f2)
    return holes_data, odds_data

# Create a function to convert implied probability to American odds. For example, a 50% implied probability would be -100 in American odds. The value being passed in is a percentage already converted (e.g. 70% is 70).
def probability_to_american_odds(probability):
    # Convert probability to percentage if it's in decimal form
    if probability < 1:
        probability *= 100

    # Convert probability to American odds
    if probability > 50:
        american_odds = - (100 / (probability / 100 - 1))
    else:
        american_odds = (100 / (1 - probability / 100)) - 100

    return round(american_odds)

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
                hole_flat_copy = hole_flat.copy()
                for wave_key, wave_value in hole_flat_copy.items():
                    if isinstance(wave_value, dict):
                        for key, value in wave_value.items():
                            hole_flat[f"{wave_key}_{key}"] = value
                        del hole_flat[wave_key]
                flattened_data.append(hole_flat)
    return flattened_data

# Create a function to create the DataFrame from the flattened data above

def create_holes_df(holes_data):
    flattened_data = flatten_data(holes_data)
    holesdf = pd.DataFrame(flattened_data)
    # Calculate 'afternoon_wave_score_to_par' and 'morning_wave_score_to_par' and round to 2 decimal places
    holesdf['afternoon_wave_score_to_par'] = holesdf['afternoon_wave_avg_score'] - holesdf['par']
    holesdf['morning_wave_score_to_par'] = holesdf['morning_wave_avg_score'] - holesdf['par']
    holesdf['total_avg_score_to_par'] =  holesdf['total_avg_score'] - holesdf['par']

    # Calculate percentages for morning wave
    holesdf['morning_wave_birdie_%'] = (holesdf['morning_wave_birdies'] / holesdf['morning_wave_players_thru']) * 100
    holesdf['morning_wave_par_%'] = (holesdf['morning_wave_pars'] / holesdf['morning_wave_players_thru']) * 100
    holesdf['morning_wave_bogey_%'] = (holesdf['morning_wave_bogeys'] / holesdf['morning_wave_players_thru']) * 100

    # Calculate percentages for afternoon wave
    holesdf['afternoon_wave_birdie_%'] = (holesdf['afternoon_wave_birdies'] / holesdf['afternoon_wave_players_thru']) * 100
    holesdf['afternoon_wave_par_%'] = (holesdf['afternoon_wave_pars'] / holesdf['afternoon_wave_players_thru']) * 100
    holesdf['afternoon_wave_bogey_%'] = (holesdf['afternoon_wave_bogeys'] / holesdf['afternoon_wave_players_thru']) * 100

    # Calculate percentages for total
    holesdf['total_birdie_%'] = (holesdf['total_birdies'] / holesdf['total_players_thru']) * 100
    holesdf['total_par_%'] = (holesdf['total_pars'] / holesdf['total_players_thru']) * 100
    holesdf['total_bogey_%'] = (holesdf['total_bogeys'] / holesdf['total_players_thru']) * 100

    # Round all columns to 2 decimal places
    holesdf = holesdf.round(2)

    new_column_order = ['round_num', 'hole', 'par', 'yardage', 'morning_wave_avg_score', 'morning_wave_score_to_par', 'afternoon_wave_avg_score', 'afternoon_wave_score_to_par', 'total_avg_score', 'total_avg_score_to_par', 'morning_wave_birdies', 'morning_wave_pars', 'morning_wave_bogeys', 'morning_wave_doubles_or_worse', 'morning_wave_players_thru', 'afternoon_wave_birdies', 'afternoon_wave_pars', 'afternoon_wave_bogeys', 'afternoon_wave_doubles_or_worse', 'afternoon_wave_players_thru', 'total_birdies', 'total_pars', 'total_bogeys', 'total_doubles_or_worse', 'total_players_thru', 'morning_wave_birdie_%', 'morning_wave_par_%', 'morning_wave_bogey_%', 'afternoon_wave_birdie_%', 'afternoon_wave_par_%', 'afternoon_wave_bogey_%', 'total_birdie_%', 'total_par_%', 'total_bogey_%']
    holesdf = holesdf[new_column_order]
    holesdf.to_excel('holes_data.xlsx', index=False)
    # Print the column names of the odds DataFrame as part of an F-String
    logging.info(f"Column names of the holes DataFrame: {holesdf.columns}")
    
    return holesdf

# Create a function to flatten the odds data
def flatten_odds_data(odds_data):
    flattened_data_odds = []
    for offerCategory in odds_data['eventGroup']['offerCategories']:
        if offerCategory['offerCategoryId'] == 1172:
            for subcategory in offerCategory['offerSubcategoryDescriptors']:
                if subcategory['subcategoryId'] == 15278:
                    for offer in subcategory['offerSubcategory']['offers']:
                        for event in offer:
                            event_label = event['label']
                            for outcome in event['outcomes']:
                                outcome_flat = outcome.copy()
                                outcome_flat['event_label'] = event_label
                                flattened_data_odds.append(outcome_flat)
    return flattened_data_odds

# Create a function to create the DataFrame from the flattened odds data above
def create_odds_df(flattened_data_odds):
    oddsdf = pd.DataFrame(flattened_data_odds)
    oddsdf['event_label_parts'] = oddsdf['event_label'].str.split(' - ')
    oddsdf['hole'] = oddsdf['event_label_parts'].apply(lambda x: int(x[1].split(' ')[1]) if len(x) > 1 else None)
    oddsdf['round_num'] = oddsdf['event_label_parts'].apply(lambda x: int(x[2].split(' ')[1]) if len(x) > 2 else None)
    oddsdf = oddsdf.drop(columns=['event_label_parts'])
    oddsdf_new_column_order = ['round_num', 'hole', 'participant', 'label', 'oddsDecimal', 'oddsFractional', 'oddsAmerican']
    oddsdf = oddsdf[oddsdf_new_column_order]
    oddsdf['oddsDecimal'] = pd.to_numeric(oddsdf['oddsDecimal'], errors='coerce')
    oddsdf['implied_probability'] = (1 / oddsdf['oddsDecimal'] * 100).round(2)
    oddsdf.to_excel('odds_data.xlsx', index=False)
    # Print the column names of the odds DataFrame as part of an F-String
    logging.info(f"Column names of the odds DataFrame: {oddsdf.columns}")
    return oddsdf

# Create a function to merge the holes and odds DataFrames
def merge_data(holesdf, oddsdf):
    merged_data = pd.merge(holesdf, oddsdf, on=['round_num', 'hole'], how='left')
    merged_data.to_excel('merged_data.xlsx', index=False)
    return merged_data

def main():
    holes_data, odds_data = load_data('dgscoreresults.json', 'liveholebetting.json')
    holesdf = create_holes_df(holes_data)
    flattened_data_odds = flatten_odds_data(odds_data)
    oddsdf = create_odds_df(flattened_data_odds)
    merged_data = merge_data(holesdf, oddsdf)

if __name__ == '__main__':
    main()

def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix

# Print the column names of the two DataFrames, but they are included in functions above