from dash import dcc, html

def create_layout():
    return html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='sidebar-content'),
        html.Div(id='page-content', className='dash-content', style={"margin-left": "350px", "padding": "20px"})
    ])
