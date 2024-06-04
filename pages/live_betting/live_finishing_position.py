# live_betting/live_finishing_position.py
import dash
from dash import html
from layout_core import create_layout_with_sidebar

dash.register_page(__name__, path_template='/live_betting/live_finishing_position')

def layout(pathname):
    page_specific_content = html.Div([
        html.H2("Live Finishing Position")
        # Add other elements as needed
    ])

    return create_layout_with_sidebar(page_specific_content, html.Div(), pathname)
