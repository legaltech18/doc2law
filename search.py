"""
Use Whoosh index files to find law section
"""
#!/usr/bin/env python

from whoosh.qparser import QueryParser
from whoosh.lang.porter import stem
from whoosh.lang.morph_en import variations
from whoosh.analysis import StemmingAnalyzer
import whoosh.index as index
from whoosh.qparser import QueryParser, OrGroup
import sqlite3


INDEX_DIR = 'db/index'
DATABASE_URL = "db/corpus.db"
TABLE_NAME = "law_text"


def get_full_law_para(law_title, para_num, matched):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    query = f"SELECT law_text from {TABLE_NAME} where law_name='{law_title}' and section='{para_num}'"
    all_text = ""
    for row in c.execute(query):
        text = row[0]
        if matched != text: 
            all_text += "<br>"+text
        else:
            all_text += "<br> <mark>"+text+"</mark>"
    return all_text
 
    
def text_search(query_input):
    ix = index.open_dir(INDEX_DIR)
    stem_ana = StemmingAnalyzer()
    query_input_stem = stem_ana(query_input)

    # #How to use the expanded query?
    # expanded_terms = []
    # for token in query_input_stem:
    #     expanded_terms.append(variations(token.text))
    # print(expanded_terms)
    response = {}
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(query_input)
        response['query'] = str(query)
        results = searcher.search(query)
        results_list = []
        print(results)
        if results:
            for r in results:
                matched, law_title, para_n = r.values()
                if para_n == "":
                    para_n = None
                score = "{0:.2f}".format(r.score)
                full_text = get_full_law_para(law_title, para_n, matched)
                results_list.append([matched, law_title, para_n, score, full_text])
        response['results'] = results_list
    return response
    

def term_expander(term):
    from nltk.corpus import wordnet as wn
    from nltk.corpus import stopwords
    stopWords = set(stopwords.words('english'))
    if term in stopWords:
        return [term]
    all_terms = [term]
    # One uses wordnet and the other uses word2vec
    extended_terms = wn.synsets(term)
    for term in extended_terms:
        term_word = str(term).split("'", 1)[-1]
        term_word = str(term_word).split(".", 1)[0]
        term_word = term_word.replace('_', ' ')
        all_terms.append(term_word)
    return list(set(all_terms))


def or_search(query_input):
    ix = index.open_dir(INDEX_DIR)
    response = {}
    with ix.searcher() as searcher:
        query = QueryParser("content", schema=ix.schema, group=OrGroup).parse(query_input)
        response['query'] = str(query)
        results = searcher.search(query)
        results_list = []
        if results:
            for r in results:
                content, law_title, para_n = r.values()
                url = law_title + '.' + para_n
                score = "{0:.2f}".format(r.score) # Careful! may lose accuracy
                results_list.append((content, url, score))
        response['results'] = results_list
    return response



import whoosh.analysis as analysis
from itertools import product
def query_expander(input_sent):
    ana = analysis.RegexTokenizer()
    input_terms = [t.text for t in ana(input_sent, mode="index")]
#     pprint(term_expander(input_terms[0]))
    expanded_terms = [term_expander(term) for term in input_terms]
#     print(list(expanded_terms))
    text_product = product(*expanded_terms)
#     print(list(text_product))
    expanded_sentences = [" ".join(sent) for sent in text_product]
    return expanded_sentences
#     print() 


def run_search(law_case):
    import nltk
    case_sentences = nltk.tokenize.sent_tokenize(law_case)
    # case_sentences = tokenizer.tokenize(law_case)
    expanded_case = []
    matched_laws = []
    for case_sentence in case_sentences:
        expanded_sentences = query_expander(case_sentence)
        for sentence in expanded_sentences:
            matched_laws.append(text_search(sentence))
    return matched_laws

def result_list_combiner(matched_laws):
    law_section_freq = {}
    from pprint import pprint
    for match in matched_laws:
            for law_match in match['results']:
                law_section = law_match[1]
                if law_section in law_section_freq.keys():
                    law_section_freq[law_section] += 1
                else:
                    law_section_freq[law_section] = 1
    pprint(law_section_freq)
            # ~ break
        
        
if __name__ == '__main__':
    from pprint import pprint
    output  = run_search(input())
    print(result_list_combiner(output))
    #pprint(output)
