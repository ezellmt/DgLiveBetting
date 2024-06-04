import dash
from dash import html, dcc
from layout_core import create_layout_with_sidebar

dash.register_page(__name__, path="/live_betting/matchups")

layout = html.Div([
    html.H1("Live Hole Winner (2-Way)"),
    html.P("Details about live hole winner (2-way) betting.")
])
def layout(pathname):
    page_specific_content = html.Div([
        html.H2("Live Hole Winner (2-Way)")
        # Add other elements as needed
    ])

    return create_layout_with_sidebar(page_specific_content, html.Div(), pathname)