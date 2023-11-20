import dash
from dash import Dash, html, dcc, callback, Output, Input, State, callback_context, ALL, MATCH, dash_table, no_update
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

import numpy as np

from get_deseq_data import *

dash.register_page(__name__)

layout = dbc.Container([
    dbc.Row([
        
        # Settings
        dbc.Col([
            
            # Experiment
            dbc.Row([
                dbc.Select(
                    id='experiment_type',
                    options=[
                        {'label': 'All cancer types', 'value': 'combined'},
                        {'label': 'breast', 'value': 'breast'},
                        {'label': 'colon', 'value': 'colon'},
                        {'label': 'female reproductive', 'value': 'female reproductive'},
                        {'label': 'pancreas', 'value': 'pancreas'},
                        {'label': 'skin', 'value': 'skin'},
                    ],
                    value='',
                    placeholder='Select experiment',
                ),
            ], style={'margin': '5%'}),

            # p-value
            dbc.Row([
                dbc.Label('Significance level for false discovery rate:', style={'font-weight': '500', 'font-size': '120%'}),
                dbc.Input(
                    type='number',
                    id='p_value',
                    value='0.05',
                    placeholder='Enter a float',
                ),
            ], style={'margin': '5%'}),

            # Minimum log2 fold change
            dbc.Row([
                dbc.Label('Minimum log2 fold change:', style={'font-weight': '500', 'font-size': '120%'}),
                dbc.Input(
                    type='number',
                    id='log2foldchange',
                    value='1',
                    placeholder='Enter a float',
                ),
            ], style={'margin': '5%'}),

        ], width=2, class_name='sidebar', style={'height': '400px'}),

        # Plots
        dbc.Col(
            children=[

                dbc.Row([

                    dbc.Col([
                        # MA plot
                        dbc.Container([
                            dbc.Label(
                                'MA plot', 
                                style={'font-weight': 'bold', 'font-size': '150%', 'margin-left': '3%', 'margin-top': '3%'}
                            ),
                            dcc.Graph(
                                id='ma_plot',
                                figure=go.Figure(),
                                style={'width': '97%'},
                            ),
                        ], class_name='card', fluid=True),
                    ], width=6),

                    dbc.Col([
                        # Volcano plot
                        dbc.Container([
                            dbc.Label(
                                'Volcano plot', 
                                style={'font-weight': 'bold', 'font-size': '150%', 'margin-left': '3%', 'margin-top': '3%'}
                            ),
                            dcc.Graph(
                                id='volcano_plot',
                                figure=go.Figure(),
                                style={'width': '97%'},
                            ),
                        ], class_name='card', fluid=True),
                    ], width=6),

                ]),
                
                dbc.Row([
                    dbc.Container(
                        dbc.Tabs([
                            # Up regulated genes dt
                            dbc.Tab(
                                label='Up-regulated genes',
                                children=[
                                    dash_table.DataTable(
                                        id='dt_up_genes',
                                        columns=[
                                            {'name': col, 'id': col, 'selectable': True}
                                            for col in ['HGNC symbol', 'baseMean', 'log2FoldChange', 'padj']
                                        ],
                                        sort_action='native',
                                        filter_action='native',
                                        page_action="native",
                                        page_current= 0,
                                        page_size=15,
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
                                ],
                            ),
                            # Down regulated genes dt
                            dbc.Tab(
                                label='Down-regulated genes',
                                children=[
                                    dash_table.DataTable(
                                        id='dt_down_genes',
                                        columns=[
                                            {'name': col, 'id': col, 'selectable': True}
                                            for col in ['HGNC symbol', 'baseMean', 'log2FoldChange', 'padj']
                                        ],
                                        sort_action='native',
                                        filter_action='native',
                                        page_action="native",
                                        page_current= 0,
                                        page_size=15,
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
                                ],
                            ),
                        ]),
                        fluid=True,
                        class_name='card',
                    ),
                ], style={'padding': '5vh 5vw'}),

                # GO analysis plot
                dbc.Row(
                    dbc.Container([
                        dbc.Label('GO enrichment analysis', style={'font-weight': 'bold', 'font-size': '150%', 'margin-left': '3%', 'margin-top': '3%'}),
                    ], id='go_analysis_container', class_name='card'),
                ),

            ], 
            width=9,
            id='plot_container',
            style={'display': 'none'},
        ),

    ])
], fluid=True)

@callback(
    Output('plot_container', 'style'),
    Input('plot_container', 'style'),
    Input('experiment_type', 'value'),
)
def display_plot(style, val):
    if val == '':
        style['display'] = 'none'
    else:
        style['display'] = 'block'
    return style

@callback(
    Output('ma_plot', 'figure'),
    Output('volcano_plot', 'figure'),
    Output('dt_up_genes', 'data'),
    Output('dt_down_genes', 'data'),

    Input('experiment_type', 'value'),
    Input('p_value', 'value'),
    Input('log2foldchange', 'value'),

    prevent_initial_call=True,

)
def update_plots(exp, p_val, log2):
    # Retrieve DESeq2 results
    df = get_deseq_result(exp)
    p_val = float(p_val)
    log2 = float(log2)

    # Determine significant genes
    df['effect'] = 'Not sig.'
    df.loc[(df['padj'] < p_val) & (df['log2FoldChange'] < -log2), 'effect'] = 'Down'
    df.loc[(df['padj'] < p_val) & (df['log2FoldChange'] > log2), 'effect'] = 'Up'

    # Generate MA plot
    ma_plot = px.scatter(df, x='baseMean', y='log2FoldChange', color='effect', log_x=True)

    # Generate volcano plot
    df['-log10(padj)'] = -np.log10(df['padj'])
    volcano_plot = px.scatter(df, x='log2FoldChange', y='-log10(padj)', color='effect')
    volcano_plot.add_vline(x=log2, line_dash='dash', line_color='black')
    volcano_plot.add_vline(x=-log2, line_dash='dash', line_color='black')
    df = df.drop(columns=['-log10(padj)'])

    # Filter df by p_val and log2foldchange
    df = df[df['padj'] < p_val]
    df = df[df['log2FoldChange'].abs() > log2]

    # Split df by up and down regulated genes
    df_up = df[df['effect'] == 'Up'].drop(columns='effect').to_dict('records')
    df_down = df[df['effect'] == 'Down'].drop(columns='effect').to_dict('records')

    return ma_plot, volcano_plot, df_up, df_down

@callback(
    Output('go_analysis_container', 'children'),
    Input('experiment_type', 'value'),
    State('go_analysis_container', 'children'),
    prevent_initial_call=True,
)
def update_go_analysis(exp, children):
    if exp == None:
        return [dbc.Label('GO enrichment analysis', style={'font-weight': 'bold', 'font-size': '150%', 'margin-left': '3%', 'margin-top': '3%'})]
    else:
        image_path = f'assets/{exp}.png'
        return [
            dbc.Label('GO enrichment analysis', style={'font-weight': 'bold', 'font-size': '150%', 'margin-left': '3%', 'margin-top': '3%'}),
            html.Img(src=image_path)
        ]
