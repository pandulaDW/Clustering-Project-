from graph_functions import cluster_equity_chart
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

# Options for the dropdowns
cluster_options = [{'label': 'Cluster {}'.format(i), 'value': i} for i in range(1, 6)]

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
         ), html.Div(id='intermediate-value', style={'display': 'none'}),
            dcc.Graph(id='multi-graph', style={'height': 600, 'margin-bottom':'4%'}),
            html.Div([
                     html.Div([dcc.Dropdown(id='cluster_picker', value=1, options=cluster_options)],
                               style= {'width':'15%', 'float':'left', 'display':'inline-block', 'margin-right':'1%'}),
                     html.Div([dcc.Input(id='max_dw', type='number',  placeholder='Enter a preferred Drawdown', value=None)],
                               style= {'width':'30%', 'float':'left', 'display':'inline-block'}),
                     html.Div([html.Button(id='submit-button', n_clicks=0, children='Submit')],
                              style= {'display':'inline-block'}),
                     html.Div([dcc.Dropdown(id='drawdown_output', value=None, placeholder='Maximum drawdowns')],
                              style= {'width':'15%', 'display':'inline-block', 'float':'right'}),
                     html.Div([dcc.Dropdown(id='strategy_output', value=None, placeholder='Strategies in the cluster')],
                              style= {'width':'15%', 'display':'inline-block', 'float':'right', 'padding-right': '1%'})]),
                     dcc.Graph(id='single-graph', style={'height': 600}),
                     html.Div([dcc.Slider(id='slider-id', min=1, max=5, marks={i: 'Label {}'.format(i) for i in range(1, 6)},value=1)],
                               style={'width':'50%', 'margin-left':'auto', 'margin-right':'auto'}),
                     html.Div(id='intermediate-value-2', style={'display': 'none'})
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

# Slider functionality
@app.callback(Output('intermediate-value-2', 'children'),
              [Input('intermediate-value', 'children'),
              Input('slider-id', 'value')])
def slider_update(jsonified_data, slider_value):

    df = pd.read_json(jsonified_data, orient='split')
    df_list = []
    i = 0
    slider_items = int(np.floor(len(df)/5))

    for item in range(5):
        j = i + slider_items
        df_2 = df[i: j]
        i = j
        df_list.append(df_2)

    new_df = pd.concat(df_list[slider_value-1:], axis=0)
    return new_df.to_json(orient='split')

# Main clustering graph
@app.callback(Output('multi-graph', 'figure'),
             [Input('intermediate-value', 'children')])
def update_multi_graph(jsonified_data):

    df = pd.read_json(jsonified_data, orient='split')
    runningR(df)
    traces, strategy_options = cluster_equity_chart(df)

    return {'data': traces,
            'layout': go.Layout(title='Equity Curves of clusters',
                                    xaxis={'title': 'Periods'},
                                    yaxis={'title': 'Cumulative Equity'})}

# Single clustering graph
@app.callback(Output('single-graph', 'figure'),
             [Input('intermediate-value-2', 'children'),
              Input('cluster_picker', 'value'),
              Input('submit-button', 'n_clicks')],
             [State('max_dw', 'value')])
def update_single_graph(jsonified_data, cluster_pick, n_clicks, max_dw):

    if max_dw is None:
        max_dw = 100000

    df = pd.read_json(jsonified_data, orient='split')
    traces, drawdown_options = single_cluster_graph(df, n=cluster_pick, max_dw=max_dw)

    return {'data': traces,
            'layout': go.Layout(title='Overview of the cluster',
                                    xaxis={'title': 'Periods'},
                                    yaxis={'title': 'Cumulative Equity'},
                                    showlegend=True)}

# Drawdown dropdown update
@app.callback(Output('drawdown_output', 'options'),
             [Input('intermediate-value-2', 'children')])
def update_drawdowns(jsonified_data):

    df = pd.read_json(jsonified_data, orient='split')
    traces, drawdown_options = single_cluster_graph(df)
    return drawdown_options

# Strategies dropdown update
@app.callback(Output('strategy_output', 'options'),
             [Input('intermediate-value', 'children'),
              Input('cluster_picker', 'value')])
def update_strategies(jsonified_data, cluster_pick):

    df = pd.read_json(jsonified_data, orient='split')
    traces, strategy_options = cluster_equity_chart(df)
    return strategy_options[cluster_pick-1]

if __name__ == '__main__':
    app.run_server(debug=True)
