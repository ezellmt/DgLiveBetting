import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html
from config import COLORS

def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

def create_column_defs():
    return [
        {"headerName": "Position", "field": "position", "sortable": True, "width": 70},
        {"headerName": "Player Name", "field": "player_name", "sortable": True, "width": 250},
        {"headerName": "Round", "field": "round", "sortable": True, "width": 50},
        {"headerName": "Thru", "field": "thru", "sortable": True, "width": 50},
        {"headerName": "Total", "field": "total", "sortable": True, "width": 50},
        {"headerName": "SG OTT", "field": "sg_ott", "sortable": True, "width": 100},
        {"headerName": "SG APP", "field": "sg_app", "sortable": True, "width": 100},
        {"headerName": "SG ARG", "field": "sg_arg", "sortable": True, "width": 100},
        {"headerName": "SG PUTT", "field": "sg_putt", "sortable": True, "width": 100},
        {"headerName": "SG T2G", "field": "sg_t2g", "sortable": True, "width": 100},
        {"headerName": "SG Total", "field": "sg_total", "sortable": True, "width": 100},
    ]

def create_figure(oddsdf, round_num, wave):
    print(f"Creating figure for round: {round_num}, wave: {wave}")
    filtered_df = oddsdf[oddsdf['round_num'] == int(round_num)]
    print(f"Filtered DataFrame columns: {filtered_df.columns}")
    if filtered_df.empty:
        print(f"No data found for round: {round_num}")
        return go.Figure()
    x_labels = filtered_df.apply(lambda row: f"{ordinal(int(row['hole']))}<br>Par {int(row['par'])}<br>{int(row['yardage'])} yds", axis=1)
    avg_score_field = f"{wave}_score_to_par" if wave != 'total' else 'total_avg_score_to_par'
    fig = go.Figure(data=[
        go.Bar(
            x=x_labels,
            y=filtered_df[avg_score_field],
            marker_color = filtered_df[avg_score_field].apply(lambda x: COLORS["primary"] if x < 0 else COLORS["secondary"]),
            # Chart Background Color
                
            text=filtered_df[avg_score_field].apply(lambda x: f"{x:.2f}"),
            textposition='outside'
        )
    ])
    fig.update_layout(
        title={
            'text': 'Scoring Average to Par by Hole',
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.9,
            'yanchor': 'top',
            'font': dict(size=24, family='Roboto')
        },
        font=dict(family='Roboto'),
        barmode='relative'
    )
    fig.update_xaxes(title='Hole', tickmode='array', tickvals=x_labels, ticktext=x_labels)
    fig.update_yaxes(title='Avg Score to Par', tickmode='linear', tick0=0, dtick=0.1, range=[filtered_df[avg_score_field].min() - 0.1, filtered_df[avg_score_field].max() + 0.1])
    return fig

def create_pie_chart(oddsdf, round_num, wave, hole_num):
    print(f"Creating pie chart for round: {round_num}, wave: {wave}, hole: {hole_num}")
    filtered_df = oddsdf[(oddsdf['round_num'] == int(round_num)) & (oddsdf['hole'] == hole_num)]
    print(f"Filtered DataFrame columns: {filtered_df.columns}")
    if filtered_df.empty:
        print(f"No data found for round: {round_num}, wave: {wave}, hole: {hole_num}")
        return px.pie(
            values=[1], 
            names=['No Data'], 
            title=f'Stats for Hole {hole_num}',
            hole=0.4
        )
    birdies_field = f"{wave}_birdies"
    pars_field = f"{wave}_pars"
    bogeys_field = f"{wave}_bogeys"
    players_thru_field = f"{wave}_players_thru"
    birdies = filtered_df[birdies_field].values[0]
    pars = filtered_df[pars_field].values[0]
    bogeys = filtered_df[bogeys_field].values[0]
    birdies_pct = birdies / filtered_df[players_thru_field].values[0]
    pars_pct = pars / filtered_df[players_thru_field].values[0]
    bogeys_pct = bogeys / filtered_df[players_thru_field].values[0]
    values = [birdies, pars, bogeys]
    percentages = [birdies_pct, pars_pct, bogeys_pct]
    labels = ['Birdies', 'Pars', 'Bogeys']
    customdata = [f'{birdies}<br>({birdies_pct:.1%})', f'{pars}<br>({pars_pct:.1%})', f'{bogeys}<br>({bogeys_pct:.1%})']
    fig = px.pie(
        values=percentages, 
        names=labels, 
        title=f'Stats for Hole {hole_num}', 
        hole=0.4
    )
    fig.update_traces(
        textposition='inside',
        textinfo='label+percent',
        customdata=customdata,
        hovertemplate='%{label}<br>%{customdata}',
        texttemplate='%{label}<br>%{customdata}',
        marker=dict(colors=[COLORS["primary"], COLORS["quaternary"], COLORS["secondary"]])
    )
    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center', 'font': dict(size=24, family='Roboto')},
        font=dict(family='Roboto'),
        showlegend=False
    )
    return fig