'''
from dash import html, dcc
import dash_bootstrap_components as dbc

def create_sidebar(page_specific_sidebar):
    sidebar_content = html.Div(
        [
            html.H2("PGA Live Betting", className="sidebar-title"),
            html.Hr(),
            html.Div([
                html.A(
                    [html.I(className="fa-solid fa-golf-ball-tee"), " Hole Results"],
                    href="/hole_results",
                    className="nav-link"
                ),
                html.A(
                    [html.I(className="fas fa-table"), " Live Stats"],
                    href="/live_stats",
                    className="nav-link"
                ),
                html.A(
                    [html.I(className="fas fa-dollar-sign"), " Live Betting"],
                    href="/live_betting",
                    className="nav-link"
                )
            ]),
            html.Hr(),
            html.H3("Filters", className="filters-title"),
            html.Div(page_specific_sidebar),
        ],
        className="sidebar"
    )
    return sidebar_content

def create_layout_with_sidebar(content, page_specific_sidebar):
    return html.Div(
        [
            create_sidebar(page_specific_sidebar),
            html.Div(content, className="content")
        ]
    )
'''