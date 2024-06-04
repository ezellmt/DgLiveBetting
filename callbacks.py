from dash import html, Input, Output, State
from utils import create_figure, create_pie_chart, create_column_defs
import dash_ag_grid as dag
import pandas as pd
import logging

def register_callbacks(app, holesdf, filtered_merged_df, live_stats_data, score_df, winner_3way_df):

    @app.callback(
        [Output('slider-round-1', 'value'),
         Output('slider-round-2', 'value'),
         Output('slider-round-3', 'value'),
         Output('slider-round-4', 'value'),
         Output('input-round-1', 'value'),
         Output('input-round-2', 'value'),
         Output('input-round-3', 'value'),
         Output('input-round-4', 'value')],
        [Input('slider-round-1', 'value'),
         Input('slider-round-2', 'value'),
         Input('slider-round-3', 'value'),
         Input('slider-round-4', 'value'),
         Input('input-round-1', 'value'),
         Input('input-round-2', 'value'),
         Input('input-round-3', 'value'),
         Input('input-round-4', 'value')],
        [State('lock-round-1', 'className'),
         State('lock-round-2', 'className'),
         State('lock-round-3', 'className'),
         State('lock-round-4', 'className')]
    )
    def update_sliders(slider1, slider2, slider3, slider4, input1, input2, input3, input4, lock1, lock2, lock3, lock4):
        sliders = [slider1, slider2, slider3, slider4]
        inputs = [input1, input2, input3, input4]
        locks = [lock1, lock2, lock3, lock4]

        for i in range(4):
            if locks[i] == 'fas fa-lock':
                sliders[i] = inputs[i]

        total = sum(sliders)
        if total == 100:
            return sliders + sliders

        remaining = 100 - total
        for i in range(4):
            if locks[i] == 'fas fa-lock-open':
                if remaining < 0:
                    if sliders[i] + remaining >= 0:
                        sliders[i] += remaining
                        remaining = 0
                    else:
                        remaining += sliders[i]
                        sliders[i] = 0
                else:
                    if sliders[i] + remaining <= 100:
                        sliders[i] += remaining
                        remaining = 0
                    else:
                        remaining -= (100 - sliders[i])
                        sliders[i] = 100

        return sliders + sliders

    @app.callback(
        Output('lock-round-1', 'className'),
        Output('lock-round-2', 'className'),
        Output('lock-round-3', 'className'),
        Output('lock-round-4', 'className'),
        [Input('lock-round-1', 'n_clicks'),
         Input('lock-round-2', 'n_clicks'),
         Input('lock-round-3', 'n_clicks'),
         Input('lock-round-4', 'n_clicks')],
        [State('lock-round-1', 'className'),
         State('lock-round-2', 'className'),
         State('lock-round-3', 'className'),
         State('lock-round-4', 'className')]
    )
    def toggle_lock(lock1_clicks, lock2_clicks, lock3_clicks, lock4_clicks, lock1, lock2, lock3, lock4):
        locks = [lock1, lock2, lock3, lock4]
        clicks = [lock1_clicks, lock2_clicks, lock3_clicks, lock4_clicks]

        for i in range(4):
            if clicks[i] is not None and clicks[i] % 2 == 1:
                locks[i] = 'fas fa-lock'
            else:
                locks[i] = 'fas fa-lock-open'

        return locks

    @app.callback(
        Output('live-stats-content', 'children'),
        [Input('stat-selector', 'value')]
    )
    def update_live_stats_content(active_tab):
        logging.info(f"update_live_stats_content callback triggered with active_tab: {active_tab}")
        if active_tab == 'event_avg':
            df = live_stats_data.get("event_avg", pd.DataFrame())
        else:
            round_num = active_tab.split('-')[-1]
            df = live_stats_data.get(round_num, pd.DataFrame())
        
        if df.empty:
            logging.warning(f"Data for {active_tab} not found in live_stats_data")
            return html.Div(f"Data for {active_tab} not found.")
        
        # Round numerical values to two decimal places
        df = df.round(2)
        columns = create_column_defs()

        return dag.AgGrid(
            id='live-stats-table',
            columnDefs=columns,
            rowData=df.to_dict('records'),
            defaultColDef={
                'sortable': True,
                'resizable': True,
                'flex': 1  # Ensure columns expand to fill the width
            },
            className="ag-theme-quartz",
            style={'height': 'calc(100vh - 100px)', 'width': '100%', 'fontFamily': 'Roboto'}
        )

    @app.callback(
        Output('hole-by-hole-chart', 'figure'),
        [Input('round-selector', 'value'), Input('wave-selector', 'value')]
    )
    def update_chart(round_num, wave):
        fig = create_figure(holesdf, round_num, wave)
        return fig

    @app.callback(
        [Output(f'hole-stats-chart-{i}', 'figure') for i in range(1, 19)],
        [Input('round-selector', 'value'), Input('wave-selector', 'value')]
    )
    def update_stats_charts(round_num, wave):
        figures = [create_pie_chart(holesdf, round_num, wave, hole_num) for hole_num in range(1, 19)]
        return figures
