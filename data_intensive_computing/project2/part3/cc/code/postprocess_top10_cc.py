from nltk.stem import WordNetLemmatizer, SnowballStemmer
import csv


def post_process_dict(dic, output_file):
    lemmatizer = WordNetLemmatizer()
    proc_dict = {}
    for key,value in dic.items():
        word = key
        count = value
        word_lemmatized = lemmatizer.lemmatize(word, pos='v')
        if word_lemmatized in proc_dict:
            proc_dict[word_lemmatized] += int(count)
        else:
            proc_dict[word_lemmatized] = int(count)
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        for key, value in proc_dict.items():
            writer.writerow([key, value])
    outfile.close()
    return proc_dict


def top10(filename):
    dict_words = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for rows in file:
            word = rows.split('\t', 1)[0]
            count = rows.split('\t', 1)[1]
            dict_words[word] = count
    file.close()
    count = 0
    dict_words=post_process_dict(dict_words, './data/crawlerWords.txt')
    with open('./data/top10_crawler.txt', 'w', encoding='utf-8', newline='') as outfile:
        for key, value in sorted(dict_words.items(), key=lambda item: item[1], reverse=True):
            if count < 10:
                print("%s: %s" % (key, value))
                outfile.write("%s: %s\n" % (key, value))
            count += 1
    outfile.close()



def main():
    top10('../../../part2/mr_output/output_cc_wc')

if __name__ == '__main__':
    main()