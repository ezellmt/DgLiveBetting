# live_betting/__init__.py
from dash import html, dcc, register_page
from layout_core import create_layout_with_sidebar

register_page(__name__, path="/live_betting")

page_specific_content = html.Div([
    html.H1("Live Betting"),
    dcc.Link('Live Finishing Position', href='/live_betting/live_finishing_position'),
    dcc.Link('Live Matchups', href='/live_betting/live_matchups'),
    dcc.Link('Live Hole Winner (2-Way)', href='/live_betting/live_hole_winner_2way'),
    dcc.Link('Live Hole Winner (3-Way)', href='/live_betting/live_hole_winner_3way'),
    dcc.Link('Live Hole Score', href='/live_betting/live_hole_score'),
])

layout = create_layout_with_sidebar(page_specific_content, html.Div(), "/live_betting")
