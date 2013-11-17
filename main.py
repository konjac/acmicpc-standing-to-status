from pyquery import PyQuery as PQ
import urllib2
import sys
import time
import os
import ConfigParser
import re

def fetch(url, TeamNum):
    html = urllib2.urlopen(url).read()
    table = PQ(html).find("#standings")[0]
    trs = PQ(table).find("tr")
    record = {}
    record['TimeStamp'] = re.findall("[0-9]{4}/[0-9]{2}/[0-9]{2} ([0-9]{2}:[0-9]{2}:[0-9]{2})", html)[0]
    start = re.findall("[0-9]{4}-[0-9]{2}-[0-9]{2} ([0-9]{2}:[0-9]{2})", html)[0]
    record['Teams'] = [None] * TeamNum
    print record['TimeStamp']
    for tr in trs[1:-1]:
        uid = int(re.findall("([0-9]+)", PQ(tr).find('a').attr('href'))[0])
        tds = PQ(tr).find("td")
        team = {}
        team['SchoolName'] = tds[1].text
        team['TeamRank'] = tds[2].text
        team['TeamName'] = tds[3].text_content()
        team['Solved'] = tds[4].text
        team['Penalty'] = tds[5].text
        team['Problem'] = []
        for td in tds[6:]:
            team['Problem'].append(td.text)
        record["Teams"][uid] = team;
    return record


def utf8_wrapper(s):
    if isinstance(s, unicode):
        return unicode.encode(s, 'utf-8')
    else:
        return s

def compare(TeamsA, TeamsB, TimeStamp, TeamNum, ProblemCount):
    Status = []
    for uid in range(0, TeamNum):
        for i in range(0, ProblemCount):
            #print id, TeamsA[id]
            pre = TeamsA[uid]['Problem'][i]
            cur = TeamsB[uid]['Problem'][i]
            Time = TimeStamp
            if pre <> cur:
                pos = cur.find("/")
                if pos == -1:
                    result = "Submit"
                else:
                    result = "Accepted"
                    #Time = cur.split("/")[1]
                Status.append({'Time': TimeStamp,
                               'Team': TeamsA[uid]['TeamName'],
                               'SchoolName' : TeamsA[uid]['SchoolName'],
                               'Problem': chr(i + ord('A')),
                               'Result': result,
                               'RankChange': pos <> -1 and TeamsA[uid]['TeamRank'] + " --> " + TeamsB[uid]['TeamRank'] or ""} )
    return Status


def readConfig():
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    RankURL = config.get("Input", "RankURL")
    TeamNum = int(config.get("Input", "TeamNum"))
    ProblemCount = int(config.get("Input", "ProblemCount"))
    Path = config.get("Output", "Path")
    return RankURL, TeamNum, ProblemCount, Path

RankURL, TeamNum, ProblemCount, Path = readConfig()

tempPath = Path + ".temp"

recA = fetch("http://localhost/test/rank-test.htm", TeamNum)
status = []
while True:
    recB = fetch(RankURL, TeamNum)
    status = compare(recA["Teams"], recB["Teams"], recB["TimeStamp"], TeamNum, ProblemCount)
    f = open(tempPath, "w+")
    for s in status:
        text = ("<tr class='%s'><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>") % (s['Result'] == 'Accepted' and 'ac' or 'fail',
                                                                                                             s['Time'],
                                                                                                             s['SchoolName'],
                                                                                                             s['Team'],
                                                                                                             s['Problem'],
                                                                                                             s['Result'],
                                                                                                             s['RankChange'])
        #print text
        f.write(utf8_wrapper(text))
    f.close()
    recA = recB
    os.system( ("type %s >> %s") % (Path, tempPath))
    os.system( ("copy %s %s") % (tempPath, Path))
    time.sleep(10)
    break
