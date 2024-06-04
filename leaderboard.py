import pandas as pd
import json

def get_leaderboard_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Print the top-level keys in the JSON
    print("Top level keys:", data.keys())
    
    if 'pga' in data and 'lb' in data['pga']:
        pga_data = data['pga']['lb']
    else:
        raise KeyError("Key 'lb' not found in the JSON data within 'pga'.")

    # Extract relevant fields
    leaderboard_data = []
    for player in pga_data:
        leaderboard_data.append({
            'name': f"{player['f']} {player['l']}",
            'position': player['p'],
            'score': player['s']
        })

    pga_df = pd.DataFrame(leaderboard_data)
    
    # Sort by position, handling the 'T' prefix correctly
    pga_df['position'] = pga_df['position'].apply(lambda x: int(x[1:]) if 'T' in x else int(x))
    pga_df = pga_df.sort_values(by='position')
    
    return pga_df

