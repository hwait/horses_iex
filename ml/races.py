from os import path, listdir, remove
import csv
import re
from datetime import datetime, timedelta, date
from selenium import webdriver
import sys
import pandas as pd
import time

isCheck = False
basepath = 'c:/dev/RP/ML/output/races/'
a = [316362]


def load_races(rid1, rid2):
    df = pd.read_csv('data/days.csv')
    driver = webdriver.Chrome(executable_path=r'../../lib/chromedriver.exe')
    id = rid1
    while id <= rid2:
        fn = 'output/races/{}.html'.format(id)
        if path.exists(fn) and path.getsize(fn) > 150000:
            id += 1
            continue
        link = df.loc[df['rid'] == id].link.iat[0]
        driver.get('https://www.racingpost.com/{}'.format(link))
        # time.sleep(3)
        html = driver.page_source
        with open(fn, 'w+', encoding='utf8') as f:
            f.write(html)
        print('[{}]: {} done with {} bytes.'.format(id, link, len(html)))
        id += 1
    driver.close()


def load_races1(rid1, rid2):
    df = pd.read_csv('data/days.csv')
    driver = webdriver.Chrome(executable_path=r'../../lib/chromedriver.exe')
    id = rid1
    while id <= rid2:
        fn = 'output/races/{}.html'.format(id)
        if path.exists(fn) and path.getsize(fn) > 150000:
            id += 1
            continue
        link = df.iloc[id].link
        driver.get('https://www.racingpost.com/{}'.format(link))
        time.sleep(3)
        html = driver.page_source
        with open(fn, 'w+', encoding='utf8') as f:
            f.write(html)
        print('[{}]: {} done with {} bytes.'.format(id, link, len(html)))
        id += 1
    driver.close()


errors = []


def parse_races(rid1, rid2):
    df = pd.read_csv('data/days.csv')
    id = rid1
    while id <= rid2:
        row = df[df['rid'] == id].iloc[0]
        link = row.link
        performer = row.performer
        performerNotes = row.performerNotes
        eyecatcher = row.eyecatcher
        eyecatcherNotes = row.eyecatcherNotes
        with open('output/races/{}.html'.format(id), 'r', encoding='utf8') as f:
            html = f.read()
        if isCheck:
            try:
                parse_race(html, id, link, performer,
                           performerNotes, eyecatcher, eyecatcherNotes)
            except:
                print(f'ERROR in {id}!')
                errors.append(id)
        else:
            parse_race(html, id, link, performer, performerNotes,
                       eyecatcher, eyecatcherNotes)
        id += 1
    print(errors)


def parse_files():
    df = pd.read_csv('data/days.csv')

    for f in listdir(basepath):
        id = int(f.replace('.html', ''))
        # print(id,f)
        with open(basepath+f, 'r', encoding='utf8') as f:
            html = f.read()
        row = df[df['rid'] == id].iloc[0]
        link = row.link
        performer = row.performer
        performerNotes = row.performerNotes
        eyecatcher = row.eyecatcher
        eyecatcherNotes = row.eyecatcherNotes
        if isCheck:
            try:
                parse_race(html, id, link, performer,
                           performerNotes, eyecatcher, eyecatcherNotes)
            except:
                print(f'ERROR in {id}!')
                errors.append(id)
        else:
            parse_race(html, id, link, performer, performerNotes,
                       eyecatcher, eyecatcherNotes)
        # break
    print(errors)


def getone(pattern, string):
    m = pattern.search(string)
    res = m.group(1) if m else ''
    return res.strip()


def parseminsec(string):
    string = string.replace('s', '')
    m = 0
    if 'm' in string:
        (m, s) = string.split('m')
        m = float(m.strip())
        s = float(s.strip())
    else:
        s = float(string.strip())
    return m*60+s


def clearhorsename(string):
    string = string.replace(')', '').strip()
    ret = string
    if '(' in string:
        ret = string.split('(')[0]
    if ret == '':
        ret = string.split('(')[1]
    return ret.strip()


pCourse = re.compile(r'rp-raceTimeCourseName__name[^>]+>\s*([^<]+)')
pTime = re.compile(r'data-analytics-race-time="([^"]+)')

pDate = re.compile(
    r'data-test-selector="text-raceDate">([^<]+)')
pTitle = re.compile(r'<h2 class="rp-raceTimeCourseName__title">([^<]+)')
pClass = re.compile(r'<span class="rp-raceTimeCourseName_class">([^<]+)')
pBandAndAgesAllowed = re.compile(
    r'<span class="rp-raceTimeCourseName_ratingBandAndAgesAllowed">([^<]+)')
pDistance = re.compile(
    r'<span class="rp-raceTimeCourseName_distance" data-test-selector="block-distanceInd">([^<]+)')
pCondition = re.compile(
    r'<span class="rp-raceTimeCourseName_condition">([^<]+)')
pHurdles = re.compile(r'<span class="rp-raceTimeCourseName_hurdles">([^<]+)')
pPrizes = re.compile(
    r'<span class="rp-raceTimeCourseName__prizeMoneyTitle">[^<]+</span>([^<]+)')
pWinningTime = re.compile(
    r'Winning time:\s*<span class="rp-raceInfo__value">([^<]+)')
pComment = re.compile(r'text-comments">\s*<td colspan="11">([^<]+)')
pHorseAncName = re.compile(
    r'<a href="/profile/horse/[^"]+" class="ui-profileLink ui-link ui-link_table js-popupLink">([^<]+)')
pHorseAncLink = re.compile(
    r'<a href="/profile/horse/([^"]+)" class="ui-profileLink ui-link ui-link_table js-popupLink">')
pRPR = re.compile(
    r'<td class="rp-horseTable__spanNarrow" data-ending="RPR" data-test-selector="full-result-rpr">([^<]+)')
pTR = re.compile(
    r'<td class="rp-horseTable__spanNarrow" data-ending="TS" data-test-selector="full-result-topspeed">([^<]+)')
pOR = re.compile(
    r'<td class="rp-horseTable__spanNarrow" data-ending="OR">([^<]+)')
pWeightSt = re.compile(
    r'<span class="rp-horseTable__st" data-ending="st" data-test-selector="horse-weight-st">([^<]+)')
pWeightLb = re.compile(
    r'<span data-ending="lb" data-test-selector="horse-weight-lb">([^<]+)')
pOverWeight = re.compile(
    r'<img src="https://www.rp-assets.com/pdfs/over_weight.gif" alt="Over-Weights" data-test-selector="img-overWeight">\s*<span>([^<]+)')
pOutHandicap = re.compile(
    r'<img src="https://www.rp-assets.com/pdfs/out_of_handicap.gif" alt="Out-of-Handicaps" data-test-selector="img-outOfHandicap">\s*<span>([^<]+)')
pHeadGear = re.compile(r'<span class="rp-horseTable__headGear">([^<]+)')
pAge = re.compile(
    r'<td class="rp-horseTable__spanNarrow rp-horseTable__spanNarrow_age" data-ending="yo" data-test-selector="horse-age">([^<]+)')
pTrainerLink = re.compile(r'<a href="/profile/trainer/([^"]+)"')
pTrainerName = re.compile(r'link-trainerName">([^<]+)')
pJockeyLink = re.compile(r'<a href="/profile/jockey/([^"]+)"')
pJockeyName = re.compile(r'link-jockeyName">([^<]+)')
pPrice = re.compile(r'<span class="rp-horseTable__horse__price">([^<]+)')
pHorseLink = re.compile(r'<a href="/profile/horse/([^"]+)"')
pHorseName = re.compile(r'link-horseName">([^<]+)')
pSaddle = re.compile(r'<span class="rp-horseTable__saddleClothNo">([^<]+)')
pPosition = re.compile(r'data-test-selector="text-horsePosition">([^<]+)')
pPositionL = re.compile(r'<span class="rp-horseTable__pos__length">([^<]+)')


def parse_race(html, rid, link,  performer, performerNotes, eyecatcher, eyecatcherNotes):
    print(' Trying to parse [{}]: {} ... '.format(rid, link), end=' ')
    course = getone(pCourse, html)
    racetime = getone(pTime, html)

    date = time.strftime(
        '%Y-%m-%d', time.strptime(getone(pDate, html), '%d %b %Y'))
    title = getone(pTitle, html)
    rclass = getone(pClass, html).replace('(', '').replace(')', '')
    bandAndAgesAllowed = getone(pBandAndAgesAllowed, html).replace(
        '(', '').replace(')', '').split(', ')
    if len(bandAndAgesAllowed) > 1:
        band = bandAndAgesAllowed[0]
        ages = bandAndAgesAllowed[1]
    else:
        if 'yo' in bandAndAgesAllowed[0]:
            band = ''
            ages = bandAndAgesAllowed[0]
        else:
            band = bandAndAgesAllowed[0]
            ages = ''

    distance = getone(pDistance, html).replace('(', '').replace(')', '')
    condition = getone(pCondition, html)
    hurdles = getone(pHurdles, html)
    winningTime = getone(pWinningTime, html)
    if '(' in winningTime:
        winningTime = winningTime.split('(')[0]
    winningTime = parseminsec(winningTime.strip())

    prizes = []
    mm = pPrizes.findall(html)
    for m in mm:
        prizes.append(float(m.strip()[1:].replace(',', '')))
    currency = ''
    if len(mm) > 0 and '£' in mm[0]:
        currency = 'GBP'
    if len(mm) > 0 and '€' in mm[0]:
        currency = 'EUR'
    parts = html.split(
        '<tr class="rp-horseTable__mainRow" data-test-selector="table-row">')[1:]
    if len(parts) == 0:
        print(' ERROR!!! 0 horses found!!!')
        return
    if not isCheck:
        fr = open(f'data/done/races_{date}.csv',
                  mode='a+', newline='',  encoding='utf8')
        writerr = csv.writer(fr, delimiter=',')
        writerr.writerow([rid, course, racetime, date, title, rclass, band, ages, distance,
                          condition, hurdles, prizes, currency, winningTime, link, performer, performerNotes, eyecatcher, eyecatcherNotes])
        fr.close()
        fh = open(f'data/done/horses_{date}.csv',
                  mode='a+', newline='',  encoding='utf8')
        writerh = csv.writer(fh, delimiter=',')
    for part in parts:
        part = part.split(
            '<tr class="rp-horseTable__hackRow">')[0].replace('–', '')

        horseLink = getone(pHorseLink, part)
        horseName = getone(pHorseName, part)
        age = getone(pAge, part)
        saddle = getone(pSaddle, part).replace('.', '')
        position = getone(pPosition, part)
        price = getone(pPrice, part)
        price = '' if 'No' in price else price
        isFav = '1' if ('F' in price) or (
            'J' in price) or ('C' in price) else '0'
        price = price.replace('F', '').replace(
            'J', '').replace('C', '').replace('Evens', '1/1').replace('Evs', '1/1')
        decimalPrice = ''
        if price != '':
            (a, b) = price.split('/')
            decimalPrice = str(float(a)/float(b)+1).replace('.0', '')
        trainerLink = getone(pTrainerLink, part)
        trainerLink = '' if trainerLink == '0/' else trainerLink
        trainerName = getone(pTrainerName, part)
        jockeyLink = getone(pJockeyLink, part)
        jockeyLink = '' if jockeyLink == '0/' else jockeyLink
        jockeyName = getone(pJockeyName, part)

        RPR = getone(pRPR, part)
        TR = getone(pTR, part)
        OR = getone(pOR, part)
        part = part.replace('<!--', '').replace('-->', '')
        weightSt = getone(pWeightSt, part)
        weightLb = getone(pWeightLb, part)
        overWeight = getone(pOverWeight, part)
        outHandicap = getone(pOutHandicap, part)
        headGear = getone(pHeadGear, part)
        part = part.replace('<span>', '').replace('</span>', '')
        positionL = getone(pPositionL, part).replace(']', '').replace(
            '½', '.5').replace('¼', '.25').replace('¾', '.75').replace('&nbsp;', '')
        dist = ''
        if '[' in positionL:
            (positionL, dist) = positionL.split('[')
            positionL = positionL.strip()
            dist = dist.strip()
        if 'data-test-selector="block-pedigreeInfoFullResults">' in part:
            part = part.split(
                'data-test-selector="block-pedigreeInfoFullResults">')[1]
            links = pHorseAncLink.findall(part)
            names = [clearhorsename(x) for x in pHorseAncName.findall(part)]
        else:
            links = names = ['', '', '']

        if len(links) == 0:
            links = names = ['', '', '']
        if len(links) == 1:
            links.append('')
            names.append('')
        if len(links) == 2:
            links.append('')
            names.append('')
        comment = getone(pComment, part).split('(')[0].strip()
        if not isCheck:
            writerh.writerow([rid, horseName, horseLink, age, saddle, price, decimalPrice, isFav, trainerLink, trainerName, jockeyLink, jockeyName, position, positionL,
                              dist, weightSt, weightLb, overWeight, outHandicap, headGear, RPR, TR, OR, names[0], names[1], names[2], links[0], links[1], links[2], comment])

        #print('horseName="{}",horseLink="{}",age="{}",saddle="{}",price="{}",decimalPrice="{}", isFav="{}",trainerLink="{}",trainerName="{}",jockeyLink="{}",jockeyName="{}",position="{}",positionL="{}",dist="{}",weightSt="{}",weightLb="{}",overWeight="{}",outHandicap="{}",headGear="{}",RPR="{}",TR="{}",OR="{}",names="{}",links="{}",comment="{}"'.format(horseName,horseLink,age,saddle,price,decimalPrice,isFav,trainerLink,trainerName,jockeyLink,jockeyName,position,positionL,dist,weightSt,weightLb,overWeight,outHandicap,headGear,RPR,TR,OR,names,links,comment))
    if not isCheck:
        fh.close()
    print(' done with {} horses'.format(len(parts)))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        parse_files()
        exit()
    elif len(sys.argv) == 3:
        action = sys.argv[1]
        rid1 = rid2 = int(sys.argv[2])
    else:
        action = sys.argv[1]
        rid1 = int(sys.argv[2])
        rid2 = int(sys.argv[3])
    if action == 'dl':
        print('DOWNLOAD:')
        load_races(rid1, rid2)
    elif action == 'p':
        print('PARSE:')
        #parse_races(rid1, 1000000)
        parse_races(rid1, rid2)
    else:
        for x in a:
            remove(basepath+f'{x}.html')
            print(x, ' removed.')
