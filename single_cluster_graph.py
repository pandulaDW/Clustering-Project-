import pandas as pd
import pandas as pd
import subprocess
import os
import plotly.graph_objs as go

userhome = os.path.expanduser('~')
desktop = userhome + r'\Desktop'

def single_cluster_graph(df, n=1, max_dw=100000):

    df2 = df.copy()
    clusters = pd.read_csv('{}/final.csv'.format(desktop), encoding='latin-1')
    clusters.columns = ['Strategy', "Cluster"]
    df2.set_index(df2.columns[0], inplace=True)
    df2 = df2.transpose()
    df2['Cluster'] = clusters['Cluster'].values

    cluster_groups = df2.groupby('Cluster')
    MtoM = cluster_groups.sum()
    cumsum = cluster_groups.sum().cumsum(axis=1)
    max_cumsum = cumsum.cummax(axis=1)
    DD = (max_cumsum - cumsum)*-1
    lower_band = max_cumsum.copy()
    max_drawdowns = DD.apply(func=min, axis=1)

    if max_dw == 100000:

        for j in range(len(max_drawdowns)):
            for i in range(len(lower_band.columns)):
                if lower_band.iloc[j, i] > 0:
                    lower_band.iloc[j, i] = lower_band.iloc[j, i] + max_drawdowns[j+1]
                else:
                    lower_band.iloc[j, i] = 0
    else:
        for i in range(len(lower_band.columns)):
            if lower_band.iloc[n-1, i] > 0:
                lower_band.iloc[n-1, i] = lower_band.iloc[n-1, i] + max_dw
            else:
                lower_band.iloc[n-1, i] = 0

    trace1 = go.Scatter(y=cumsum.loc[n], x=cumsum.columns, mode='lines', name='Ecurve')
    trace2 = go.Scatter(y=max_cumsum.loc[n], x=cumsum.columns, mode='lines', name='Ecurve_High')
    trace3 = go.Scatter(y=lower_band.loc[n], x=cumsum.columns, name='Stop_limit', line = dict(
                        color = ('rgb(205, 12, 24)'), width = 3, dash='dash'))
    trace4 = go.Scatter(y=DD.loc[n], x=cumsum.columns, mode=None, name='Drawdown', fill='tozeroy')
    trace5 = go.Bar(y=MtoM.loc[n], x=MtoM.columns, name='MtoM', marker=dict(color='rgb(158,202,225)',
                 line=dict(color='rgb(8,48,107)', width=1.5), opacity=0.6))

    drawdown_dict = [{'label': 'Cluster_{} -> ({})'.format(i+1, round(j)), 'value': i}
                      for i, j in enumerate(max_drawdowns)]

    data = [trace1, trace2, trace3, trace4, trace5]

    return data, drawdown_dict
