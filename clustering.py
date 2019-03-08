from graph_functions import  split_dataset, cluster_equity_chart
from running_r import runningR
from single_cluster_graph import single_cluster_graph

import json
import base64
import io
import os
import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets = external_stylesheets)

userhome = os.path.expanduser('~')
desktop = userhome + r'\Desktop'

# layout of the app
app.layout = html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
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
            # Allow multiple files to be uploaded
            multiple=False
         ), dcc.Input(
                 id='ratio-in',
                 value="Ratio of the out-in-sample split",
                 style={'fontSize':14, 'display':'block',
                        'margin-left':'auto', 'margin-right':'auto', 'textAlign': 'center',
                        'margin-top': 15, 'width': '25%', 'font-family': "Open Sans"}
             ),
             dcc.Input(
                 id='number-of-clusters',
                 value="Number of clusters to be made",
                 style={'fontSize':14, 'display':'block',
                 'margin-left':'auto', 'margin-right':'auto', 'textAlign': 'center',
                 'margin-top': 15, 'width': '25%', 'font-family': "Open Sans"}
             ),html.Div([
             html.Button(
                 id='submit-button',
                 n_clicks=0,
                 children='Submit',
            )], style= {'textAlign':'center', 'margin-top':15}
),          html.Div(id='intermediate-value', style={'display': 'none'}),
            dcc.Graph(id='multi-graph', style={'height': 600}),
            dcc.Graph(id='single-graph', style={'height': 600})
])

# file upload function
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return None

    return df

# Callback to Upload the data and the parse the excel file
@app.callback(Output('intermediate-value', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(contents, filename):
    if contents is not None:
        df = parse_contents(contents, filename)
        return df.to_json(orient='split')

# Main clustering graph
@app.callback(Output('multi-graph', 'figure'),
             [Input('intermediate-value', 'children')])
def update_multi_graph(jsonified_data):

    df = pd.read_json(jsonified_data, orient='split')
    runningR(df)
    traces = cluster_equity_chart(df)

    return {'data': traces,
            'layout': go.Layout(title='Equity Curves of clusters',
                                    xaxis={'title': 'Periods'},
                                    yaxis={'title': 'Cumulative Equity'})}

# Single clustering graph
@app.callback(Output('single-graph', 'figure'),
             [Input('intermediate-value', 'children')])
def update_single_graph(jsonified_data):

    df = pd.read_json(jsonified_data, orient='split')
    traces = single_cluster_graph(df)

    return {'data': traces,
            'layout': go.Layout(title='Overview of the cluster',
                                    xaxis={'title': 'Periods'},
                                    yaxis={'title': 'Cumulative Equity'})}

if __name__ == '__main__':
    app.run_server(debug=True)
