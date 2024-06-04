# layout_core.py
from dash import html

def create_sidebar(current_path, page_specific_sidebar):
    sidebar_links = [
        {'name': 'Live Betting', 'path': '/live_betting', 'icon': 'fas fa-dollar-sign'},
        {'name': 'Live Finishing Position', 'path': '/live_betting/live_finishing_position', 'icon': 'fas fa-flag-checkered'},
        {'name': 'Live Matchups', 'path': '/live_betting/live_matchups', 'icon': 'fas fa-users'},
        {'name': 'Live Hole Winner (2-Way)', 'path': '/live_betting/live_hole_winner_2way', 'icon': 'fas fa-golf-ball'},
        {'name': 'Live Hole Winner (3-Way)', 'path': '/live_betting/live_hole_winner_3way', 'icon': 'fas fa-golf-ball'},
        {'name': 'Live Hole Score', 'path': '/live_betting/live_hole_score', 'icon': 'fas fa-chart-line'},
        {'name': 'Live Stats', 'path': '/live_stats', 'icon': 'fas fa-table'},
        {'name': 'Hole Results', 'path': '/hole_results', 'icon': 'fas fa-flag'}
    ]

    links = [
        html.A(
            [html.I(className=link['icon']), html.Span(link['name'])],
            href=link['path'],
            className='nav-link' + (' active' if link['path'] == current_path else '')
        ) for link in sidebar_links
    ]

    return html.Div([
        html.H2("PGA Live Betting", className="sidebar-title"),
        html.Div(links),
        html.Hr(),
        html.H3("Filters", className="filters-title"),
        html.Div(page_specific_sidebar)
    ], className="sidebar")

def create_layout_with_sidebar(content_layout, page_specific_sidebar, current_path):
    return html.Div([
        create_sidebar(current_path, page_specific_sidebar),
        html.Div(content_layout, className="content")
    ])
