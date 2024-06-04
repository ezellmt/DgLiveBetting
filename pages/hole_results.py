import dash
from dash import dcc, html
from layout_core import create_layout_with_sidebar
import config

dash.register_page(__name__, path="/hole_results")

round_options = [{'label': f'Round {i}', 'value': str(i)} for i in range(1, config.ROUNDS_COMPLETED + 1)]

page_specific_sidebar = [
    dcc.Dropdown(
        id='round-selector',
        options=round_options,
        value='1',
        clearable=False
    ),
   html.Br(),
    dcc.Dropdown(
        id='wave-selector',
        options=[
            {'label': 'Total', 'value': 'total'},
            {'label': 'Morning Wave', 'value': 'morning_wave'},
            {'label': 'Afternoon Wave', 'value': 'afternoon_wave'}
        ],
        value='total',
        clearable=False
    )
]

page_specific_content = html.Div([
    dcc.Graph(id='hole-by-hole-chart', className='dash-graph'),
    html.Div([
        dcc.Graph(id=f'hole-stats-chart-{i}', className='dash-graph', style={'width': '33%', 'display': 'inline-block'}) for i in range(1, 19)
    ])
], className="dash-content")

def layout(current_path):
    return create_layout_with_sidebar(page_specific_content, page_specific_sidebar, current_path)