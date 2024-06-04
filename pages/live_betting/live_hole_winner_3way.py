# pages/live_betting/live_hole_winner_3way.py

import dash
from dash import html
import dash_ag_grid as dag
import pandas as pd
from sqlalchemy import create_engine
import config
from layout_core import create_layout_with_sidebar

dash.register_page(__name__, path_template='/live_betting/live_hole_winner_3way')

def fetch_live_hole_winner_3way_data():
    engine = create_engine(f'postgresql://{config.DB_CONFIG["user"]}:{config.DB_CONFIG["password"]}@{config.DB_CONFIG["host"]}:{config.DB_CONFIG["port"]}/{config.DB_CONFIG["database"]}')
    query = 'SELECT * FROM "live_hole_winner_3way_odds_data"'
    df = pd.read_sql_query(query, engine)
    return df

def layout(pathname):
    page_specific_content = html.Div([
        html.H2("Live Hole Winner (3-Way)"),
        dag.AgGrid(
            id='live-hole-winner-3way-table',
            columnDefs=[
                {'headerName': 'Event ID', 'field': 'event_id', 'sortable': True, 'filter': False, 'minWidth': 70, 'maxWidth': 100},
                {'headerName': 'Event Label', 'field': 'event_label', 'sortable': True, 'filter': False, 'minWidth': 120, 'maxWidth': 200},
                {'headerName': 'Outcome Label', 'field': 'outcome_label', 'sortable': True, 'filter': False, 'minWidth': 100, 'maxWidth': 140},
                {'headerName': 'Odds American', 'field': 'odds_american', 'sortable': True, 'filter': False, 'minWidth': 80, 'maxWidth': 100},
                {'headerName': 'Odds Decimal', 'field': 'odds_decimal', 'sortable': True, 'filter': False, 'minWidth': 80, 'maxWidth': 100},
                {'headerName': 'Odds Fractional', 'field': 'odds_fractional', 'sortable': True, 'filter': False, 'minWidth': 80, 'maxWidth': 100},
                {'headerName': 'Implied Probability', 'field': 'implied_probability', 'sortable': True, 'filter': False, 'minWidth': 140, 'maxWidth': 180},
                {'headerName': 'Participant', 'field': 'participant', 'sortable': True, 'filter': False, 'minWidth': 100, 'maxWidth': 150},
            ],
            rowData=fetch_live_hole_winner_3way_data().to_dict('records'),
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
