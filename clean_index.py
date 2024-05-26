from elasticsearch import Elasticsearch


def delete_index(es_host, index_name: str) -> dict:
    """
    Delete an index in Elasticsearch.
    
    :param es: An instance of Elasticsearch.
    :param index_name: The name of the index to delete.
    :return: The response from Elasticsearch.
    """
    
    es = Elasticsearch([es_host])
    
    if es.indices.exists(index=index_name):
        return es.indices.delete(index=index_name)
    else:
        return {"error": "Index does not exist"}

if __name__ == '__main__':    
    es_host = 'http://localhost:9292'  # Substitua pelo host do seu Elasticsearch
    
    index_name = 'teste-index2'
    response = delete_index(es_host, index_name)
    print(response)