# pages/live_betting/live_hole_score.py
'''
import dash
from dash import html
import dash_ag_grid as dag
import pandas as pd
from sqlalchemy import create_engine
import config
from layout_core import create_layout_with_sidebar

dash.register_page(__name__, path_template='/live_betting/live_hole_score')

def fetch_live_hole_score_data():
    engine = create_engine(f'postgresql://{config.DB_CONFIG["user"]}:{config.DB_CONFIG["password"]}@{config.DB_CONFIG["host"]}:{config.DB_CONFIG["port"]}/{config.DB_CONFIG["database"]}')
    query = 'SELECT * FROM live_hole_score_view'
    df = pd.read_sql_query(query, engine)
    df['implied_probability_delta'] = df['implied_probability_delta'].astype(float)
    return df

def create_top_bets_cards(df):
    top_bets = df.nlargest(3, 'implied_probability_delta')
    cards = []
    for _, row in top_bets.iterrows():
        card = html.Div(
            className='card',
            children=[
                html.Div(f"{row['participant']} {row['label']}", className='card-title'),
                html.Div(f"{row['hole']}th Hole ({row['oddsAmerican']})", className='card-content'),
                html.Div(f"{row['implied_probability_delta']:.2f}% Edge", className='card-footer'),
            ]
        )
        cards.append(card)
    return html.Div(className='top-bets-box', children=[
        html.H3("Top Bets", style={'textAlign': 'center'}),
        html.Div(className='cards-container', children=cards)
    ])

def layout(pathname):
    df = fetch_live_hole_score_data()
    top_bets_cards = create_top_bets_cards(df)

    page_specific_content = html.Div([
        html.H2("Live Hole Score", style={'textAlign': 'center'}),
        top_bets_cards,
        dag.AgGrid(
            id='live-hole-score-table',
            columnDefs=[
                {'headerName': 'Round Number', 'field': 'round_num', 'sortable': True, 'filter': False, 'minWidth': 70, 'maxWidth': 85},
                {'headerName': 'Hole', 'field': 'hole', 'sortable': True, 'filter': False, 'minWidth': 70, 'maxWidth': 85},
                {'headerName': 'Participant', 'field': 'participant', 'sortable': True, 'filter': False, 'minWidth': 120, 'maxWidth': 150},
                {'headerName': 'Label', 'field': 'label', 'sortable': True, 'filter': False, 'minWidth': 100, 'maxWidth': 140},
                {'headerName': 'Odds American', 'field': 'oddsAmerican', 'sortable': True, 'filter': False, 'minWidth': 80, 'maxWidth': 100},
                {'headerName': 'Implied Probability', 'field': 'implied_probability', 'sortable': True, 'filter': False, 'minWidth': 140, 'maxWidth': 180},
                {'headerName': 'Actual Implied Probability', 'field': 'actual_implied_probability', 'sortable': True, 'filter': False, 'minWidth': 140, 'maxWidth': 180},
                {'headerName': 'Implied Probability Delta', 'field': 'implied_probability_delta', 'sortable': True, 'filter': False, 'minWidth': 140, 'maxWidth': 180},
            ],
            rowData=df.to_dict('records'),
            defaultColDef={
                'sortable': True,
                'resizable': True,
                'filter': False,
                'floatingFilter': False,
                'flex': 1
            },
            className="ag-theme-quartz",
            style={'height': '600px', 'width': '100%', 'fontFamily': 'Roboto'}
        )
    ])

    return create_layout_with_sidebar(page_specific_content, html.Div(), pathname)
'''