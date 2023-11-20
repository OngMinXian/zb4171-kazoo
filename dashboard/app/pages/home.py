import dash
from dash import Dash, html, dcc, callback, Output, Input, State, callback_context, ALL, MATCH, dash_table, no_update
import dash_bootstrap_components as dbc

import base64
import io
import pandas as pd 

dash.register_page(__name__, path='/')

layout = dbc.Container(fluid=True, children=[

    # Application description
    dbc.Row([
        dbc.Container(
            fluid=True,
            children=[
                dbc.Label('Lorem Ipsum', style={'font-weight': 'bold', 'font-size': '200%'}),
                html.P(
                    '''
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent accumsan leo vel orci malesuada luctus. Nunc elementum felis consectetur venenatis viverra. Praesent porttitor et tellus pretium vehicula. Duis a lacinia lacus, euismod posuere eros. Nunc sollicitudin magna felis, dignissim efficitur arcu mattis eu. Proin at urna pulvinar, vestibulum sapien a, congue diam. Curabitur molestie feugiat sapien, eget ultrices libero accumsan eget. Cras sed porta enim, eu volutpat nunc. Curabitur vel arcu at erat bibendum imperdiet. Duis eleifend tortor id quam lobortis, non egestas sapien eleifend. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                    Praesent vulputate nunc at aliquam accumsan. Nam varius risus sed commodo tempor. Sed lorem neque, sagittis a turpis a, mattis pretium magna. Suspendisse eu nisl sapien. Praesent laoreet, augue ac commodo vulputate, risus nibh sagittis lectus, sed cursus lorem quam eu libero. Suspendisse ac arcu eu tellus vehicula condimentum. Praesent bibendum libero quis mauris tincidunt semper.
                    Donec ultrices lectus erat, a interdum ipsum ornare eu. Nullam id mattis ante. Duis vel magna purus. Morbi mollis mauris ut blandit faucibus. Nunc dolor erat, suscipit vitae augue et, placerat varius enim. Vestibulum non imperdiet quam. In sodales rhoncus metus nec luctus. In pellentesque vulputate nisl, molestie faucibus elit accumsan quis. Cras varius euismod maximus. Integer feugiat tempor augue vitae interdum. Nunc porta lacinia metus in vehicula. Sed sit amet convallis elit. Etiam rhoncus dolor dolor, vitae lobortis magna fermentum et. Curabitur tempus tellus neque, eu fermentum tortor rhoncus nec. Donec congue et nisl vel maximus. In fringilla fringilla augue, sollicitudin luctus risus molestie vel.
                    ''',
                )
            ],
            class_name='card',
        ),
    ], style={'padding': '2vh 5vw'}),

    # Upload samplesheet and provide email
    dbc.Row([
        dbc.Container(
            fluid=True,
            children=[
                dbc.Row([
                    dbc.Col([
                        # Upload samplesheet
                        dcc.Upload(
                            id='upload_samplesheet',
                            children=html.Div([
                                'Drag or select samplesheet to upload',
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
                                id='samplesheet_filename', 
                                style={'text-align': 'center', 'font-weight': '500', 'font-size': '135%'}
                            ),
                            justify='center',
                        ),
                    ], width=7),
                    dbc.Col([
                        dbc.Row([
                            # Email input
                            dbc.Input(
                                id='input_email',
                                placeholder='Enter your email',
                            ),
                        ], style={'padding': '2vh 2vw'}),
                        dbc.Row([
                            # Button to submit
                            dbc.Button(
                                'Upload samplesheet',
                                id='button_samplesheet',
                                n_clicks=0,
                                style={'width': '200px'},
                            ),
                        ], justify='center'),
                        dbc.Row([
                            # Alert for success or failure to upload
                            dbc.Alert(
                                'Samplesheet succesfully uploaded',
                                color='success',
                                id='alert_samplesheet_success',
                                is_open=False,
                                duration=4000,
                                style={'width': '500px'},
                            ),
                            dbc.Alert(
                                'Samplesheet failed to upload',
                                color='danger',
                                id='alert_samplesheet_fail',
                                is_open=False,
                                duration=4000,
                                style={'width': '500px'},
                            ),
                        ], justify='center', style={'padding': '2vh 2vw'}),
                    ], width=5),
                ]),
            ],
            class_name='card',
        )
    ], style={'padding': '3vh 6vw'}),

])

@callback(
    Output('alert_samplesheet_success', 'is_open'),
    Output('alert_samplesheet_fail', 'is_open'),
    Input('button_samplesheet', 'n_clicks'),
    State('input_email', 'value'),
    State('upload_samplesheet', 'contents'),
    State('upload_samplesheet', 'filename'),
    prevent_initial_call=True,
)
def upload_samplesheet(n_clicks, email, contents, filename):
    # Samplesheet uploaded succesfully
    try:
        # Read CSV file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            df['Email'] = email
            df.to_csv('s3://zb4171/kazoo/samplesheets/samplesheet.csv', index=False)
            return True, False

        else:
            return False, True
    
    # Samplesheet upload fail
    except:
        return False, True

@callback(
    Output('samplesheet_filename', 'children'),
    Input('upload_samplesheet', 'filename'),
)
def update_filename(filename):
    if filename == None:
        return no_update
    return dbc.Label(filename, style={})
