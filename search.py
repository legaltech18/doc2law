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
    query = 'SELECT law_text from %s where law_name=\'%s\' and section=\'%s\'' % (TABLE_NAME, law_title, para_num)
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


# ~ def or_search(query_input):
    # ~ ix = index.open_dir(INDEX_DIR)
    # ~ response = {}
    # ~ with ix.searcher() as searcher:
        # ~ query = QueryParser("content", schema=ix.schema, group=OrGroup).parse(query_input)
        # ~ response['query'] = str(query)
        # ~ results = searcher.search(query)
        # ~ results_list = []
        # ~ if results:
            # ~ for r in results:
                # ~ content, law_title, para_n = r.values()
                # ~ url = law_title + '.' + para_n
                # ~ score = "{0:.2f}".format(r.score) # Careful! may lose accuracy
                # ~ results_list.append((content, url, score))
        # ~ response['results'] = results_list
    # ~ return response



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
    scored_results = result_list_combiner(matched_laws)
    # use combined_result to sort results...
    from pprint import pprint
    # ~ pprint(matched_laws)
    pprint(scored_results)
    final_results = []
    for sr in scored_results:
        law_section, para_n = sr
        # ~ print(matched_laws)
        for match in matched_laws:
            if match['results'] == []:
                continue
            # ~ print(match)
            # ~ print("\n\n")
            samples = []
            for res in match['results']:
                m_sample, m_section, m_para_n, _, full_text = res
                if law_section == m_section and para_n == m_para_n:
                    samples.append(m_sample)
            result = (law_section, para_n, samples[0], full_text) # ! samples of 0!! (should work for every sample)
            final_results.append(result)
    return final_results
    # ~ return combined_result

def dict_increment(d, tag, i=1):
    if tag in d.keys():
        d[tag] += i
    else:
        d[tag] = i
    return d


def result_list_combiner(matched_laws):
    import operator
    law_section_freq = {}
    law_section_score= {}
    golden_words = ['fine', 'imprisonment', 'whosoever', 'liable']
    from pprint import pprint
    golden_list = []
    for match in matched_laws:
            for law_match in match['results']:
                law_section = law_match[1]
                para_num = law_match[2]
                full_text = law_match[4]
                tag = (law_section, para_num)
                law_section_freq = dict_increment(law_section_freq, tag)
                if law_section == "stgb":
                    import re
                    para_num_int = int(re.split("[a-z]", para_num)[0])
                    if para_num_int < 80:
                        # law_section_score = dict_increment(law_section_score, tag, 1)
                        pass
                    else:
                        law_section_score = dict_increment(law_section_score, tag, 10)
                for gw in golden_words:
                    if gw in full_text:
                        golden_list.append(tag)
                        break #Score only once for any golden word occurance?
    # ~ pprint(law_section_freq)
    for k in law_section_score.keys():
        if k in set(golden_list):
            law_section_score[k] += 2
    law_section_score = sorted(law_section_score.items(), key=operator.itemgetter(1),  reverse=True)
    return [s[0] for s in law_section_score]
            # ~ break


if __name__ == '__main__':
    # ~ output  = run_search(input())
    output  = run_search('murder')
    # ~ result_list_combiner(output)
    #pprint(output)
