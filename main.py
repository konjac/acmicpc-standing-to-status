from pyquery import PyQuery as PQ
import urllib2
import sys
import time
import os
import ConfigParser

def fetch(url):
    html = urllib2.urlopen(url).read()
    table = PQ(html).find("#standings")[0]
    trs = PQ(table).find("tr")
    record = {}
    record['TimeStamp'] = time.strftime('%H:%M:%S',time.localtime(time.time()));
    record['Teams'] = {}
    for tr in trs[1:-1]:
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
        record["Teams"][team['TeamName']] = team;
    return record


def utf8_wrapper(s):
    if isinstance(s, unicode):
        return unicode.encode(s, 'utf-8')
    else:
        return s

def compare(TeamsA, TeamsB, TimeStamp, ProblemCount):
    Status = []
    for TeamName in TeamsA:
        for i in range(0, ProblemCount):
            #print TeamName, TeamsA[TeamName]
            pre = TeamsA[TeamName]['Problem'][i]
            cur = TeamsB[TeamName]['Problem'][i]
            if pre <> cur:
                pos = cur.find("/")
                if pos == -1:
                    result = "Submit"
                else:
                    result = "Accepted"
                Status.append({'Time': TimeStamp,
                               'Team': TeamName,
                               'SchoolName' : TeamsA[TeamName]['SchoolName'],
                               'Problem': chr(i + ord('A')),
                               'Result': result,
                               'RankChange': pos <> -1 and TeamsA[TeamName]['TeamRank'] + " --> " + TeamsB[TeamName]['TeamRank'] or ""} )
    return Status


def readConfig():
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    RankURL = config.get("Input", "RankURL")
    ProblemCount = int(config.get("Input", "ProblemCount"))
    Path = config.get("Output", "Path")
    return RankURL, ProblemCount, Path

RankURL, ProblemCount, Path = readConfig()

tempPath = Path + ".temp"

recA = fetch("http://localhost/test/aaa.html")
status = []
while True:
    time.sleep(1)
    recB = fetch(RankURL)
    status = compare(recA["Teams"], recB["Teams"], recB["TimeStamp"], ProblemCount) + status
    f = open(tempPath, "w")
    for s in status:
        text = ("<tr class='%s'><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>") % (s['Result'] == 'Accepted' and 'ac' or 'fail',
                                                                                                             s['Time'],
                                                                                                             s['SchoolName'],
                                                                                                             s['Team'],
                                                                                                             s['Problem'],
                                                                                                             s['Result'],
                                                                                                             s['RankChange'])
        print text
        f.write(utf8_wrapper(text))
    f.close()
    os.system( ("copy %s %s") % (tempPath, Path))
#    break
