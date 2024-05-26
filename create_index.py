from elasticsearch import Elasticsearch


def create_index(es_host, index_name: str) -> dict:
    """
    Cria um índice vazio no Elasticsearch.
    
    :param es: Uma instância do Elasticsearch.
    :param index_name: O nome do índice a ser criado.
    :return: A resposta do Elasticsearch.
    """
    es = Elasticsearch([es_host])
    
    if not es.indices.exists(index=index_name):
        return es.indices.create(index=index_name)
    else:
        return {"error": "Index already exists"}
    

if __name__ == '__main__':
    es_host = 'http://localhost:9292'  # Substitua pelo host do seu Elasticsearch
    index_name = 'teste-index2'
    response = create_index(es_host, index_name)
    print(response)