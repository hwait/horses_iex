from datetime import datetime
from flask import Flask
import pandas as pd
import numpy as np
from flask import Response

app = Flask(__name__)


@app.route('/')
def get_main():
    return {}


@app.route('/races/<d>')
def get_races(d):
    try:
        ds = datetime.strptime(d, '%Y-%m-%d')
        df = pd.read_csv('data/races/races_{}.csv'.format(d))
        df['marketTime'] = pd.to_datetime(df['marketTime'])
        df['countryCode'] = df['course'].apply(
            lambda x: x.split('(')[-1].replace(')', ''))
        df['countryCode'] = np.where(
            df['countryCode'].str.len() > 4, 'GBR', df['countryCode'])
        dic = {'AW': 'GBR', 'Ayr': 'GBR'}
        df['countryCode'] = df['countryCode'].replace(dic)
        resp = Response(df[['rid', 'course', 'time', 'marketTime', 'title', 'runners', 'rclass',
                            'ages', 'distance', 'condition']].to_json(orient='records'), mimetype='application/json')
    except:
        resp = {}
    return resp


@app.route('/races/<d>/<rid>')
def get_horses(d, rid):
    try:
        ds = datetime.strptime(d, '%Y-%m-%d')
        df = pd.read_csv('data/horses/horses_{}.csv'.format(d))
        df['weight'] = (df['weightSt']*6.35+df['weightLb']*0.454).astype(int)
        df['runners'] = df.groupby(['rid'])['horseName'].transform('count')
        df.loc[df['position'] == 1, 'res_win'] = 1
        df.loc[df['position'] != 1, 'res_win'] = 0
        df['res_place'] = 0
        df.loc[(df['position'] == 1), 'res_place'] = 1
        df.loc[(df['position'] == 2) & (df['runners'] >= 5),
               'res_place'] = 1  # 5,6,7 runners
        df.loc[(df['position'] == 3) & (df['runners'] >= 8),
               'res_place'] = 1  # 8 to 15
        df.loc[(df['position'] == 4) & (
            df['runners'] >= 16), 'res_place'] = 1  # 16+
        cols = ['rid', 'mid', 'rid_win', 'horseName', 'age', 'decimalPrice', 'trainerName', 'jockeyName', 'dist', 'weight', 'RPR', 'TR',
                'OR', 'father', 'mother', 'gfather', 'position', 'res_win', 'res_place', 'win_mean', 'win_high', 'win_low', 'win_open', 'win_close']
        df = df.loc[df['rid'] == int(rid)][cols]
        df.rename(columns={"rid_win": "key"}, inplace=True)
        resp = Response(df.to_json(orient='records'),
                        mimetype='application/json')
    except:
        resp = {}
    return resp


@app.route('/bf/<d>/<mid>')
def get_changes(d, mid):
    try:
        mid = int(mid)
        dfh = pd.read_csv('data/horses/horses_{}.csv'.format(d))
        dfh = dfh.loc[dfh['mid'] == mid]
        dfr = pd.read_csv('data/races/races_{}.csv'.format(d))
        dfr['marketTime'] = pd.to_datetime(dfr['marketTime'])
        de = dfr.loc[dfr['mid'] == mid, 'marketTime'].values[0]
        dfp = pd.read_csv('data/bf/changes_{}.csv'.format(d))
        dfp['dt'] = pd.to_datetime(dfp['dt'])
        dfp = dfp.loc[(dfp['mid'] == mid) & (dfp['dt'] < de)]
        dfp.rename(columns={'price': 'p_'}, inplace=True)
        cols = ['dt', 'p_', 'rid']
        df = pd.DataFrame()
        for row in dfh.itertuples():
            dft = dfp.loc[dfp['rid'] == row.rid_win][cols]
            dft['mean'] = dft.groupby(['rid'])['p_'].transform('mean')
            dft['d_'] = (dft['p_']-dft['mean'])/dft['mean']
            dft['p_'] = 1/dft['p_']
            if df.empty:
                df = dft
                df.rename(columns={'p_': f'p_{row.rid_win}',
                                   'd_': f'd_{row.rid_win}'}, inplace=True)
            else:
                df = df.merge(dft, on='dt', how='outer')
                df.rename(columns={'p_': f'p_{row.rid_win}',
                                   'd_': f'd_{row.rid_win}'}, inplace=True)
            df.drop(columns=['mean', 'rid'], inplace=True)
        df.fillna(method='ffill', inplace=True)
        df.sort_values(by='dt', inplace=True)
        resp = Response(df.to_json(orient='records'),
                        mimetype='application/json')
    except:
        resp = {}
    return resp
