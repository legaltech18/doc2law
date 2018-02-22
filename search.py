"""
Use Whoosh index files to find law section
"""
#!/usr/bin/env python

from whoosh.qparser import QueryParser
from whoosh.lang.porter import stem
from whoosh.lang.morph_en import variations
from whoosh.analysis import StemmingAnalyzer
import whoosh.index as index

INDEX_DIR = 'db/en'

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
        query = QueryParser("content", ix.schema).parse(query_input)
        response['query'] = str(query)
        results = searcher.search(query)
        results_list = []
        if results:
            for r in results:
                content, law_title, para_n = r.values()
                if para_n == "":
                    para_n = None
                score = "{0:.2f}".format(r.score)
                results_list.append([content, law_title, para_n, score])
        response['results'] = results_list
    return response
if __name__ == '__main__':
    from pprint import pprint
    output  = search(input())
    # ~ pprint(output['results'])
    pprint(output)
