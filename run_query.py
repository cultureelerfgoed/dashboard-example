from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import date, timedelta, datetime

nde_sparql = SPARQLWrapper(
    'https://datasetregister.netwerkdigitaalerfgoed.nl/sparql'
)
nde_sparql.setReturnFormat(JSON)

rce_sparql = SPARQLWrapper(
    'https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/datacatalog/services/datacatalog/sparql'
)
rce_sparql.setReturnFormat(JSON)


# gets the first 3 geological ages
# from a Geological Timescale database,
# via a SPARQL endpoint
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

# gets the first 3 geological ages
# from a Geological Timescale database,
# via a SPARQL endpoint
rce_sparql.setQuery('''
    PREFIX schema: <https://schema.org/>
    SELECT (count(distinct ?dataset) as ?count) WHERE {
    ?dataset schema:publisher <https://www.cultureelerfgoed.nl> .
    } '''
)

try:
    nde_q = nde_sparql.queryAndConvert()
    set_count_nde = nde_q['results']['bindings'][0]['count']['value']
    nde_str = f'{set_count_nde} sets op het NDE Datasetregister \n'

    rce_q = rce_sparql.queryAndConvert()
    set_count_rce = rce_q['results']['bindings'][0]['count']['value']
    rce_str = f'{set_count_rce} sets op de linked data voorziening van de RCE \n'

    with open("README.md", "w") as f:
        f.write('## Dataset dashboard: ')
        if set_count_nde == set_count_rce:
            f.write('alles OK \n')
        else:
            f.write('fout \n')
        f.write(nde_str)
        f.write(rce_str)
        f.write(f'Checked at {datetime.now()}')
        
except Exception as e:
    print(e)