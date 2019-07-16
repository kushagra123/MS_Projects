import nltk
import numpy as np
from datetime import datetime
from datetime import timedelta
from collections import OrderedDict
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from nltk.chunk import conlltags2tree, tree2conlltags
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
import pandas as pd
from nltk.chunk import ne_chunk
from nltk.sem.relextract import NE_CLASSES
import json
from nltk import Tree
import re
import os
import inspect
from nltk.tag.stanford import StanfordNERTagger
import nltk
import spacy


# Load SpaCy configuration and location dataset
nlp = spacy.load('en_core_web_sm')
loc_data_india = pd.read_csv('../data/input/India_places.csv', encoding="ISO-8859-1")
loc_data_other = pd.read_csv('../data/input/worldcities.csv', encoding="ISO-8859-1")


def get_continuous_chunks(tagged_sent):
    continuous_chunk = []
    current_chunk = []
    for token, tag in tagged_sent:
        if tag != "O":
            current_chunk.append((token, tag))
        else:
            if current_chunk:
                continuous_chunk.append(current_chunk)
                current_chunk = []
    if current_chunk:
        continuous_chunk.append(current_chunk)
    return continuous_chunk


# create PERSON and ORGANIZATION sets from tagged NEs
def get_per_org_tags(text, only=False, candidate=None):
    doc = nlp(text)
    person = set()
    org = set()
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            person.add(ent.text)
            text = text.replace(ent.text, '')
        elif ent.label_ == "ORG":
            org.add(ent.text)
            text = text.replace(ent.text, '')
    if only == True:
        if candidate == "PERSON":
            return person
        elif candidate == "ORG":
            return org
    return person, org


# obtain first matched location from both NE tagging and location dataset
def get_loc(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON" or ent.label_ == "ORG" or ent.label_ == "GPE":
            location = ent.text
            if location.lower() in (oname.lower() for oname in loc_data_india['districtname']) or location.lower() in (oname.lower() for oname in loc_data_india['statename']) or location.lower() in (oname.lower() for oname in loc_data_other['city']):
                return location


# store sentences with PERSON and ORGANIZATION tags only
def sentence_segment(doc, candidate_pos):
    sentences = []
    for sent in doc.sents:
        selected_words = []
        for token in sent:
            if token.ent_type_ in candidate_pos and token.is_stop is False:
                    selected_words.append(token.text)
        sentences.append(selected_words)
    return sentences


# get token pairs using sliding window
def get_token_pairs(window_size, sentences):
    token_pairs = list()
    for sentence in sentences:
        for i, word in enumerate(sentence):
            for j in range(i + 1, i + window_size):
                if j >= len(sentence):
                    break
                pair = (word, sentence[j])
                if pair not in token_pairs:
                    token_pairs.append(pair)
    return token_pairs


# get normalized matrix
def get_matrix(vocab, token_pairs):
    vocab_size = len(vocab)
    g = np.zeros((vocab_size, vocab_size), dtype='float')
    for word1, word2 in token_pairs:
        i, j = vocab[word1], vocab[word2]
        g[i][j] = 1
    g = g + g.T - np.diag(g.diagonal())
    norm = np.sum(g, axis=0)
    g_norm = np.divide(g, norm, where=norm != 0)
    return g_norm


# get term frequency for all tokens
def term_freq_count(sentences):
    vocab = OrderedDict()
    count = 0
    for sentence in sentences:
        for word in sentence:
            if word not in vocab:
                vocab[word] = count
                count += 1
    return vocab


# get rule-based extraction of date
# obtain date by identifying relative date patterns
def get_date(date, phrase):
    day = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    date = date.strip()
    # The Bangkok Post
    if ' at' in date:
        rest = date.split(' at', 1)[0]
        d1 = datetime.strptime(rest, '%d %b %Y')
        dt = datetime.strptime(rest, '%d %b %Y').strftime('%A')
    # The Times of India
    elif ('|' in date and ':' in date):
        rest = re.sub(r'.*: ', '', date)
        rest = rest.split(' IST', 1)[0]
        rest = rest.strip()
        d1 = datetime.strptime(rest, '%b %d, %Y, %H:%M')
        dt = datetime.strptime(rest, '%b %d, %Y, %H:%M').strftime('%A')
    # The Hindu
    elif ' IST' in date:
        rest = date.split(' IST', 1)[0]
        rest = rest.strip()
        d1 = datetime.strptime(rest, '%B %d, %Y %H:%M')
        dt = datetime.strptime(rest, '%B %d, %Y %H:%M').strftime('%A')
    # The Jakarta Globe
    else:
        d1 = datetime.strptime(date, '%B%d,%Y')
        dt = datetime.strptime(date, '%B%d,%Y').strftime('%A')
    if dt == 'Sunday':
        index = 7
    elif dt in day:
        index = day.index(dt)
    else:
        d2 = d1.strftime('%d-%m-%Y')
        return d2
    pos = -1
    if ('yesterday' in phrase) and not ('day before yesterday' in phrase):
        pos = index - 1
    elif 'day before yesterday' in phrase:
        pos = index - 2
    elif 'last week' in phrase:
        pos = index - 7
    else:
        for d in day:
            if d in phrase:
                pos = day.index(d)
                break
    if pos == -1:
        d2 = d1.strftime('%d-%m-%Y')
        return d2
    diff = index - pos
    if diff < 0:
        diff += 7
    d2 = (d1 - timedelta(days=diff)).strftime('%d-%m-%Y')
    return d2


# compute node weight of PERSON and ORGANIZATION tags
def textrank_keyword(text, candidate, window_size=4):
    doc = nlp(text)
    sentences = sentence_segment(doc, candidate)
    vocab = term_freq_count(sentences)
    token_pairs = get_token_pairs(window_size, sentences)
    g = get_matrix(vocab, token_pairs)
    pr = np.array([1] * len(vocab))
    previous_pr = 0
    for epoch in range(10):
        pr = (1 - 0.85) + 0.85 * np.dot(g, pr)
        if abs(previous_pr - sum(pr)) < 1e-5:
            break
        else:
            previous_pr = sum(pr)
    node_weight = dict()
    for word, index in vocab.items():
        node_weight[word] = pr[index]
    node_weight = OrderedDict(sorted(node_weight.items(), key=lambda t: t[1], reverse=True))
    result = dict()
    for i, (key, value) in enumerate(node_weight.items()):
        result[key] = value
    return result