from bs4 import BeautifulSoup
import requests
import re


def crawl_page(url,i):
    try:
        url = str(url).rstrip()
        res = requests.get(url)
        url = url.rstrip()
        soup = BeautifulSoup(res.text, "lxml")
        news_text = ""
        date = ""
        for news in soup.find_all('div', {'class': 'css-53u6y8'}):
            for p in news.find_all("p"):
                news_text += p.get_text()
    except Exception as ex:
        print(ex)
        print(url+" "+str(i))
        return
    return news_text
