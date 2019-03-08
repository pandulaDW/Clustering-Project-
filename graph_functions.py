import pandas as pd
import subprocess
import os
import plotly.graph_objs as go

userhome = os.path.expanduser('~')
desktop = userhome + r'\Desktop'

# Splitting the dataset
def split_dataset(df, split):
    n_rows = round(len(df) * split)
    in_sample = df.iloc[0:len(df)-n_rows,]
    out_sample = df.iloc[len(df)-n_rows:,]

# Cluster_equity_graph
def cluster_equity_chart(df, t_period = 100000):

    if t_period != 100000:
        df2 = df.loc[t_period:,:]
    else:
        df2 = df.copy()

    clusters = pd.read_csv('{}/final.csv'.format(desktop), encoding='latin-1')
    clusters.columns = ['Strategy', "Cluster"]
    df2.set_index(df.columns[0], inplace=True)
    df2 = df2.transpose()
    df2['Cluster'] = clusters['Cluster'].values
    col_order = [df2.columns[-1]] + list(df2.columns[0:len(df2.columns)-1])
    df2 = df2.reindex(columns=col_order)

    cluster_groups = df2.groupby('Cluster')
    MtoM = cluster_groups.sum()
    cumsum = cluster_groups.sum().cumsum(axis=1)

    traces = []

    for i in range(len(cumsum)):

        trace = go.Scatter(x = cumsum.columns, y = cumsum.iloc[i,:],
                           mode = 'lines', name='Cluster {}'.format(i+1))
        traces.append(trace)

    return traces
