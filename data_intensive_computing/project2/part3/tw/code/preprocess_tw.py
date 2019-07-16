import pandas as pd
import json
import string
import re
import os
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import preprocessor

def save_as_txt(filename, data):
    exists = os.path.isfile(filename)
    if exists:
        with open(file=filename, encoding='utf-8', mode='a') as output:
            for dat in data:
                output.write(dat + "\n\n")
    else:
        with open(file=filename, encoding='utf-8', mode='w') as output:
            for dat in data:
                output.write(dat + "\n\n")
    print("Processed: " + filename)


def preprocess_tw(input_file):
    data = []
    stop_words = set(stopwords.words('english'))
    with open(file=input_file, encoding='utf-8', mode='r') as file:
        for linep in file:
            line_obj = json.loads(linep)
            line = line_obj["text"]
            # remove hashtag, mentions, urls, emojis, smileys, etc
            line1 = preprocessor.clean(line)
            # lower case + number
            line1 = line1.lower()
            line2 = re.sub(r'\d +', '', line1)
            line2 = re.sub('[^a-zA-Z]+', ' ', line2)

            # stop words
            line4 = ' '.join([word for word in line2.split() if word not in stop_words])
            data.append(line4)

    file.close()
    save_as_txt('./data/twitterData.txt', data)


def main():
    tw_file = '../../../part1/data/tw/twitter.json'
    preprocess_tw(tw_file)


if __name__ == '__main__':
    main()