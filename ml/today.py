import numpy as np
import pandas as pd
from os import path, mkdir
import glob
from datetime import datetime, timedelta, date
from selenium import webdriver
from os import path, listdir
import shutil
import time
import re
import sys

def load_today():
    driver = webdriver.Chrome(executable_path=r'../../lib/chromedriver.exe')
    load_atr(driver)
    #load_atr(None)
    load_rp(driver)
    driver.close()

def load_atr(driver):
    fn = 'output/today/atr.html'
    driver.get('https://www.attheraces.com/racecards')
    time.sleep(5)
    html = driver.page_source
    #with open(fn, 'r', encoding='utf8') as f:
    #    html=f.read()
    parse_atr_day(html, driver)
    with open(fn, 'w+', encoding='utf8') as f:
        f.write(html)
    print('ATR: {} done with {} bytes.'.format(fn, len(html)))

def load_rp(driver):
    fn = 'output/today/rp.html'
    driver.get('https://www.racingpost.com/racecards/')
    time.sleep(5)
    html = driver.page_source
    parse_rp_day(html, driver)
    with open(fn, 'w+', encoding='utf8') as f:
        f.write(html)
    print('RP: {} done with {} bytes.'.format(fn, len(html)))

pRPLinks = re.compile(r'data-racecourse="[^"]+" href="([^"]+)">')
def parse_rp_day(html, driver):
    links = pRPLinks.findall(html)
    for link in links:
        fn = 'output/today/rp/{}.html'.format(link.split('/')[-1])
        load_link(f'https://www.racingpost.com{link}', fn, driver)


pATR_places = re.compile(r'<span class="h6 visible">([^<]+)')
pATR_races = re.compile(r'<span class="h7">([^<]+)')
pATR_split='<span class="h6 visible">'
pATR_Links = re.compile(r'<a href="([^"]+)"[^>]+>\s*<span class="h7">')
def parse_atr_day(html, driver):
    races=[]
    places=pATR_places.findall(html)
    parts=html.split(pATR_split)[1:]
    for i,part in enumerate(parts):
        if 'Abandoned' in part:
            continue
        place=places[i].strip()
        races = pATR_races.findall(part)
        links = pATR_Links.findall(part)
        for j,race in enumerate(races):
            ps=race.split(' - ')
            name=ps[-1].strip()
            tstr=ps[0].strip()
            tm=get_date(tstr)
            if 'Suspended' in name:# or (tm-timedelta(minutes=5))<datetime.now():
                continue
            link=links[j].strip()
            fn=f'output/today/atr/{name}_{tstr}.html'.replace(':','')
            load_link('https://www.attheraces.com'+link, fn, driver)
            print(tm, place, tstr, name, link)

def getone(pattern, string):
    m = pattern.search(string)
    res = m.group(1) if m else ''
    return res.strip()

def get_date(tstr):
    t = datetime.strptime('{:%Y-%m-%d} {}'.format(date.today(),tstr), '%Y-%m-%d %H:%M')
    return t+timedelta(hours=6)

def load_link(link, fn, driver):
    if not (path.exists(fn) and path.getsize(fn) > 10000):
        driver.get(link)
        time.sleep(10)
        html = driver.page_source
        with open(fn, 'w+', encoding='utf8') as f:
            f.write(html)
        print('{} done with {} bytes.'.format(fn, len(html)))

def parse_today():
    folder='output/today/atr/'
    files=listdir(folder)
    for fn in files:
        with open(folder+fn, 'r', encoding='utf8') as f:
            html = f.read()
            print('parse '+fn)
            parse_atr(html)
        fn_target=folder.replace('today','done')+'{:%Y-%m-%d}_'.format(date.today())+fn
        shutil.move(folder+fn, fn_target)
    folder='output/today/rp/'
    files=listdir(folder)
    for fn in files:
        with open(folder+fn, 'r', encoding='utf8') as f:
            html = f.read()
            print('parse '+fn)
            parse_rp(html)
        fn_target=folder.replace('today','done')+'{:%Y-%m-%d}_'.format(date.today())+fn
        shutil.move(folder+fn, fn_target)
    

patrCourse = re.compile(r'<title>([^<]+)')
patrDistance = re.compile(r'<div class="p--large font-weight--semibold">([^<]+)')
patrCondition = re.compile(r'<p class="p--medium">([^<]+)</p>')
patrOR = re.compile(r'<span class="text-pill text-pill--steel tooltip tooltipstered"[^>]+>([^<]+)')
patrHorseName = re.compile(r'<a href="/form/horse/[^>]+>([^<]+)')
patrOddsHorse = re.compile(r'class="odds-grid-horse__name a--plain js-popup-trigger" data-cookie="popupForm">([^<]+)')
patrOddsBookies = re.compile(r'<b class="bookmaker-logo__inner"[^>]+>([^<]+)')
patrOdds = re.compile(r'<span class="odds-value odds-value--decimal">([^<]+)')

def parse_atr(html):
    course=getone(patrCourse, html)
    ps=course.split(' | ')
    t=ps[0]
    course=ps[1]
    condition=getone(patrCondition, html).split('(')[0].replace('&nbsp;','')
    distance=getone(patrDistance, html)
    parts=html.split('<h2 class="h6 horse__details flush">')[1:]
    prices_count=html.count('<div class="odds-grid__cell odds-grid__cell--ew">')
    horses=[]
    for part in parts:
        if 'Non Runner' in part:
            continue
        horse=getone(patrHorseName, part)
        OR=getone(patrOR, part).replace('&nbsp;-&nbsp;','')
        horses.append([course, t, condition, distance, horse,OR])
    oddsHorses = patrOddsHorse.findall(html)
    oddsBookies = patrOddsBookies.findall(html)[:-1]
    oddsOdds=[]
    prices=patrOdds.findall(html)
    print(prices)
    for x in prices:
        oddsOdds.append(0 if x=='-' or x=='odds' or x=='SP' or x=='N/A' else float(x))
    rows=len(oddsHorses)
    o1=oddsOdds[:10*rows]
    o2=oddsOdds[10*rows:]
    try:
        hdf=pd.DataFrame(horses, columns=['course', 'marketTime', 'condition', 'distance', 'horseName','OR'])
        df=pd.DataFrame(np.hstack([np.reshape(oddsHorses,(rows,1)),np.reshape(o1,(rows,10)),np.reshape(o2,(rows,prices_count-10))]), columns=['horseName']+oddsBookies)
        df['decimalPrice']=df.loc[:, (df != "0.0").any(axis=0)].mode(axis=1).iloc[:,0]
        atr_odds.append(df)
        atrs.append(hdf.merge(df[['horseName','decimalPrice']], on='horseName', how='left'))
    except:
        print('error')
    #print(course, t, condition, distance)

#cols_base=['rid','course', 'marketTime', 'horseName', 'runners', 'ncond', 'metric', 'class', 'decimalPrice', 'age', 'isFav', 'RPR', 'TR', 'OR', 'weight']
pCourse = re.compile(r'<h1[^>]+>([^<]+)')
pDistance = re.compile(r'data-test-selector="RC-header__raceDistanceRound">([^<]+)')
pTime = re.compile(r'<span class="RC-courseHeader__time" data-test-selector="RC-courseHeader__time">([^<]+)')
pTitle = re.compile(r'<span data-test-selector="RC-header__raceInstanceTitle">([^<]+)')
pClass = re.compile(r'\s\((Class \d)\)\s')
pCondition = re.compile(r'Going.</div>\s+<div class="RC-headerBox__infoRow__content">([^<]+)')
pTrainer = re.compile(r'data-order-trainer="([^"]+)')
pJockey = re.compile(r'data-order-jockey="([^"]+)')
pRPR = re.compile(r'data-order-rpr="([^"]+)')
pTR = re.compile(r'data-order-ts="([^"]+)')
pOR = re.compile(r'data-order-or="([^"]+)')
pWeightSt = re.compile(r'<span class="RC-runnerWgt__carried_st">([^<]+)')
pWeightLb = re.compile(r'<span class="RC-runnerWgt__carried_lb">([^<]+)')
pAge = re.compile(r'data-order-age="([^"]+)')
pHorseName = re.compile(r'data-test-selector="RC-cardPage-runnerName">([^<]+)')

def parse_rp(html):
    course=getone(pCourse, html)
    distance=getone(pDistance, html)
    condition=getone(pCondition, html)
    rclass=getone(pClass, html)
    t=getone(pTime, html)
    title=getone(pTitle, html)
    parts=html.split('<div class="RC-runnerCardWrapper">')[1:]
    runners=len(parts)
    for part in parts:
        part=part.split('</tbody>')[0]
        horse=getone(pHorseName,part)
        trainer=getone(pTrainer,part)
        jockey=getone(pJockey,part)
        RPR=getone(pRPR,part)
        RPR='' if RPR=='-' else RPR
        TR=getone(pTR,part)
        TR='' if TR=='-' else TR
        OR=getone(pOR,part)
        OR='' if OR=='-' else OR
        weightSt=getone(pWeightSt,part)
        weightLb=getone(pWeightLb,part)
        age=getone(pAge,part)
        rps.append([course,runners,distance,condition,rclass,date.today(),title,horse,trainer,jockey,RPR,TR, weightSt,weightLb,age])
        #print(course,distance,t,date.today(),title,horse,trainer,jockey,RPR,TR, OR,weightSt,weightLb,age)

def parse_dt(x):
    h,m=map(int,x[0].split(':'))
    ds = x[1]
    hours_add=11 if (ds>=datetime(2019,3,31,0,0,0) and ds<datetime(2019,10,27,0,0,0)) or (ds>=datetime(2018,3,25,0,0,0) and ds<datetime(2018,10,28,0,0,0)) or (ds>=datetime(2017,3,26,0,0,0) and ds<datetime(2017,10,29,0,0,0)) or (ds>=datetime(2016,3,27,0,0,0) and ds<datetime(2016,10,30,0,0,0)) or ds<datetime(2015,10,25,0,0,0) else 12
    if h<9:
        h+=hours_add
    
    ds+= timedelta(hours=h)
    ds+= timedelta(minutes=m)
    return ds

def convert_distance(txt):
    f=txt.replace('½','.5').replace('f','')
    dm=0
    if 'm' in f:
        m,f=f.split('m')
        dm=float(m)*1609
    df=0 if f=='' else float(f)*201
    return dm+df

def horses_count(id):
    return len(df_horses[df_horses['rid']==id].index)

def convert_condition(df):
    dic={'Standard':0, 'Good':1, 'Good To Firm':2, 'Very Soft':3,
       'Good To Yielding':4, 'Soft':5, 'Yielding':6, 'Fast':7, 'Firm':8, 'Heavy':9,
       'Good To Soft':10, 'Yielding To Soft':11, 'Soft To Heavy':12,
       'Standard To Slow':13,'Standard To Fast':14, 'Sloppy':15, 'Muddy':16, 'Slow':17,'Holding':18, 'Frozen':19,'Abandoned':20, np.NaN:0}
    return df['condition'].replace(dic)

def convert_class(df):
    dic={np.NaN:0, '':0, 'Class 1':1, 'Class 2':2, 'Class 3':3,
       'Class 4':4, 'Class 5':5, 'Class 6':6, 'Class 7':7}
    return df['rclass'].replace(dic)

def prepare_topred():
    cols_null=['position','res_win', 'res_place','isFav', 'dist']
    cols_home=['course', 'date','marketTime', 'horseName','hname', 'decimalPrice', 'age','RPR', 'TR', 'OR']
    cols_home_calc=['runners', 'ncond', 'metric', 'class','weight']
    cols_home_diffs_ranks=[ 'age', 'decimalPrice', 'weight', 'RPR', 'TR', 'OR']
    cols_stats=['hname','res_win_h_avg_rank', 'res_place_h_avg_rank','decimalPrice_diff_h_avg_rank', 'position_diff_h_avg_rank','res_win_t_avg_rank', 'res_place_t_avg_rank','decimalPrice_diff_t_avg_rank', 'position_diff_t_avg_rank','res_win_j_avg_rank', 'res_place_j_avg_rank','decimalPrice_diff_j_avg_rank', 'position_diff_j_avg_rank','metric_h_avg', 'res_win_h_avg', 'res_place_h_avg','decimalPrice_diff_h_avg', 'RPR_diff_h_avg', 'TR_diff_h_avg','OR_diff_h_avg', 'position_diff_h_avg', 'metric_t_avg', 'res_win_t_avg','res_place_t_avg', 'decimalPrice_diff_t_avg', 'RPR_diff_t_avg','TR_diff_t_avg', 'OR_diff_t_avg', 'position_diff_t_avg', 'metric_j_avg','res_win_j_avg', 'res_place_j_avg', 'decimalPrice_diff_j_avg','RPR_diff_j_avg', 'TR_diff_j_avg', 'OR_diff_j_avg','position_diff_j_avg', 'res_win_h_avg_diff', 'res_place_h_avg_diff','decimalPrice_diff_h_avg_diff', 'position_diff_h_avg_diff','res_win_t_avg_diff', 'res_place_t_avg_diff','decimalPrice_diff_t_avg_diff', 'position_diff_t_avg_diff','res_win_j_avg_diff', 'res_place_j_avg_diff','decimalPrice_diff_j_avg_diff', 'position_diff_j_avg_diff']

    df_stat=pd.read_csv('data/to_train.csv', index_col=False)
    df_stat.drop_duplicates(subset=['horseName'], keep='last', inplace=True)
    df_stat['hname']=df_stat['horseName'].str.lower().replace(regex=True,to_replace=r'\W',value=r'')
    df_today = pd.concat(map(pd.read_csv, glob.glob(path.join('data/today/', '*.csv'))))
    df_today=df_today.reset_index(drop=True)
    df_today['rclass']=df_today['rclass'].fillna('')
    df=df_today[cols_home]
    df['class']=convert_class(df_today)
    df['rid']=df_today.index
    df['rid']=df.groupby(['course','marketTime'])['rid'].transform('sum')
    for col in cols_null:
        df[col]=0
    df['ncond']=convert_condition(df_today)
    df['runners']=df.groupby(['course','marketTime'])['horseName'].transform('count')
    df['metric']=df_today['distance'].apply(lambda x: convert_distance(x))
    df['decimalPrice']=1/df['decimalPrice']
    df['weight']=(df_today['weightSt']*6.35+df_today['weightLb']*0.454).astype(int)
    for col in cols_home_diffs_ranks:
        print(col)
        df[col+'_mean']=df.groupby(['rid'])[col].transform('mean')
        df[col+'_diff']=df[col]-df[col+'_mean']
        df[col+'_diff'].replace([np.inf, -np.inf,np.nan], 0,inplace=True)
        df[col + '_rank'] = df.groupby(['rid'])[col + '_diff'].rank(method='dense', ascending=False).astype(int)
    df.merge(df_stat[cols_stats], on='hname', how='left').to_csv('data/topred.csv')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        action = sys.argv[1]
        if action == 'dl':
            print('DOWNLOAD:')
            load_today()
        elif action == 'p':
            print('PARSE:')
            rps=[]
            atrs=[]
            atr_odds=[]
            parse_today()
            df_atr=pd.concat(atrs)
            df_rp=pd.DataFrame(rps, columns=['course','runners','distance','condition','rclass','date','title','horseName','trainer','jockey','RPR','TR','weightSt','weightLb','age'])
            df_atr['hname']=df_atr['horseName'].str.lower().replace(regex=True,to_replace=r'\W',value=r'')
            df_rp['hname']=df_rp['horseName'].str.lower().replace(regex=True,to_replace=r'\W',value=r'')
            df = df_rp.merge(df_atr[['marketTime', 'hname', 'OR', 'decimalPrice']], on='hname')
            df.to_csv('data/today/{:%Y-%m-%d}.csv'.format(date.today()))
        elif action == 't':
            prepare_topred()
            
