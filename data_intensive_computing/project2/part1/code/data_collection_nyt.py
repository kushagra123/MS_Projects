import requests
import datetime
import time
import os
import csv
import pandas as pd
from part1.code.web_crawler import crawl_page


def read_urls(input_file, output_file):
    colnames = ['topic', 'url', 'snippet']
    header = ['topic', 'url', 'snippet', 'text']
    input_data = pd.read_csv(input_file, delimiter=',', names=colnames, encoding='utf-8', skiprows=1)
    news_text = ""
    topics = input_data.topic.tolist()
    urls = input_data.url.tolist()
    snippet = input_data.snippet.tolist()
    with open(output_file, 'w', encoding='utf-8', newline='') as output:
        i = 0
        count = 0
        writer = csv.writer(output)
        writer.writerow(header)
        for uri in input_data.url.tolist():
            if uri != None or uri != "" or uri != " ":
                url_list = list()
                url_list.append(input_data.topic.tolist()[i])
                url_list.append(input_data.url.tolist()[i])
                url_list.append(input_data.snippet.tolist()[i])
                news_text = crawl_page(uri,i)
                url_list.append(news_text)
                writer.writerow(url_list)
                time.sleep(6)
            else:
                count += 1
            i += 1
            if (i - count) == 600:
                break
    output.close()


def store_data(data, subtopic):
    in_list = []
    store_list = []

    length = len(data['response']['docs'])
    for i in range(1, length):
        web_url = data['response']['docs'][i]['web_url']
        text = data['response']['docs'][i]['snippet']
        in_list.append(subtopic)
        in_list.append(web_url)
        in_list.append(text)
        store_list.append(in_list)
        in_list = []
    return store_list


def save_as_csv(csv_list, subtopic, uri):
    header = ['topic', 'url', 'snippet']
    exists = os.path.isfile(uri)
    if exists:
        with open(uri, 'a', encoding='utf-8', newline='') as csvFile:
            writer = csv.writer(csvFile)
            for val in csv_list:
                for v in val:
                    writer.writerow(v)
    else:
        with open(uri, 'w', encoding='utf-8', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(header)
            for val in csv_list:
                for v in val:
                    writer.writerow(v)
    csvFile.close()


def collect_data():
    input_file = '../data/nyt/urls.csv'
    output_file = '../data/nyt/nyt.csv'
    api = "<NYTimes API key>"
    subtopic = ['soccer', 'rugby', 'ice hockey', 'basketball', 'tennis']
    csv_list = []

    # get current date
    i = datetime.datetime.now()
    year = str(i.year)
    if i.month < 10:
        month = "0" + str(i.month)
    else:
        month = str(i.month)
    if i.day < 10:
        day = "0" + str(i.day)
    else:
        day = str(i.day)
    begin_date = "20190101"
    end_date = year + month + day
    url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?q="
    for q in subtopic:
        for pg in range(1, 100):
            final_url = url + q + "&api-key=" + api + "&begin_date=" + begin_date + "&end_date=" + end_date + "&page=" + str(pg)
            r = requests.get(final_url)
            try:
                dat = r.json()
                csv_list.append(store_data(dat, q))
                print("collecting...")
                time.sleep(6)
            except:
                time.sleep(60)
                continue
        save_as_csv(csv_list, q, input_file)
    read_urls(input_file, output_file)


def main():
    collect_data()


if __name__ == '__main__':
    main()