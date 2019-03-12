import pandas as pd
import subprocess
import os
import plotly.graph_objs as go

userhome = os.path.expanduser('~')
desktop = userhome + r'\Desktop'

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

    # Strategy drawdown options formation
    list_strategies = [df2[df2['Cluster'] == i].index for i in range(1, 6)]
    option_list = []

    for item in list_strategies:
        dict_st = []
        for index, value in enumerate(item):
            dict_st.append({'label': value, 'value': index})
        option_list.append(dict_st)

    return traces, option_list
