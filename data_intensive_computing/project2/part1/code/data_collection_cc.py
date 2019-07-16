import requests
import argparse
import time
import json
import urllib3
from io import BytesIO,StringIO
import urllib.request, json
import requests
import numpy
import gzip
import csv
from bs4 import BeautifulSoup


def main():
    data=list()
    with urllib.request.urlopen('https://index.commoncrawl.org/CC-MAIN-2019-13-index?url=https%3A%2F%2Fwww.skysports.com&output=json') as url:
        for l in url:
            data.append(json.loads(l))
    with urllib.request.urlopen('https://index.commoncrawl.org/CC-MAIN-2019-09-index?url=https%3A%2F%2Fwww.skysports.com&output=json') as url:
        for l in url:
            data.append(json.loads(l))
    with urllib.request.urlopen('https://index.commoncrawl.org/CC-MAIN-2019-04-index?url=https%3A%2F%2Fwww.skysports.com&output=json') as url:
        for l in url:
            data.append(json.loads(l))
    filename=list()
    offsets=list()
    lengths=list()
    links=list()
    for d in data:
        filename.append('https://commoncrawl.s3.amazonaws.com/'+d['filename'])
        offsets.append(d['offset'])
        lengths.append(d['length'])
    nfl=0
    nhl=0
    soccer=0
    basketball=0
    tennis=0
    for i in range(0,len(filename)):
        offset= int(offsets[i])
        length=int(lengths[i])
        offset_end = offset + length - 1
        req=requests.get(filename[i],headers={'Range': 'bytes={}-{}'.format(offset, offset_end)})
        temp_data=BytesIO(req.content)
        f=gzip.GzipFile(fileobj=temp_data)
        data=f.read().decode('utf-8')
        res=""
        if len(data):
            try:
                warc,header,res=data.strip().split('\r\n\r\n',2)
            except Exception as ex:
                print(ex)
                pass
        bs=BeautifulSoup(res,"lxml")
        urls=bs.find_all("a")
        if urls:
            for url in urls:
                href=url.attrs.get('href')
                if href!=None:
                    if(href[0]=='/' and '/news/' in href):
                        if href in links:
                            continue
                        print(href)
                        if ('football' in href and '/news/' in href):
                            soccer += 1
                            links.append(href)
                        elif('rugby' in href):
                            nfl+=1
                            links.append(href)
                        elif ('tennis' in href):
                            tennis += 1
                            links.append(href)
                        elif ('hockey' in href):
                            nhl += 1
                            links.append(href)
                        elif ('basketball' in href):
                            basketball += 1
                            links.append(href)
    news_list=list()
    count=0
    for link in links:
        try:
            res=requests.get('https://www.skysports.com'+link)
            soup = BeautifulSoup(res.text, "lxml")
            news = soup.find('div', {'class': 'article__body article__body--lead callfn'})
            news_text = ""
            summary = False
            for p in news.find_all("p"):
                if not summary:
                    summary = True
                    continue
                news_text += p.get_text()
            news_list.append(news_text)
        except:
            print("failed")
            continue
    with open('../data/cc/cc.csv', mode='w', newline='',encoding='utf8') as output_file:
        output = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for output_row in news_list:
            output.writerow([output_row])


if __name__ == "__main__":
    main()
