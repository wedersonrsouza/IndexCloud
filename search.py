from elasticsearch import Elasticsearch

# Crie uma instância do Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9292}])

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
