import csv
import nltk
import os
import inspect
from src.web_crawler import crawl_page
from src.text_rank import text_rank,load_word_embeddings
from nltk.tokenize import sent_tokenize
import googlemaps
from src.lda_approach import load_lda,compare_doc_election,compare_doc_rp_vac
from src.text_extract import get_per_org_tags,get_loc,textrank_keyword,get_date
import pandas as pd
from src.twitter_preprocess import update_tweets
import dateparser
from nltk.corpus import stopwords

gmaps = googlemaps.Client(key=<Insert Google API key>)


# remove stopwords from text
def remove_stopwords(text):
    stop_words = stopwords.words('english')
    stop_words.extend(('and', 'I', 'A', 'And', 'So', 'arnt', 'This', 'When', 'It', 'many', 'Many', 'so', 'cant', 'Yes',
                       'yes', 'No', 'no', 'These', 'these', 'The', 'the', 'it','Mr'))
    sen_new = " ".join([i for i in text if i not in stop_words])
    return sen_new


# pre-process news text to remove stopwords, tokenize
def pre_process_news(text):
    df = text.split('.')
    sentences = list()
    for sentence in df:
        sentences.append(sent_tokenize(sentence))
    sentences = [y for x in sentences for y in x]  # flatten list
    sentences = pd.Series(sentences).str.replace("[^a-zA-Z]", " ")
    sentence_processed = [remove_stopwords(r.split()) for r in sentences]
    sentence_text = '.'.join(sentence_processed)
    return sentences, sentence_text


# pre-process tweets to remove stopwords, tokenize
def pre_process_twitter(text):
    df = text.split('.')
    sentences = list()
    for sentence in df:
        sentences.append(sent_tokenize(sentence))
    sentences = [y for x in sentences for y in x]  # flatten list
    sentence_processed = [remove_stopwords(r.split()) for r in sentences]
    sentence_text = '.'.join(sentence_processed)
    return sentences, sentence_text


# keyword extraction and summarization for news article
def extract_summarize_news(input_data, count):
    output_data = list()
    # Iterate rows of input_data
    # 0-Country,1-Source,2-URL,3-Summary
    for row in input_data:
        try:
            news_text, pub_date = crawl_page(row[0], row[1])
            score = compare_doc_election(news_text)
            if score < 0.34:
                continue
            eventType = compare_doc_rp_vac(news_text)
            news_processed_list, news_text_processed = pre_process_news(news_text)
            summary = text_rank(news_processed_list, "news")
            location = get_loc(news_text_processed)
            latlon = []
            if location != None:
                geo_loc = location.lower()
                geocode_result = gmaps.geocode(geo_loc)
                lat = geocode_result[0]["geometry"]["location"]["lat"]
                lon = geocode_result[0]["geometry"]["location"]["lng"]
                latlon = [lat, lon]
                if location in news_text_processed:
                    news_text_processed = news_text_processed.replace(location, '')
            relevancePerson = textrank_keyword(news_text_processed, ["PERSON"])
            relevanceOrg = textrank_keyword(news_text_processed, ["ORG"])
            date = get_date(pub_date, news_text_processed)
            if len(list(relevancePerson)) > 3 :
                tr_person_str = ','.join(list(relevancePerson)[:3])
            else:
                tr_person_str = ','.join(list(relevancePerson))
            if len(list(relevanceOrg)) > 3:
                tr_org_str = ','.join(list(relevanceOrg)[:3])
            else:
                tr_org_str = ','.join(list(relevanceOrg))
            data_row = [count, date, location, tr_person_str, tr_org_str, eventType, summary, latlon, row[1]]
            output_data.append(data_row)
            count += 1
        except Exception as ex:
            print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - " + str(ex))
            continue
    return output_data, count


# keyword extraction and summarization for extract_summarize_tweets
def extract_summarize_tweets(tweet_data):
    count = 1
    output_data = list()
    # Iterate rows of input_data
    # 0-Country,1-Source,2-URL,3-Summary
    for row in tweet_data:
        try:
            person = list()
            org = list()
            tweet_text = row[1]
            score = compare_doc_election(tweet_text)
            if score < 0.34:
                continue
            eventType = compare_doc_rp_vac(tweet_text)
            news_processed_list, news_text_processed = pre_process_twitter(tweet_text)
            if len(news_processed_list) > 1:
                summary = text_rank(news_processed_list, "twitter")
            else:
                summary = news_processed_list[0]
            location = get_loc(news_text_processed)
            if location == None:
                location = row[2]
            else:
                news_text_processed = news_text_processed.replace(location, "")
            relevancePerson = textrank_keyword(news_text_processed, ["PERSON"])
            relevanceOrg = textrank_keyword(news_text_processed, ["ORG"])
            if len(list(relevancePerson)) > 0:
                person = list(relevancePerson)[0]
            if len(list(relevanceOrg)) > 0:
                org = list(relevanceOrg)[0]
            date = row[3]
            data_row = [count, date, location, person, org, summary, eventType, "Twitter"]
            output_data.append(data_row)
            count += 1
        except Exception as ex:
            continue
    fields = ["Sr.no","Date","Location", "Person", "Organization","Summary","Event Type","Source"]
    with open('../data/output/tweet_result.csv', mode='w', newline='', encoding='utf8') as output_file:
        output = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output.writerow(fields)
        for output_row in output_data:
            output.writerow(output_row)


def main():
    load_word_embeddings()
    load_lda()
    output_data = list()
    count = 0
    dir = "../data/input/FinalNews"
    print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - Starting Extraction & Summarization of news data")
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith('.csv'):
                input_data = csv.reader(open(os.path.join(dir, file), encoding='utf8'))
                next(input_data)
                temp, count = extract_summarize_news(input_data, count)
                output_data += temp
    fields = ["Sr.no", "Event Date", "Location", "Person", "Organization", "Event Type", "Summary", "Coordinates",
              "Source"]
    with open('../data/output/results.csv', mode='w', newline='', encoding='utf8') as output_file:
        output = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output.writerow(fields)
        for output_row in output_data:
            output.writerow(output_row)
    input_file = open('../data/input/tweets.csv')
    input_data = csv.reader(input_file)
    next(input_data)
    print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - Starting Extraction & Summarization of Twitter data")
    extract_summarize_tweets(input_data)


if __name__ == '__main__':
    main()