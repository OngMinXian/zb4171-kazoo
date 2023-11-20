from dash import dash, Dash, html, dcc, callback, Output, Input, State, callback_context, ALL, MATCH, dash_table, no_update
import dash_bootstrap_components as dbc

theme = dbc.themes.BOOTSTRAP
icon_lib = dbc.icons.FONT_AWESOME
bs_icon_lib = dbc.icons.BOOTSTRAP

app = Dash(
    name=__name__,
    external_stylesheets=[theme, icon_lib, bs_icon_lib],
    use_pages=True,
    suppress_callback_exceptions=True,
)

app.layout = dbc.Container(fluid=True, children=[

    # Navigation bar
    dbc.Row([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink('Home', href='/')),
                dbc.NavItem(dbc.NavLink('Patient Metadata', href='patient')),
                dbc.NavItem(dbc.NavLink('MultiQC Results', href='multiqc')),
                dbc.NavItem(dbc.NavLink('DESeq2 Results', href='deseq')),
                dbc.NavItem(dbc.NavLink('Machine Learning Model', href='ml')),
            ],
            brand='ZB4171: Team Kazoo',
            color='primary',
            dark=True,
            fluid=True,
        ),
    ]),

    # Page content
    dbc.Row([
        dash.page_container,
    ]),
    
])

# Run the app
if __name__ == '__main__':
    app.run()

"""
To do: 
    - Static GO analysis and ML metric plots
    - (Maybe) Button to empty cache, to allow data refresh
    - (Maybe) Upload fastq file feature using presigned url
"""
