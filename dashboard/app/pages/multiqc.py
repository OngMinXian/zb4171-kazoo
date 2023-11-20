import dash
from dash import Dash, html, dcc, callback, Output, Input, State, callback_context, ALL, MATCH, dash_table, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.express as px

from get_multiqc_data import *

dash.register_page(__name__)

initial_cols = ['Sample ID', 'reads_mapped', 'reads_unmapped', 'reads_duplicated', 'median_sequence_length']

layout = dbc.Container(
    fluid=True,
    children=[

        dbc.Row([
            # Page label
            dbc.Row([
                dbc.Label(
                    'Select metrics to display:',
                    style={'font-weight': '500', 'font-size': '120%'},
                ),
            ]),

            # Multi select columns on datatable
            dbc.Row([
                dmc.MultiSelect(
                    id='select_cols',
                    data=get_multiqc_data().columns,
                    value=initial_cols,
                    clearable=True,
                    searchable=True,
                    nothingFound='No metric found',
                ),
            ]),
        ], class_name='card'),

        dbc.Row([
            # Datatable
            dbc.Row([
                dash_table.DataTable(
                    data=get_multiqc_data().to_dict('records'),
                    columns=[
                        {'name': col, 'id': col, 'selectable': True}
                        for col in initial_cols
                    ],
                    id='dt_multiqc',
                    sort_action='native',
                    filter_action='native',
                    page_action="native",
                    page_current= 0,
                    page_size=20,
                    column_selectable='single',
                    selected_columns=[],
                    style_table={'overflowX': 'scroll'},
                    style_cell={
                        'textAlign': 'center',
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'font-family':'sans-serif',
                        'lineHeight': '1.5',
                        'border': '1px solid #dee2e6',
                        'verticalAlign': 'top'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f2f2f2',
                        }
                    ],
                ),
            ]),

            # Plot metric
            dbc.Row(
                id='metric',
                children=[
                    dbc.Label(
                        'Select metric to plot', 
                        id='metric', 
                        style={'font-weight': '500', 'font-size': '120%', 'margin-top': '2%'},
                    ),
                ],
            ),
        ], class_name='card'),
    ],
)

@callback(
    Output('dt_multiqc', 'columns'),
    Input('select_cols', 'value')
)
def update_datatable_columns(val):
    output = []
    for col in val:
        output.append({'name': col, 'id': col, 'selectable': True})
    return output

@callback(
    Output('metric', 'children'),
    Input('dt_multiqc', 'selected_columns'),
    prevent_initial_call=True,
)
def update_metric(cols):
    if cols == None:
        return no_update
    else:
        metric = cols[0]
        try:
            fig = px.histogram(get_multiqc_data(), x=metric, nbins=len(get_multiqc_data()))
            fig = dcc.Graph(figure=fig)
        except:
            try:
                fig = px.pie(get_multiqc_data(), names=metric)
                fig = dcc.Graph(figure=fig)
            except:
                fig = dbc.Label('Cannot plot metric', style={'font-weight': '500', 'font-size': '120%'})

        return [
            dbc.Label(metric, style={'font-weight': '500', 'font-size': '120%'}),
            fig,
        ]
