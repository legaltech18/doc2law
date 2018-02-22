"""
Use Whoosh index files to find law section
"""
#!/usr/bin/env python

from whoosh.qparser import QueryParser
from whoosh.lang.porter import stem
from whoosh.lang.morph_en import variations
from whoosh.analysis import StemmingAnalyzer
import whoosh.index as index
import sqlite3


INDEX_DIR = 'db/index'
DATABASE_URL = "db/corpus.db"
TABLE_NAME = "law_text"

conn = sqlite3.connect(DATABASE_URL)
c = conn.cursor()

def get_full_law_para(law_title, para_num, matched):
    query = f"SELECT law_text from {TABLE_NAME} where law_name='{law_title}' and section='{para_num}'"
    all_text = ""
    for row in c.execute(query):
        text = row[0]
        if matched != text: 
            all_text += "\n"+text
        else:
            all_text += "\n <mark>"+text+"</mark>"
    return all_text
    
def search(query_input):
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
        query = QueryParser("matched", ix.schema).parse(query_input)
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
    
    
if __name__ == '__main__':
    from pprint import pprint
    output  = search(input())
    # ~ pprint(output['results'])
    pprint(output)
