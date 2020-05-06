from os import path, listdir
import csv
import re
from datetime import datetime, timedelta, date
from selenium import webdriver
import sys
import time

def load_days(ds, de):
    driver = webdriver.Chrome(executable_path=r'../../lib/chromedriver.exe')
    d = ds
    while d >= de:
        fn = 'output/days/{:%Y-%m-%d}.html'.format(d)
        if path.exists(fn) and path.getsize(fn) > 10000:
            d += timedelta(days=-1)
            continue
        driver.get('https://www.racingpost.com/results/{:%Y-%m-%d}'.format(d))
        time.sleep(3)
        html = driver.page_source

        with open(fn, 'w+', encoding='utf8') as f:
            f.write(html)
        print('{} done with {} bytes.'.format(fn, len(html)))
        d += timedelta(days=-1)
    driver.close()


def parse_days(ds, de):
    d = ds
    while d >= de:
        with open('output/days/{:%Y-%m-%d}.html'.format(d), 'r', encoding='utf8') as f:
            html = f.read()
        print('Try to parse output/days/{:%Y-%m-%d}.html ({} bytes)'.format(d,len(html)))
        parse_day(html)
        d += timedelta(days=-1)


def getone(pattern, string):
    m = pattern.search(string)
    res = m.group(1) if m else ''
    return res.strip()


def parse_day(html):
    f = open('data/days.csv', mode='a+', newline='',  encoding='utf8')
    writer = csv.writer(f, delimiter=',')



    pStarPerformerName = re.compile(
        r'href="([^"]+)"\s*target="_blank"\s*data-test-selector="link-starPerformerName">')
    #r'data-test-selector="link-starPerformerName">\s*([^<]+)')
    pStarPerformerTime = re.compile(
        r'data-test-selector="text-starPerformerTime">\s*([^<]+)')
    pStarPerformerNotes = re.compile(
        r'data-test-selector="text-starPerformerNotes">\s*([^<]+)')



    pEyecatcherName = re.compile(
        r'href="([^"]+)"\s*target="_blank"\s*data-test-selector="link-eyecatcherName">')
    #r'data-test-selector="link-eyecatcherName">\s*([^<]+)')
    pEyecatcherTime = re.compile(
        r'data-test-selector="text-eyecatcherTime">\s*([^<]+)')
    pEyecatcherNotes = re.compile(
        r'data-test-selector="text-eyecatcherNotes">\s*([^<]+)')
    
    pRaceTime = re.compile(r'data-test-selector="race-panel-\d+-([^"]+)"')
    pRaceLink = re.compile(
        r'<div class="rp-raceCourse__panel__race__info__title">\s+<a href="([^"]+)')

    parts = html.split(
        '<h2 class="rp-raceCourse__row__name"')[1:]
    for part in parts:
        raceCourseName = part[part.find('>')+1:part.find('<')].split('(')[0].strip()
        starPerformerName = getone(pStarPerformerName, part)
        starPerformerTime = getone(pStarPerformerTime, part).replace(
            '(', '').replace(')', '').replace('.', ':')
        starPerformerNotes = getone(pStarPerformerNotes, part)
        eyecatcherName = getone(pEyecatcherName, part)
        eyecatcherTime = getone(pEyecatcherTime, part).replace(
            '(', '').replace(')', '').replace('.', ':')
        eyecatcherNotes = getone(pEyecatcherNotes, part)
       
        links = pRaceLink.findall(part)
        times = pRaceTime.findall(part)

        if len(times) == 0:
            continue

        for i in range(len(links)):
            perf = starPerformerName if starPerformerTime == times[i] else ''
            perfNotes = starPerformerNotes if starPerformerTime == times[i] else ''
            eyec = eyecatcherName if eyecatcherTime == times[i] else ''
            eyecNotes = eyecatcherNotes if eyecatcherTime == times[i] else ''
            #print(times[i], eyecatcherTime, eyec, eyecNotes)
            writer.writerow(
                [links[i], perf, perfNotes, eyec, eyecNotes])
        print('{}: {} races has found'.format(raceCourseName, len(links)))
    f.close()


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Please add action, ds and de to script call!')
    else:
        action=sys.argv[1]
        ds = datetime.strptime(sys.argv[2], '%Y-%m-%d')
        de = datetime.strptime(sys.argv[3], '%Y-%m-%d')
        if action=='dl':
            print('DOWNLOAD:')
            load_days(ds, de)
        elif action=='p':
            print('PARSE:')
            parse_days(ds, de)
