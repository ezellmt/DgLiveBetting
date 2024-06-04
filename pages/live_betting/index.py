import dash
from dash import html, dcc

dash.register_page(__name__, path="/live_betting_home")

layout = html.Div([
    html.H1("Live Betting Home"),
    html.P("Welcome to the Live Betting Home Page!")
])