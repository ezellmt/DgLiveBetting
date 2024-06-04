import dash
from dash import html
import dash_ag_grid as dag
import pandas as pd
from sqlalchemy import create_engine
import config
from layout_core import create_layout_with_sidebar
import logging

dash.register_page(__name__, path_template='/live_stats')

def fetch_live_stats_data():
    engine = create_engine(f'postgresql://{config.DB_CONFIG["user"]}:{config.DB_CONFIG["password"]}@{config.DB_CONFIG["host"]}:{config.DB_CONFIG["port"]}/{config.DB_CONFIG["database"]}')
    
    # List of tables to fetch
    tables = ['live_stats_data_round_1', 'live_stats_data_round_2', 'live_stats_data_round_3', 'live_stats_data_round_4', 'live_stats_data_round_event_avg']
    
    dataframes = []
    for table in tables:
        try:
            df = pd.read_sql_table(table, engine)
            dataframes.append(df)
        except Exception as e:
            logging.error(f"Error fetching data from {table}: {e}")
    
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df
    else:
        logging.error("No dataframes were fetched successfully.")
        return pd.DataFrame()

def layout(pathname):
    live_stats_df = fetch_live_stats_data()

    page_specific_content = html.Div([
    html.H2("Live Stats"),
    dag.AgGrid(
        id='live-stats-table',
        columnDefs=[
            {'headerName': 'Position', 'field': 'position', 'sortable': True, 'filter': False, 'minWidth': 70, 'maxWidth': 85},
            {'headerName': 'Player Name', 'field': 'player_name', 'sortable': True, 'filter': False, 'minWidth': 120, 'maxWidth': 150},
            {'headerName': 'Round', 'field': 'round', 'sortable': True, 'filter': False, 'minWidth': 60, 'maxWidth': 80},
            {'headerName': 'Thru', 'field': 'thru', 'sortable': True, 'filter': False, 'minWidth': 60, 'maxWidth': 80},
            {'headerName': 'Total', 'field': 'total', 'sortable': True, 'filter': False, 'minWidth': 60, 'maxWidth': 80},
            {'headerName': 'SG OTT', 'field': 'sg_ott', 'sortable': True, 'filter': False, 'minWidth': 80, 'maxWidth': 100,
             'cellStyle': {'function': 'window.dash_clientside.clientside.sgCellStyle'}},
            {'headerName': 'SG APP', 'field': 'sg_app', 'sortable': True, 'filter': False, 'minWidth': 80, 'maxWidth': 100,
             'cellStyle': {'function': 'window.dash_clientside.clientside.sgCellStyle'}},
            {'headerName': 'SG ARG', 'field': 'sg_arg', 'sortable': True, 'filter': False, 'minWidth': 80, 'maxWidth': 100,
             'cellStyle': {'function': 'window.dash_clientside.clientside.sgCellStyle'}},
            {'headerName': 'SG PUTT', 'field': 'sg_putt', 'sortable': True, 'filter': False, 'minWidth': 80, 'maxWidth': 100,
             'cellStyle': {'function': 'window.dash_clientside.clientside.sgCellStyle'}},
            {'headerName': 'SG T2G', 'field': 'sg_t2g', 'sortable': True, 'filter': False, 'minWidth': 80, 'maxWidth': 100,
             'cellStyle': {'function': 'window.dash_clientside.clientside.sgCellStyle'}},
            {'headerName': 'SG Total', 'field': 'sg_total', 'sortable': True, 'filter': False, 'minWidth': 80, 'maxWidth': 100,
             'cellStyle': {'function': 'window.dash_clientside.clientside.sgCellStyle'}},
        ],
        rowData=live_stats_df.to_dict('records'),
        defaultColDef={
            'sortable': True,
            'resizable': False,
            'filter': False,
            'floatingFilter': False,
            'flex': 1
        },
        className="ag-theme-quartz",
        style={'height': '600px', 'width': '100%', 'fontFamily': 'Roboto'}
    )
])
    return create_layout_with_sidebar(page_specific_content, html.Div(), pathname)
