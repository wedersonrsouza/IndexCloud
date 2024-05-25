from elasticsearch import Elasticsearch

es_host = 'http://localhost:9292'  # Substitua pelo host do seu Elasticsearch

# Conectar ao Elasticsearch
es = Elasticsearch([es_host])

# Defina a consulta de pesquisa
query = {"query": {"match_all": {}}}


# Execute a pesquisa
res = es.search(index='teste-index2', body=query)
#
# print(res['hits'])
# Imprima os resultados
for hit in res['hits']['hits']:
    print(hit)
    # print(hit['_source'])
