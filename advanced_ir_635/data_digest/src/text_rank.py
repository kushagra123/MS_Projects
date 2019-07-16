import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from nltk.corpus import stopwords
import os
import inspect

word_embeddings = {}

# load GloVe word embeddings
def load_word_embeddings():
    print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - Loading GloVe embeddings file")
    f = open('../data/input/glove.6B.100d.txt', encoding='utf-8')
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        word_embeddings[word] = coefs
    f.close()


# remove stopwords from sentences
def remove_stopwords(sen):
    stop_words = stopwords.words('english')
    stop_words.extend(('and', 'I', 'A', 'And', 'So', 'arnt', 'This', 'When', 'It', 'many', 'Many', 'so', 'cant', 'Yes',
                       'yes', 'No', 'no', 'These', 'these', 'The', 'the', 'it','Mr'))
    sen_new = " ".join([i for i in sen if i not in stop_words])
    return sen_new


# apply TextRank algorithm and return top 10 sentences as summary
def text_rank(sentences, source):
    sentence_vectors = []
    if len(sentences) <= 2:
        return '.'.join(sentences)
    sentences_processed = list()
    for sen in sentences:
        sen_new = remove_stopwords(sen.split())
        sentences_processed.append(sen_new)
    for i in sentences_processed:
      try:
          if len(i) != 0:
            v = sum([word_embeddings.get(w, np.zeros((100,))) for w in i.split()])/(len(i.split())+0.001)
          else:
            v = np.zeros((100,))
          sentence_vectors.append(v)
      except Exception as ex:
          print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - " + str(ex))
    sim_mat = np.zeros([len(sentences), len(sentences)])
    for i in range(len(sentences)):
      for j in range(len(sentences)):
        try:
            if i != j:
              sim_mat[i][j] = cosine_similarity(sentence_vectors[i].reshape(1,100), sentence_vectors[j].reshape(1,100))[0,0]
        except Exception as ex:
            print(os.path.basename(__file__) + "::" + inspect.currentframe().f_code.co_name + " - " + str(ex))
            continue
    nx_graph = nx.from_numpy_array(sim_mat)
    scores = nx.pagerank(nx_graph)
    ranked_sentences = sorted(((scores[i],s) for i, s in enumerate(sentences)), reverse=True)
    result = ""
    if source == "news":
        if len(ranked_sentences) < 6:
            for i in range(2):
                result += ranked_sentences[i][1] + "."
        else:
            for i in range(4):
              result += ranked_sentences[i][1] + "."
    elif source == "twitter":
        for i in range(2):
          result += ranked_sentences[i][1] + "."
    return result
