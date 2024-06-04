'''
# main.py
from data_import import load_data, create_holes_df, create_odds_df, merge_data, flatten_odds_data
import plotly.express as px
import logging

def main():
    holes_data, odds_data = load_data('dgscoreresults.json', 'liveholebetting.json')
    
    holesdf = create_holes_df(holes_data)
    flattened_data_odds = flatten_odds_data(odds_data)
    oddsdf = create_odds_df(flattened_data_odds)
    
    merged_data = merge_data(holesdf, oddsdf)
    
    # Debug: Check DataFrames
    logging.info(f"Column names of the holes DataFrame: {holesdf.columns}")
    logging.info(f"Column names of the odds DataFrame: {oddsdf.columns}")
    logging.info(f"Column names of the merged DataFrame: {merged_data.columns}")
    
    # Ensure column names are as expected
    print(holesdf.columns)
    print(oddsdf.columns)
    print(merged_data.columns)
    
    # Create a bar chart: Total Average Score by Round
    fig1 = px.bar(holesdf, x='round_num', y='total_avg_score', title='Total Average Score by Round')
    fig1.show()
    
    # Create a line chart: Morning Wave Average Score by Hole
    fig2 = px.line(holesdf, x='hole', y='morning_wave_avg_score', title='Morning Wave Average Score by Hole', color='round_num')
    fig2.show()
    
    # Create a scatter plot: Implied Probability vs. American Odds
    fig3 = px.scatter(oddsdf, x='implied_probability', y='oddsAmerican', title='Implied Probability vs. American Odds', color='participant')
    fig3.show()
    
    # Create a bar chart: Total Birdies by Hole
    fig4 = px.bar(holesdf, x='hole', y='total_birdies', title='Total Birdies by Hole', color='round_num')
    fig4.show()

if __name__ == '__main__':
    main()
'''