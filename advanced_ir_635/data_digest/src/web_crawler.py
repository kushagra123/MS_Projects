from bs4 import BeautifulSoup
import requests
import dateparser
import csv
import re
import os
import inspect
from googlesearch import search


# crawl through the search result URLs of The Times of India
def get_toi_news_urls():
    print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - Fetching Times of India URLS")
    news_data = list()
    for i in range(1, 4):
        res = requests.get("https://timesofindia.indiatimes.com/topic/Election-riots-India/news/" + str(i))
        soup = BeautifulSoup(res.text, "lxml")
        urls = list()
        news = soup.find_all('div', {'class':'content'})
        for div in news:
            links = div.findAll('a')
            for link in links:
                url = link['href']
                if "https:" not in url and "/videos/" not in url:
                    url = "https://timesofindia.indiatimes.com" + url
                    if url not in news_data:
                        news_data.append([url, 'The Times of India'])
                    print(url)
    with open('../data/input/FinalNews/news-data-TI-latest.csv', mode='w', newline='') as output_file:
        output = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output.writerow(['URL', 'Source'])
        for output_row in news_data:
            output.writerow(output_row)


# crawl through the search result URLs of The Bangkok Post
def get_tbp_news_urls():
    print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - Fetching The Bangkok Post URLS")
    news_data = list()
    for i in range(2):
        res = requests.get("http://search.bangkokpost.com/search/result?start=" + str(i*10) + "&q=election+riots&category=news&sort=relevance&rows=10&refinementFilter=AQRuZXdzDGNoYW5uZWxhbGlhcwEBXgEk")
        soup = BeautifulSoup(res.text, "lxml")
        urls = list()
        news = soup.find_all('div', {'class':'detail'})
        for div in news:
            try:
                links = div.find_all('h3')
                for link in links:
                    news_a = link.find_all('a')
                    for new_a in news_a:
                        url = new_a['href']
                        if url not in news_data:
                            news_data.append([url, 'The Bangkok Post'])
                    print(url)
            except:
                continue
    with open('../data/input/FinalNews/news-data-BP-latest.csv', mode='w', newline='') as output_file:
        output = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output.writerow(['URL', 'Source'])
        for output_row in news_data:
            output.writerow(output_row)


# crawl through the search result URLs of The Jakarta Globe
def get_tjg_news_urls():
    print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - Fetching The Jakarta Globe URLS")
    news_data = list()
    for i in range(2):
        res = requests.get("https://jakartaglobe.id/landing/search?keyword=riots+jakarta&page=" + str(i))
        soup = BeautifulSoup(res.text, "lxml")
        news = soup.find_all('div', {'class':'newsindex'})
        for div in news:
            try:
                links = div.findAll('a')
                for link in links:
                    url = link['href']
                    if url not in news_data:
                        news_data.append([url, 'The Jakarta Globe'])
                    print(url)
            except:
                continue
    with open('../data/input/FinalNews/news-data-JG-latest.csv', mode='w', newline='') as output_file:
        output = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output.writerow(['URL', 'Source'])
        for output_row in news_data:
            output.writerow(output_row)


# crawl through each URL to get news text
def crawl_page(url, source):
    url = url.rstrip()
    res = requests.get(url, verify=False)
    soup = BeautifulSoup(res.text, "lxml")
    news_text = ""
    date = ""
    if source == "The Times of India":
        news = soup.find('div', {'class':'_3WlLe clearfix '})
        news_text = re.sub('<[^>]*>', '', str(news))
        date = soup.find('div', {'class':'_3Mkg- byline'}).get_text()
        date = re.sub('%B %d, %Y %H:%M', '', date)
    elif source == "The Hindu":
        article = soup.select("[class~=article]")
        title = article[0].select("[class~=title]")
        title = title[0].get_text()
        body = article[0].select("[id*='content-body-']")
        news_text = ""
        for p in body[0].find_all("p"):
            news_text += p.get_text()
        dateDiv = soup.find('div', {'class':'ut-container'})
        for p in dateDiv.find_all("span"):
            date = dateDiv.find("none")
            if date == None:
                continue
            else:
                date = date.get_text()
    elif source == "The Jakarta Post":
        news = soup.find('div', {'class': 'col-md-10 col-xs-12 detailNews'})
        text_news = news.find("p")
        news_text = text_news.get_text()
        dateSpan = soup.find('span', {'class':'day'})
        if dateSpan != None:
            date = dateSpan.get_text()
    elif source == "The Bangkok Post":
        news = soup.find('div', {'class': 'articleContents'})
        news_text = ""
        for p in news.find_all("p"):
            news_text += p.get_text()
        dateSpan = soup.find('span', {'itemprop': 'datePublished'})
        if dateSpan != None:
            date = dateSpan.get_text()
    elif source == "The Jakarta Globe":
        news = soup.find('div', {'class': 'mb20 col-md-12 body-content lh14'})
        news_text = ""
        for p in news.find_all("p"):
            news_text += p.get_text()
        dateSpan = soup.find('p', {'class': 'ls1 mb0 fs10 nbold text-left w100'})
        date = dateSpan.get_text()
        date = re.sub('\s+', '', date)
    news_text = news_text.splitlines()
    regex = ['\'\'',',']
    for rex in regex:
        news_text = re.sub(rex, '', str(news_text))
    return news_text, date



def get_url():
    input_file = open('../data/input/acled_filtered.csv')
    input_data = csv.reader(input_file)
    next(input_data)
    result = list()
    count = 0
    for row in input_data:
        try:
            if count <= 119:
                count += 1
                continue
            text = row[7]
            text = text + " " + row[6]
            for url in search(text, stop=1, pause=10):
                result.append([row[6], row[7], url])
            count += 1
        except Exception as ex:
            print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - " + str(ex))
            break
    with open('../data/input/moreArticles3.csv', mode='w', newline='') as output_file:
        output = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for output_row in result:
            output.writerow(output_row)



def filter_url():
    input_file = open('../data/input/moreArticles3.csv')
    input_data = csv.reader(input_file)
    result = list()
    count = 0
    for row in input_data:
        source = row[0]
        text = row[1]
        url = row[2]
        if url not in result and ('thehindu' in url or 'timesofindia' in url):
            result.append([source,text,url])
            count += 1
    with open('../data/input/filterurl2.csv', mode='w', newline='') as output_file:
        output = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for output_row in result:
            output.writerow(output_row)