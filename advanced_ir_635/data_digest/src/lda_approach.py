from gensim.utils import simple_preprocess
from gensim import corpora, models
from nltk.corpus import stopwords
import csv
from nltk.stem import WordNetLemmatizer, SnowballStemmer
import os
import inspect


# initialize global values to None
elec_dictionary = None
riots_dictionary = None
VAC_dictionary = None
lda_model = None
riot_lda_model = None
VAC_lda_model = None


# configure stemming lemmatizing parameters
# return lemmatized text
stemmer = SnowballStemmer('english')
def lemmatize_stemming(text,stemmer):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))


# remove stopwords from text
def preprocess(text):
    result = []
    stop_words = stopwords.words('english')
    stop_words.extend(('and', 'I', 'A', 'And', 'So', 'arnt', 'This', 'When', 'It', 'many', 'Many', 'so', 'cant', 'Yes',
                       'yes', 'No', 'no', 'These', 'these', 'The', 'the', 'it'))
    for token in simple_preprocess(text):
        if token not in stop_words and len(token) >3:
            result.append(lemmatize_stemming(token,stemmer))
    return result


# train LDA model for identifying riots/protests topics
def load_lda_rp():
    print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - Loading Riots/Protests model")
    input_file = open('../data/input/riots.csv')
    input_data = csv.reader(input_file)
    processed_docs = list()
    count=0
    for rows in input_data:
        if count == 1000:
            break
        pro_docs = preprocess(rows[0])
        processed_docs.append(pro_docs)
        count += 1
    global riots_dictionary
    global riot_lda_model
    riots_dictionary = corpora.Dictionary(processed_docs)
    bow_corpus = [riots_dictionary.doc2bow(doc) for doc in processed_docs]
    riot_lda_model = models.LdaModel(bow_corpus, num_topics=10, id2word=riots_dictionary, passes=100)


# train LDA model for identifying violence against civilians topics
def load_lda_vac():
    print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - Loading Violence against Civilians model")
    input_file = open('../data/input/VAC.csv')
    input_data = csv.reader(input_file)
    processed_docs = list()
    count=0
    for rows in input_data:
        if count == 1000:
            break
        pro_docs = preprocess(rows[0])
        processed_docs.append(pro_docs)
        count += 1
    global VAC_dictionary
    global VAC_lda_model
    VAC_dictionary = corpora.Dictionary(processed_docs)
    bow_corpus = [VAC_dictionary.doc2bow(doc) for doc in processed_docs]
    VAC_lda_model = models.LdaModel(bow_corpus, num_topics=10, id2word=VAC_dictionary, passes=100)


# train LDA model for identifying if election violence relevant
def load_lda_election():
    print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - Loading Election Violence model")
    input_file = open('../data/input/training_set.csv')
    input_data = csv.reader(input_file)
    processed_docs = list()
    for rows in input_data:
        pro_docs = preprocess(rows[0])
        processed_docs.append(pro_docs)
    global elec_dictionary
    global lda_model
    elec_dictionary = corpora.Dictionary(processed_docs)
    bow_corpus = [elec_dictionary.doc2bow(doc) for doc in processed_docs]
    lda_model = models.LdaModel(bow_corpus, num_topics=10, id2word=elec_dictionary, passes=100)


# load all LDA models
def load_lda():
    print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - Loading LDA models")
    load_lda_election()
    load_lda_rp()
    load_lda_vac()


# LDA score for election violence = max(scores)
def compare_doc_election(doc):
    bow_vector = elec_dictionary.doc2bow(preprocess(doc))
    score_list = list()
    for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1 * tup[1]):
        score_list.append(score)
    return max(score_list)


# LDA score for riots/protests and violence against civilians = avg(scores)
def compare_doc_rp_vac(doc):
    riots_bow_vector = riots_dictionary.doc2bow(preprocess(doc))
    riot_score_list = list()
    VAC_score_list = list()
    for index, score in sorted(riot_lda_model[riots_bow_vector], key=lambda tup: -1 * tup[1]):
        riot_score_list.append(score)
    VAC_bow_vector = VAC_dictionary.doc2bow(preprocess(doc))
    for index, score in sorted(VAC_lda_model[VAC_bow_vector], key=lambda tup: -1 * tup[1]):
        VAC_score_list.append(score)
    avg_riot_score = sum(riot_score_list)/len(riot_score_list)
    avg_VAC_score = sum(VAC_score_list)/len(VAC_score_list)
    if avg_riot_score < avg_VAC_score:
        return "Violence Against Civilian"
    else:
        return "Riots/Protests"