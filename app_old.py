'''
import dash
from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import logging
from data_loader import (
    load_and_prepare_data,
    load_and_prepare_live_hole_winner_3way_data,
    fetch_data_from_db,
    fetch_and_store_live_hole_score_data,
    fetch_and_store_live_hole_winner_3way_data,  # Ensure this is imported
    fetch_and_store_data  # Ensure this is imported
)
from callbacks import register_callbacks
import config

# Set React version before Dash instantiation
dash._dash_renderer._set_react_version("18.2.0")

app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css", "cards.css"
], suppress_callback_exceptions=True, use_pages=True)

# Ensure Poppins font and other configurations
app.index_string =
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700&display=swap" rel="stylesheet">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>

# Configuration: Set to 'local' or 'live'
HOLES_DATA_SOURCE = config.HOLES_DATA_SOURCE
LIVE_HOLE_SCORE_ODDS_DATA_SOURCE = config.LIVE_HOLE_SCORE_ODDS_DATA_SOURCE
LIVE_HOLE_WINNER_3WAY_ODDS_DATA_SOURCE = config.LIVE_HOLE_WINNER_3WAY_ODDS_DATA_SOURCE
LIVE_STATS_DATA_SOURCE = config.LIVE_STATS_DATA_SOURCE
EVENTGROUP = config.EVENTGROUP

# Fetch live data and store locally
if HOLES_DATA_SOURCE == 'live':
    holes_data_url = config.HOLES_DATA_URL
else:
    holes_data_url = config.LOCAL_HOLES_DATA_FILE

if LIVE_HOLE_SCORE_ODDS_DATA_SOURCE == 'live':
    odds_data_url = config.LIVE_HOLE_SCORE_ODDS_DATA_URL_TEMPLATE.format(EVENTGROUP)
else:
    odds_data_url = config.LOCAL_LIVE_HOLE_SCORE_ODDS_DATA_FILE

if LIVE_STATS_DATA_SOURCE == 'live':
    fetch_and_store_live_hole_score_data(config.HOLES_DATA_URL, config.LIVE_HOLE_SCORE_ODDS_DATA_URL_TEMPLATE.format(EVENTGROUP))

# Load data based on the configuration
holesdf, filtered_merged_df, live_stats_data, oddsdf = load_and_prepare_data(EVENTGROUP, live=(HOLES_DATA_SOURCE == 'live'))

# Confirm data loading
logging.info("Data loaded and prepared successfully.")

# Fetch data from the database
holesdf = fetch_data_from_db('holes_data')
oddsdf = fetch_data_from_db('live_hole_score_odds_data')
# Assuming live_stats_data is stored in multiple tables or a different format, adjust this as needed
live_stats_data = {
    '1': fetch_data_from_db('live_stats_data_round_1'),
    '2': fetch_data_from_db('live_stats_data_round_2'),
    '3': fetch_data_from_db('live_stats_data_round_3'),
    '4': fetch_data_from_db('live_stats_data_round_4'),
    'event_avg': fetch_data_from_db('live_stats_data_round_event_avg')
}

# Import the layout functions for each page
from pages.live_betting.index import layout as live_betting_layout
from pages.live_betting.live_finishing_position import layout as live_finishing_position_layout
from pages.live_betting.live_matchups import layout as live_matchups_layout
from pages.live_betting.live_hole_winner_2way import layout as live_hole_winner_2way_layout
from pages.live_betting.live_hole_winner_3way import layout as live_hole_winner_3way_layout
from pages.live_betting.live_hole_score import layout as live_hole_score_layout
from pages.live_stats import layout as live_stats_layout
from pages.hole_results import layout as hole_results_layout

# Sidebar function
def create_sidebar(current_path):
    sidebar_links = [
        {'name': 'Live Betting', 'path': '/live_betting', 'icon': 'fas fa-dollar-sign'},
        {'name': 'Live Stats', 'path': '/live_stats', 'icon': 'fas fa-table'},
        {'name': 'Hole Results', 'path': '/hole_results', 'icon': 'fas fa-golf-ball'},
        {'name': 'Live Finishing Position', 'path': '/live_betting/live_finishing_position', 'icon': 'fas fa-flag-checkered'},
        {'name': 'Live Matchups', 'path': '/live_betting/live_matchups', 'icon': 'fas fa-user-friends'},
        {'name': 'Live Hole Winner (2-Way)', 'path': '/live_betting/live_hole_winner_2way', 'icon': 'fas fa-trophy'},
        {'name': 'Live Hole Winner (3-Way)', 'path': '/live_betting/live_hole_winner_3way', 'icon': 'fas fa-trophy'},
        {'name': 'Live Hole Score', 'path': '/live_betting/live_hole_score', 'icon': 'fas fa-chart-bar'}
    ]

    links = [
        html.A(
            [html.I(className=link['icon']), html.Span(link['name'])],
            href=link['path'],
            className='nav-link' + (' active' if link['path'] == current_path else '')
        ) for link in sidebar_links
    ]

    return html.Div([
        html.H2("PGA Live Betting", className="sidebar-title"),
        html.Div(links),
        html.Hr(),
        html.H3("Filters", className="filters-title")
    ], className="sidebar")

# Define the main layout with a sidebar wrapped in MantineProvider
app.layout = dmc.MantineProvider(
    children=[
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-container')
    ]
)

# Define a dictionary mapping paths to layout functions
page_layouts = {
    '/live_betting': live_betting_layout,
    '/live_betting/live_finishing_position': live_finishing_position_layout,
    '/live_betting/live_matchups': live_matchups_layout,
    '/live_betting/live_hole_winner_2way': live_hole_winner_2way_layout,
    '/live_betting/live_hole_winner_3way': live_hole_winner_3way_layout,
    '/live_betting/live_hole_score': live_hole_score_layout,
    '/live_stats': live_stats_layout,
    '/hole_results': hole_results_layout
}

@app.callback(
    Output('page-container', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    stripped_pathname = pathname.strip("/")
    full_pathname = f"/{stripped_pathname}"
    logging.info(f"Full pathname for registry match: {full_pathname}")

    layout_function = page_layouts.get(full_pathname)
    if layout_function:
        return layout_function(pathname)
    else:
        logging.info("Page not found, returning 404")
        return html.Div("404 Page Not Found")

# Register the callbacks
register_callbacks(app, holesdf, filtered_merged_df, live_stats_data, oddsdf)

if __name__ == '__main__':
    logging.info("Starting Dash server...")
    app.run_server(debug=True)

'''