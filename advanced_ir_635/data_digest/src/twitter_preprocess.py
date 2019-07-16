import csv
import json
import os
import preprocessor

tweets = list()


# remove repetitions in extract_summarize_tweets
def get_unique_tweets():
    dir = "../data/input/twitter"
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith('.csv'):
                input_data = csv.reader(open(os.path.join(dir, file), encoding='utf8'))
                next(input_data)
                for row in input_data:
                    try:
                        if row[1] not in tweets and row[11] != 'TRUE':
                            text = preprocessor.clean(row[4])
                            tweets.append([row[1], text, row[71], row[2]])
                    except:
                        continue


# store unique extract_summarize_tweets as CSV
def write_tweets_to_csv():
    fields=['user', 'texts', 'location', 'date']
    with open('../data/input/tweets.csv', mode='w', newline='') as output_file:
        output = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output.writerow(fields)
        for output_row in tweets:
            output.writerow(output_row)


# extract required fields from Twitter JSON response
def json_extract():
    tweet = list()
    dir = '../data/input'
    fields = ['user', 'texts', 'location', 'date']
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith('.json'):
                input_data = os.path.join(dir, file)
                output_data = os.path.splitext(input_data)[0] + '.csv'
                next(input_data)
                for row in input_data:
                    with open(file=row, encoding='utf-8', mode='r') as file:
                        for linep in file:
                            line_obj = json.loads(linep)
                            id = line_obj["id"]
                            rt = line_obj["retweeted"]
                            text = line_obj["text"]
                            location = line_obj["user"]["location"]
                            createdat = line_obj["created_at"]
                            if id not in tweet and rt != 'TRUE':
                                text = preprocessor.clean(text)
                                tweet.append([id, text, location, createdat])
                    file.close()
                    with open(output_data, encoding='utf8', mode='w', newline='') as output_file:
                        output = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        output.writerow(fields)
                        for output_row in tweet:
                            output.writerow(output_row)


def update_tweets():
    get_unique_tweets()
    write_tweets_to_csv()
    json_extract()
