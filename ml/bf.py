import json
import csv
import bz2
import numpy as np
import pandas as pd
from os import path, listdir
from datetime import datetime, timedelta, date
import sys

def load_files(ds, de):
    d = ds
    while d <= de:
        markets_file = open('data/BF/markets_{:%Y-%m-%d}.csv'.format(d), mode='a+', newline='',  encoding='utf8')
        markets_writer = csv.writer(markets_file, delimiter=',')
        markets_writer.writerow(['mid','eid','dt','marketType','marketTime','name','eventName','bspMarket','turnInPlayEnabled','marketBaseRate','eventTypeId','numberOfWinners','numberOfActiveRunners','countryCode','timezone','openDate','version'])
        runners_file = open('data/BF/runners_{:%Y-%m-%d}.csv'.format(d), mode='a+', newline='',  encoding='utf8')
        runners_writer = csv.writer(runners_file, delimiter=',')
        runners_writer.writerow(['mid','dt','rid','name','sortPriority','adjustmentFactor','status'])
        changes_file = open('data/BF/changes_{:%Y-%m-%d}.csv'.format(d), mode='a+', newline='',  encoding='utf8')
        changes_writer = csv.writer(changes_file, delimiter=',')
        changes_writer.writerow(['mid','dt','rid','price'])
        base='output/BASIC/{:%Y/%b/%#d}/'.format(d)
        for folder in listdir(base):
            for f in listdir(base+folder):
                with bz2.open(base+folder+'/'+f, "r") as bz_file:
                    c=0
                    for line in bz_file:
                        #ln="".join( chr(x) for x in line).replace('"name"}','"name":"unknown"}')
                        #data = json.loads(ln)
                        data = json.loads(line)
                        parse_day(data, d, markets_writer, runners_writer, changes_writer)
                        c+=1
                    print (base+folder+'/'+f,c)
                #break
        markets_file.close()
        runners_file.close()
        changes_file.close()
        d += timedelta(days=1)

def parse_day(data, d, markets_writer, runners_writer, changes_writer):
    op=data['op']
    clk=data['clk']
    pt=datetime.fromtimestamp(data['pt']//1000)
    #print('\n At {:%Y-%b-%d %H:%M:%S}:'.format(pt))
    if 'mc' in data:
        markets=data['mc']
        for market in markets:
            mid=market['id'][2:]
            # MARKET DEFINITION
            if 'marketDefinition' in market:
                md=market['marketDefinition']
                eventId=md['eventId']
                bspMarket=md['bspMarket']
                turnInPlayEnabled=md['turnInPlayEnabled']
                marketBaseRate=md['marketBaseRate']
                eventTypeId=md['eventTypeId']
                numberOfWinners=md['numberOfWinners']
                marketType=md['marketType'] if 'marketType' in md else ''
                marketTime=md['marketTime']
                numberOfActiveRunners=md['numberOfActiveRunners']
                countryCode=md['countryCode'] if 'countryCode' in md else ''
                timezone=md['timezone']
                openDate=md['openDate']
                version=md['version']
                name=md['name']
                eventName=md['eventName']
                markets_writer.writerow([mid,eventId,pt,marketType,marketTime,name,eventName,bspMarket,turnInPlayEnabled,marketBaseRate,eventTypeId,numberOfWinners,numberOfActiveRunners,countryCode,timezone,openDate,version])
                runners_list=[]
                runners=md['runners']
                for runner in runners:
                    adjustmentFactor=runner['adjustmentFactor'] if 'adjustmentFactor' in runner else np.NaN
                    status=runner['status']
                    sortPriority=runner['sortPriority']
                    rid=runner['id']
                    name=runner['name']
                    runners_writer.writerow([mid,pt,rid,name,sortPriority,adjustmentFactor,status])
                    runners_list.append([name,rid,adjustmentFactor,status,sortPriority])
                #print(f'{mid} definition: eventName={eventName}, name={name}, version={version}, eventId={eventId}, bspMarket={bspMarket}, turnInPlayEnabled={turnInPlayEnabled}, marketBaseRate={marketBaseRate}, eventTypeId={eventTypeId}, numberOfWinners={numberOfWinners}, marketType={marketType}, marketTime={marketTime}, countryCode={countryCode}, timezone={timezone}, openDate={openDate}, numberOfActiveRunners={numberOfActiveRunners}:')
                #print(runners_list)

            # RUNNERS CHANGE
            if 'rc' in market:
                runners=market['rc']
                #print(f'{mid} price(s) change:', end=' ')
                for runner in runners:
                    rid=runner['id']
                    price=runner['ltp']
                    changes_writer.writerow([mid,pt,rid,price])
                    #print(f'{rid}:{price};', end=' ')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        ds = de = datetime.strptime(sys.argv[1], '%Y-%m-%d')
    else:
        ds = datetime.strptime(sys.argv[1], '%Y-%m-%d')
        de = datetime.strptime(sys.argv[2], '%Y-%m-%d')
    load_files(ds, de)