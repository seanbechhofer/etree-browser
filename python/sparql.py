from SPARQLWrapper import SPARQLWrapper, JSON
import logging

CACHE = {}
SPARQL = None

def setUp(args):
    global SPARQL
    SPARQL = SPARQLWrapper(args.endpoint)
    SPARQL.setReturnFormat(JSON)

def query(name=None, query=None):
    global CACHE, SPARQL
    # Check the cache to see if this named query is there. 
    if name in CACHE:
        # If it is, grab it from the cache.
        logging.debug('Query in cache')
        return CACHE[name]
    else:
        # If not, execute the query.
        logging.debug('Hitting endpoint')

        SPARQL.setQuery(query)
        results = SPARQL.query().convert()
        # If the name is non null, then cache it
        if name:
            CACHE[name] = results
    # return the results
    return results

def result_to_table(sparql_results):
    variables = sparql_results['head']['vars']
    results = {
        'vars': variables,
        'bindings': []
        }
    logging.debug(variables)
    for sparql_result in sparql_results['results']['bindings']:
        result = {}
        for v in variables:
            if v in sparql_result.keys():
                result[v] = sparql_result[v]['value']
        results['bindings'].append(result)
    return results
    



