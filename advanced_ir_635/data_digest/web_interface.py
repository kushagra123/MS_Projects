import flask
from flask import Flask, render_template, request
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from urllib import request, parse
import googlemaps
import matplotlib.pyplot as plt
from datetime import datetime
import os
import inspect
import json
import collections
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cnf1miou0vdt9d1qe8sx164zejp3fnay'
app.config["CACHE_TYPE"] = "null"
gmaps = googlemaps.Client(key=<Insert Google API key>)


# create wordcloud for the PERSON tag
def person_wordcloud(data_set):
    filename = 'data/output/person_wordcloud.csv'
    filename1 = 'static/images/Person.png'
    if os.path.exists(filename):
        os.remove(filename)
        print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - File " + filename + " successfully deleted")
    else:
        print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - File " + filename + " could not be deleted")
    if os.path.exists(filename1):
        os.remove(filename1)
        print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - File " + filename1 + " successfully deleted")
    else:
        print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - File " + filename1 + " could not be deleted")
    data_set_wordcloud = data_set.groupby('Person').size()
    data_set_wordcloud.to_csv("data/output/person_wordcloud.csv")
    Hashtag_Combined = " ".join(data_set['Person'].values.astype(str))
    wc = WordCloud(background_color="rgba(0,0,0,0)", stopwords=STOPWORDS)
    wc.generate(Hashtag_Combined)
    plt.figure(figsize=(20,10), facecolor='k')
    plt.imshow(wc)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig('static/images/Person.png', dpi=400, transparent=True)


# create wordcloud for the ORG tag
def org_wordcloud(data_set):
    filename = 'data/output/org_wordcloud.csv'
    filename1 = 'static/images/Organization.png'
    if os.path.exists(filename):
        os.remove(filename)
        print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - File " + filename + " successfully deleted")
    else:
        print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - File " + filename + " could not be deleted")
    if os.path.exists(filename1):
        os.remove(filename1)
        print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - File " + filename1 + " successfully deleted")
    else:
        print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - File " + filename1 + " could not be deleted")
    data_set_wordcloud = data_set.groupby('Organization').size()
    data_set_wordcloud.to_csv("data/output/org_wordcloud.csv")
    Hashtag_Combined = " ".join(data_set['Organization'].values.astype(str))
    wc = WordCloud(background_color="rgba(0,0,0,0)", stopwords=STOPWORDS)
    wc.generate(Hashtag_Combined)
    plt.figure(figsize=(20,10), facecolor='k')
    plt.imshow(wc)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig('static/images/Organization.png', dpi=400, transparent=True)


# create heatmap for the tweets
def tweets_heatmap(location):
    for i in range(len(location)):
        location[i] = location[i].lower()
    source_dict = {'IN': 0, 'ID': 0, 'TH': 0}
    for loc in location:
        if loc == 'india':
                source_dict['IN'] += 1
        elif loc == 'jakarta' or loc == 'indonesia':
                source_dict['ID'] += 1
        elif loc == 'bangkok' or loc == 'thailand':
                source_dict['TH'] += 1
        else:
                source_dict['IN'] += 1
    return source_dict


# lookup Twitter related query on Solr
def get_twitter_data_solr(query):
    filterQuery = parse.quote_plus(query)
    in_url = 'http://localhost:8983/solr/twitter_data/select?indent=on&q=' + filterQuery + '&rows=1000&wt=json'
    data = request.urlopen(in_url)
    docs = json.load(data)
    response = docs['response']['docs']
    output = list()
    source = list()
    person = list()
    org = list()
    topic_list = list()
    date_list = list()
    location = list()
    summary = list()
    for row in response:
        try:
            curr_summary = ""
            curr_per = ""
            curr_org = ""
            curr_date = ""
            curr_loc = ""
            curr_event_type = ""
            if 'Summary' in row.keys():
                curr_summary = row['Summary']
            if 'Person' in row.keys():
                curr_per = row['Person']
            if 'Organization' in row.keys():
                curr_org = row['Organization']
            if 'Date' in row.keys():
                dt = datetime.strptime(row['Date'][0],'%Y-%m-%dT%H:%M:%SZ').strftime('%d-%m-%Y')
                curr_date =[dt]
            if 'Location' in row.keys():
                curr_loc = row['Location']
            if 'Event_Type' in row.keys():
                curr_event_type = row['Event_Type']
            if 'Source' in row.keys():
                source.append(row['Source'])
            output.append([curr_event_type, curr_date, curr_loc, curr_per, curr_org, curr_summary])
        except Exception as ex:
            print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - " + ex)
            continue
    for row in output:
        date_list.append(row[1][0])
        if len(row[2]) > 0:
            location.append(row[2][0])
        topic_list.append(row[0][0])
        if len(row[3]) > 0:
            person.append(row[3][0])
        if len(row[4]) > 0:
            org.append(row[4][0])
        summary.append([row[5]])
    return output, source, date_list, person, org, topic_list, location, summary


# return data for time period analysis
def timeline(dlist):
    date_dict = dict()
    for date in dlist:
        date = str(date)
        d = datetime.strptime(date, '%d-%m-%Y')
        month = datetime.strptime(date, '%d-%m-%Y').strftime('%b')
        year = d.year
        m_y = str(year) + "-" + str(month)
        if m_y in date_dict.keys():
            date_dict[m_y] += 1
        else:
            date_dict[m_y] = 1
    od = collections.OrderedDict(sorted(date_dict.items()))
    return od


# return data for topics analysis
def topics_analysis(topics):
    topics_dict = dict()
    for topic in topics:
        if topic in topics_dict.keys():
            topics_dict[topic] += 1
        else:
            topics_dict[topic] = 1
    ot = collections.OrderedDict(sorted(topics_dict.items()))
    return ot


# return data for source analysis
def source_analysis(sources):
    source_dict = {'IN':0, 'ID':0, 'TH':0}
    for source in sources:
        if source[0] == 'The Times of India':
            source_dict['IN'] += 1
        elif source[0] == 'The Jakarta Globe':
            source_dict['ID'] += 1
        elif source[0] == 'The Bangkok Post':
            source_dict['TH'] += 1
    return source_dict


# lookup news related query on Solr
def get_news_data_solr(query):
    filterQuery = parse.quote_plus(query)
    in_url = 'http://localhost:8983/solr/news_data/select?indent=on&q=' + filterQuery + '&rows=100&wt=json'
    data = request.urlopen(in_url)
    docs = json.load(data)
    response = docs['response']['docs']
    output = list()
    coord = list()
    source = list()
    for row in response:
        try:
            curr_summary = ""
            curr_per = ""
            curr_org = ""
            curr_date = ""
            curr_loc = ""
            curr_event = ""
            if 'Summary' in row.keys():
                curr_summary = row['Summary']
            if 'Person' in row.keys():
                curr_per = row['Person']
            if 'Organization' in row.keys():
                curr_org = row['Organization']
            if 'Event_Date' in row.keys():
                curr_date = row['Event_Date']
            if 'Location' in row.keys():
                curr_loc = row['Location']
            if 'Event_Type' in row.keys():
                curr_event = row['Event_Type']
            if 'Coordinates' in row.keys():
                coord.append(row['Coordinates'])
            if 'Source' in row.keys():
                source.append(row['Source'])
            output.append([curr_event, curr_date, curr_loc, curr_per, curr_org, curr_summary])
        except Exception as ex:
            print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - " + ex)
            continue
    return output, coord, source


@app.route("/", methods = ['GET', 'POST'])


def index():
    src_analysis = []
    field_names = ['Event Type', 'Event Date', 'Location', 'Person', 'Organization', 'Summary']
    if flask.request.method == 'POST':
        date_list = list()
        topic_list = list()
        timeline_key_list = list()
        timeline_val_list = list()
        topics_key_list = list()
        topics_val_list = list()
        text = flask.request.form.get('stext')
        combo_source = flask.request.form.get('combo')
        if combo_source == 'twitter':
            output, source, date_list, person, org, topic_list, location,summary=get_twitter_data_solr(text)
            src_analysis = ['Twitter']
            coord = []
            source_dict = source_analysis(source)
            location_dict = tweets_heatmap(location)
            location_key_list = list()
            location_val_list = list()
            for key, value in location_dict.items():
                location_key_list.append(key)
                location_val_list.append(value)
            source_key_list = ['Twitter']
            source_val_list = [len(source)]
        elif combo_source == 'news':
            src_analysis = ['The Times of India', 'The Jakarta Globe', 'The Bangkok Post']
            output, coord, source = get_news_data_solr(text)
            for row in output:
                date_list.append(row[1][0])
                topic_list.append(row[0][0])
            person = list()
            org = list()
            for row in output:
                if len(row[3]) > 0:
                    person.append(row[3][0])
                if len(row[4]) > 0:
                    org.append(row[4][0])
            source_dict = source_analysis(source)
            source_key_list = []
            source_val_list = []
            for key, value in source_dict.items():
                source_key_list.append(key)
                source_val_list.append(value)
            location_key_list = source_key_list
            location_val_list = source_val_list
            person_df = pd.DataFrame(person, columns=["Person"])
            org_df = pd.DataFrame(org, columns=["Organization"])
            org_wordcloud(org_df)
            person_wordcloud(person_df)
        ddict = timeline(date_list)
        for key, value in ddict.items():
            timeline_key_list.append(key)
            timeline_val_list.append(value)
        topics_dict = topics_analysis(topic_list)
        for key, value in topics_dict.items():
            topics_key_list.append(key)
            topics_val_list.append(value)
        return render_template('index.html', fieldname=field_names, tldate=timeline_key_list, tlfreq=timeline_val_list, tevent=topics_key_list, tfreq=topics_val_list, src=source_key_list, srcfreq=source_val_list, srcAnalysis=src_analysis, loc=location_key_list, locfreq=location_val_list, coord=coord, len=len(output), output=output)
    else:
        output1 = [['', '', '', '', '']]
        return render_template("index.html", fieldname=field_names, tldate=[''], tlfreq=[0], tevent=[''], tfreq=[0], src=[''], srcfreq=[''], srcAnalysis=src_analysis, coord=[], len=0, output=output1)


if __name__ == '__main__':
    app.run(debug=True)
