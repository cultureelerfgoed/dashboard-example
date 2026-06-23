from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import date, timedelta, datetime

STATE = {
    'OK': '![#339900](https://placehold.co/5x5/339900/339900.png)',
    'WARNING': '![#ec942c](https://placehold.co/5x5/ec942c/ec942c.png)',
    'FAIL': '![#f03c15](https://placehold.co/5x5/f03c15/f03c15.png)',
}

nde_sparql = SPARQLWrapper('https://datasetregister.netwerkdigitaalerfgoed.nl/sparql')
nde_sparql.setReturnFormat(JSON)

rce_sparql = SPARQLWrapper('https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/datacatalog/services/datacatalog/sparql')
rce_sparql.setReturnFormat(JSON)

# query to count datasets on nde datasetregister published by rce and read recently
nde_sparql.setQuery(
    'PREFIX dct: <http://purl.org/dc/terms/>' \
    'PREFIX schema: <https://schema.org/>' \
    'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>' \
    'SELECT (count(distinct ?dataset) as ?count) WHERE {' \
    '?dataset dct:publisher <https://www.cultureelerfgoed.nl> .' \
    '?dataset schema:dateRead ?date .' \
    f'FILTER (?date > "{date.today() - timedelta(days=2)}T00:00:00+00:00"^^xsd:dateTime) .' \
    '} ' 
)

# query to count datasets in rce catalog
rce_sparql.setQuery('''
    PREFIX schema: <https://schema.org/>
    SELECT (count(distinct ?dataset) as ?count) WHERE {
    ?dataset schema:publisher <https://www.cultureelerfgoed.nl> .
    } '''
)

try:
    nde_q = nde_sparql.queryAndConvert()
    set_count_nde = nde_q['results']['bindings'][0]['count']['value']
    rce_q = rce_sparql.queryAndConvert()
    set_count_rce = rce_q['results']['bindings'][0]['count']['value']

    if set_count_nde == set_count_rce:
        status = STATE['OK']
    else:
        status = STATE['FAIL']

    with open("README.md", "w") as f:
        f.write(f'## Status <br /> \n')
        f.write(f'{status} [{datetime.now():%Y-%m-%d %H:%M.%S}] {set_count_nde}/{set_count_rce} datasets uit de datacatalog van de RCE beschikbaar op het NDE Datasetregister.  <br /> \n')
        
except Exception as e:
    print(e)