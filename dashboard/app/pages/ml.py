import dash
from dash import Dash, html, dcc, callback, Output, Input, State, callback_context, ALL, MATCH, dash_table, no_update
import dash_bootstrap_components as dbc

import base64
import io
import pandas as pd

from get_sample_ids import *
from ml_model import *

dash.register_page(__name__)

layout = dbc.Container([

    dbc.Row([
        dbc.Container(
            children=[
                dbc.Row([
                    dbc.Col(
                        dbc.Tabs([
                            # Select sample from S3
                            dbc.Tab(
                                dbc.Select(
                                    id='select_sample',
                                    options=[
                                        {'label': sample, 'value': sample}
                                        for sample in get_sample_ids()
                                    ],
                                ),
                                label='Select analyzed sample',
                            ),

                            # Upload own tsv file
                            dbc.Tab([
                                dcc.Upload(
                                    id='upload_tsv',
                                    children=html.Div([
                                        'Drag or select tsv to upload',
                                    ]),
                                    style={
                                        'width': '100%',
                                        'height': '60px',
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px'
                                    },
                                ),
                                dbc.Row(
                                    dbc.Label(
                                        children=[], 
                                        id='tsv_filename', 
                                        style={'text-align': 'center', 'font-weight': '500', 'font-size': '135%'}
                                    ),
                                    justify='center',
                                ),
                            ], label='Upload own TSV file'),
                        ], id='tab_tsv'),
                        width=5,
                    ),

                    # Predict
                    dbc.Col([
                        dbc.Row(
                            dbc.Button('Predict', id='button_predict', n_clicks=0, style={'width': '200px'}),
                            justify='center',
                        ),
                        dbc.Row(
                            dbc.Label(id='prediction', style={'text-align': 'center', 'font-weight': '500', 'font-size': '165%'}),
                            style={'margin': '2%'},
                        ),
                    ], width=5),
                ], justify='center'),

            ],
            class_name='card',
            fluid=True,
        )
    ]),

    dbc.Row([
        # ML metric plots
        dbc.Container([

        ], class_name='card', fluid=True,)
    ]),
])

@callback(
    Output('tsv_filename', 'children'),
    Input('upload_tsv', 'filename'),
)
def update_filename(filename):
    if filename == None:
        return no_update
    return dbc.Label(filename, style={})

@callback(
    Output('prediction', 'children'),
    Input('button_predict', 'n_clicks'),
    State('tab_tsv', 'active_tab'),
    State('select_sample', 'value'),
    State('upload_tsv', 'contents'),
    State('upload_tsv', 'filename'),
    prevent_initial_call=True,
)
def make_prediction(n_clicks, active_tab, sample_id, contents, filename):
    if active_tab == 'tab-0':
        tsv = s3_client.get_object(Bucket='zb4171', Key=f'kazoo/results/{sample_id}/star_rsem/rsem.merged.gene_counts.tsv')['Body']
        df = pd.read_csv(tsv, sep='\t')[['gene_id', sample_id]]

    elif active_tab == 'tab-1':
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    if predict_cancer(df):
        return 'Prediction: Cancer'
    else:
        return 'Prediction: Not cancer'
