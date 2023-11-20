import dash
from dash import Dash, html, dcc, callback, Output, Input, State, callback_context, ALL, MATCH, dash_table, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import plotly.express as px

from get_sample_metadata import *

dash.register_page(__name__)

only_use_analyzed_data = True
initial_cols = [
    'Patient ID', 'Gender', 'CTEP SDCDescription',
    'Disease BodyLocation', 'Age atDiagnosis', 'Race',
    'Date ofDiagnosis', 'PatientNotes'
]


layout = dbc.Container(
    fluid=True,
    children=[
        # Patient metadata
        dbc.Row([

            dbc.Tabs([
                # Summary plots
                dbc.Tab(
                    label='Summary',
                    children=[

                        dbc.Row([
                            dbc.Col([
                                # Total samples
                                dbc.Container(
                                    fluid=True,
                                    children=[
                                        dbc.Row(
                                            dbc.Label(
                                                'Total samples analyzed', 
                                                style={
                                                    'font-size': '250%',
                                                    'text-align': 'center',
                                                    'width': '85%',
                                                },
                                            ),
                                        ),
                                        dbc.Row(
                                            dbc.Label(
                                                len(get_sample_metadata(only_use_analyzed_data)), 
                                                style={
                                                    'font-weight': 'bold', 
                                                    'font-size': '800%',
                                                    'text-align': 'center',
                                                    'color': '#2543cc',
                                                },
                                            ),
                                        ),
                                    ],
                                    class_name='card',
                                ),
                            ], align='center'),
                            dbc.Col([
                                # Gender pie chart
                                dbc.Container(
                                    fluid=True,
                                    children=[
                                        dbc.Label('Gender'),
                                        dcc.Graph(
                                            figure=px.pie(
                                                get_sample_metadata(only_use_analyzed_data),
                                                names='Gender',
                                            ),
                                        ),
                                    ],
                                    class_name='card',
                                ),
                            ]),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                # CTEP SDCDescription pie chart
                                dbc.Container(
                                    fluid=True,
                                    children=[
                                        dbc.Label('CTEP SDCDescription'),
                                        dcc.Graph(
                                            figure=px.pie(
                                                get_sample_metadata(only_use_analyzed_data),
                                                names='CTEP SDCDescription',
                                            ),
                                        ),
                                    ],
                                    class_name='card',
                                ),
                            ]),
                            dbc.Col([
                                # Disease body location pie chart
                                dbc.Container(
                                    fluid=True,
                                    children=[
                                        dbc.Label('Disease location'),
                                        dcc.Graph(
                                            figure=px.pie(
                                                get_sample_metadata(only_use_analyzed_data),
                                                names='Disease BodyLocation',
                                            ),
                                        ),
                                    ],
                                    class_name='card',
                                ),
                            ]),
                        ]),

                        dbc.Row([
                            # Age histogram
                            dbc.Container(
                                fluid=True,
                                children=[
                                    dbc.Label('Age'),
                                    dcc.Graph(
                                        figure=px.histogram(
                                            get_sample_metadata(only_use_analyzed_data),
                                            x='Age atDiagnosis',
                                        ),
                                    ),
                                ],
                                class_name='card',
                            ),
                        ]),

                    ],
                ),

                # Clinical data
                dbc.Tab(
                    label='Clinical data',
                    children=[

                        # Select columns menu
                        dbc.Row([
                            dmc.Menu(children=[
                                dmc.MenuTarget(
                                    dmc.Tooltip(children=[
                                        dmc.ActionIcon(
                                            DashIconify(icon='fluent:column-triple-edit-20-regular', width=20),
                                            variant='outline',
                                            size='lg', 
                                            color='#0d6efd', 
                                            mb=5)
                                    ], label="Show/Hide column", position="bottom", zIndex=1000)),

                                dmc.MenuDropdown(
                                    [dmc.MenuLabel("Show/Hide Columns")] +
                                    [
                                        dmc.MenuItem(
                                            dmc.Switch(
                                                label=col, 
                                                id={'type': 'select_col', 'value': col}, 
                                                checked=True if col in initial_cols else False,
                                                color='#0d6efd'
                                            )
                                        )
                                        for col in get_sample_metadata(only_use_analyzed_data).columns
                                    ]
                                )
                            ], zIndex=1000, closeOnItemClick=False),
                        ], justify='end', style={'margin': '2vh 0vw'}),
                        
                        # Datatable
                        dash_table.DataTable(
                            data=get_sample_metadata(only_use_analyzed_data).to_dict('records'),
                            columns=[
                                {'name': col, 'id': col}
                                for col in initial_cols
                            ],
                            id='dt_patient',
                            sort_action='native',
                            filter_action='native',
                            page_action="native",
                            page_current= 0,
                            page_size=20,
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
                        )

                    ],
                ),

            ]),

        ], style={'padding': '2vh 2vw'}),
        
    ]
)

@callback(
    Output('dt_patient', 'columns'),
    Input({'type': 'select_col', 'value': ALL}, 'checked')
)
def update_datatable_columns(checked):
    output = []
    for i, col in enumerate(get_sample_metadata(only_use_analyzed_data).columns):
        if checked[i]:
            output.append({'name': col, 'id': col})
    return output
