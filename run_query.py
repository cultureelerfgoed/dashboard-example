""" module to query two sparql endpoints, compare them, and write to file """
from datetime import date, timedelta, datetime, timezone
from SPARQLWrapper import SPARQLWrapper, JSON

# colored images for state indicator, because github markdown does not support color
STATE = {
    'OK': '![#339900](https://placehold.co/5x5/339900/339900.png)',
    'FAIL': '![#f03c15](https://placehold.co/5x5/f03c15/f03c15.png)',
}

# nde datasetregister sparql endpoint
nde_sparql = SPARQLWrapper('https://datasetregister.netwerkdigitaalerfgoed.nl/sparql')
nde_sparql.setReturnFormat(JSON)
# query to count datasets on nde datasetregister published by rce and read within the last two days
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

# rce datacatalog sparql endpoint
rce_sparql = SPARQLWrapper('https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/datacatalog/services/datacatalog/sparql')
rce_sparql.setReturnFormat(JSON)
# query to count datasets in rce catalog
rce_sparql.setQuery(
    'PREFIX schema: <https://schema.org/>' \
    'SELECT (count(distinct ?dataset) as ?count) WHERE { ' \
    '?dataset schema:publisher <https://www.cultureelerfgoed.nl> . }' \
)

try:
    # query and get results from json structure
    nde_q = nde_sparql.queryAndConvert()
    set_count_nde = nde_q['results']['bindings'][0]['count']['value']
    rce_q = rce_sparql.queryAndConvert()
    set_count_rce = rce_q['results']['bindings'][0]['count']['value']

    # set color based on equal counts
    if set_count_nde == set_count_rce:
        status = STATE['OK']
    else:
        status = STATE['FAIL']

    # write to README
    with open('README.md', 'w', encoding='UTF8') as f:
        f.write('## Status <br /> \n')
        now_cet = (datetime.now(timezone.utc) + timedelta(hours=2)).replace(tzinfo=None)
        f.write(f'{status} [{now_cet:%Y-%m-%d %H:%M}] <b>{set_count_nde}/{set_count_rce}</b> datasets uit de datacatalog van de RCE beschikbaar op het NDE Datasetregister.  <br /> \n')
        
except OSError as e:
    print(e)