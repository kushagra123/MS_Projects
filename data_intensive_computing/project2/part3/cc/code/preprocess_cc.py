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

def preprocess_cc(input_file):
    colnames = ['text']
    input_data = pd.read_csv(input_file, delimiter=',', names=colnames, encoding='utf-8', skiprows=1)
    data = []
    stop_words = set(stopwords.words('english'))
    for line in input_data.text.tolist():

        # lower case + numbers
        line = line.lower()
        line1 = re.sub(r'\d +', '', line)

        # punctuations + whitespace
        line2 = re.sub('[^a-zA-Z]+', ' ', line1)
        line2 = line2.strip()

        # stop words
        line3 = ' '.join([word for word in line2.split() if word not in stop_words])
        data.append(line3)

    save_as_txt('./data/crawlerData.txt', data)


def main():
    cc_file = '../../../part1/data/cc/cc.csv'
    preprocess_cc(cc_file)


if __name__ == '__main__':
    main()