from rouge import Rouge
import csv
from nltk.corpus import stopwords
from src.lda_approach import preprocess


# preprocess - remove stopwords
def remove_stopwords(text):
    stop_words = stopwords.words('english')
    stop_words.extend(('and', 'I', 'A', 'And', 'So', 'arnt', 'This', 'When', 'It', 'many', 'Many', 'so', 'cant', 'Yes',
                       'yes', 'No', 'no', 'These', 'these', 'The', 'the', 'it','Mr'))
    tokens = text.split(" ")
    sen_new = ""
    for token in tokens:
        if token not in stop_words:
           sen_new += token + " "
    return sen_new


# calculate ROUGE scores
def getScores(i,model):
    input_file = open('../data/output/result.csv', encoding='utf8')
    input_data = csv.reader(input_file)
    print("\nStarting " + model + " Evaluation\n")
    rogue = Rouge()
    next(input_data)
    sumf = 0.0
    sump = 0.0
    sumr = 0.0
    count = 0
    results = list()
    for row in input_data:
        hyp = row[9]
        ref = row[10]
        hyp = remove_stopwords(hyp)
        scores = rogue.get_scores(hyp,ref)
        rogue1 = list(scores[0].items())[i]
        f = rogue1[1]['f']
        p = rogue1[1]['p']
        r = rogue1[1]['r']
        if f == 0.0 and p == 0.0 and r == 0.0:
            results.append([0,0,0])
            continue
        sumf += f
        sump += p
        sumr += r
        count += 1
        results.append([f,p,r])
    fields = ['F-Score','Precision','Recall']
    file = '../data/output/RelScores' + str(i) + '.csv'
    with open(file, mode='w', newline='') as output_file:
        output = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output.writerow(fields)
        for output_row in results:
            output.writerow(output_row)
    print("F-Score : " + str(sumf/count))
    print("Precision :" + str(sump/count))
    print("Recall :" + str(sumr/count))



# calculate precision for NER
def getNERScore():
    input_file = open('../data/output/result.csv', encoding='utf8')
    input_data = csv.reader(input_file)
    print("\nStarting NER(ORG) Evaluation\n")
    next(input_data)
    sp_match = 0
    tr_match = 0
    sp_count = 0
    tr_count = 0
    sp_match = 0
    count = 0
    for row in input_data:
        sp_code_org = row[6]
        tr_code_org = row[7]
        actual_org = row[8]
        if(actual_org == ''):
            continue
        sp_code_org = sp_code_org.split(',')
        tr_code_org = tr_code_org.split(',')
        actual_org = actual_org.split(',')
        for org in sp_code_org:
            if (len(org) == 1):
                continue
            for per in actual_org:
                if org in per:
                    sp_match += 1
                    break
            sp_count+=1
        if len(tr_code_org) == 0:
            continue
        for org in tr_code_org:
            if(len(org) == 1):
                continue
            for per in actual_org:
                if org in per:
                    tr_match += 1
                    break
            tr_count += 1
        count += 1
    print("Total Results" + str(count))
    print("True Positive(Spacy)" + str(sp_match))
    print("Precision for Spacy:" + str(sp_match/sp_count))
    print("True Positive(TextRank)" + str(tr_match))
    print("Precision for TextRank:" + str(tr_match / tr_count))


# calculate precision for PERSON tag
def getNERScorePerson():
    input_file = open('../data/output/result.csv', encoding='utf8')
    input_data = csv.reader(input_file)
    print("\nStarting NER(Person)Evaluation\n")
    next(input_data)
    sp_match = 0
    tr_match = 0
    sp_count = 0
    tr_count = 0
    sp_match = 0
    count = 0
    for row in input_data:
        sp_code_org = row[3]
        tr_code_org = row[4]
        actual_org = row[5]
        if(actual_org == ''):
            continue
        sp_code_org = sp_code_org.split(',')
        tr_code_org = tr_code_org.split(',')
        actual_org = actual_org.split(',')
        for org in sp_code_org:
            if (len(org) == 1):
                continue
            for per in actual_org:
                if org in per:
                    sp_match += 1
                    break
            sp_count += 1
        if len(tr_code_org) == 0:
            continue
        for org in tr_code_org:
            if(len(org) == 1):
                continue
            for per in actual_org:
                if org in per:
                    tr_match += 1
                    break
            tr_count += 1
    print("Total Results" + str(count))
    print("True Positive(Spacy)" + str(sp_match))
    print("Precision for Spacy:" + str(sp_match / sp_count))
    print("True Positive(TextRank)" + str(tr_match))
    print("Precision for TextRank:" + str(tr_match / tr_count))


# calculate precision for location
def getLocation():
    input_file = open('../data/output/result.csv', encoding='utf8')
    input_data = csv.reader(input_file)
    print("\nStarting Rule Based Location Finder Evaluation\n")
    next(input_data)
    count = 0
    match = 0
    for row in input_data:
        code_rel = row[2]
        act_rel = row[16]
        if act_rel == "" or code_rel == "":
            continue
        if code_rel.lower() == act_rel.lower():
            match += 1
        count += 1
    print("Total count :" + str(count))
    print("True Positives : " + str(match))
    print("Precision :" + str(match/count))


# calculate precision for date
def getDate():
    input_file = open('../data/output/result.csv', encoding='utf8')
    input_data = csv.reader(input_file)
    print("\nStarting Rule Based Date Finder Evaluation\n")
    next(input_data)
    count = 0
    match = 0
    for row in input_data:
        code_rel = row[1]
        act_rel = row[15]
        if act_rel == "" or code_rel == "":
            continue
        if code_rel == act_rel:
            match += 1
        count += 1
    print("Total count :" + str(count))
    print("True Positives : " + str(match))
    print("Precision :" + str(match/count))

# calculate precision of LDA model
def getRelevancyScore():
    input_file = open('../data/output/result.csv', encoding='utf8')
    input_data = csv.reader(input_file)
    print("\nStarting Relevancy Score Evaluation\n")
    next(input_data)
    count = 0
    match = 0
    for row in input_data:
        code_rel = row[13]
        act_rel = row[14]
        if (code_rel == 'yes' and act_rel == 'Y') or (code_rel == 'no' and act_rel == 'N'):
            match += 1
        count += 1
    print("Total count :" + str(count))
    print("True Positives : " + str(match))
    print("Precision :" + str(match/count))


def main():
    getDate()
    getScores(0, "ROUGE-1")
    getScores(2, "ROUGE-L")
    getNERScorePerson()
    getNERScore()
    getLocation()
    getRelevancyScore()


if __name__ == '__main__':
    main()