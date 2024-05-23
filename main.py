from elasticsearch import Elasticsearch

# Crie uma instância do Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9292}])

# Dados do documento a ser indexado
doc = {
    'nome': 'John Doe222222',
    'profissao': 'Engenheiro de Software',
    'cidade': 'São Paulo',
    'pais': 'Brasil'
}

# Indexe o documento
res = es.index(index='teste-index', doc_type='doc', id=2, body=doc)

print(res['result'])
