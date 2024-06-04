import dash
from dash import dcc, html
from layout_core import create_layout_with_sidebar

dash.register_page(__name__, path="/live_betting")

page_specific_sidebar = [
    # Add any page-specific sidebar components here if necessary
]

page_specific_content = html.Div([
    # Add any page-specific content here if necessary
], className="dash-content")

def layout(current_path):
    return create_layout_with_sidebar(page_specific_content, page_specific_sidebar, current_path)
