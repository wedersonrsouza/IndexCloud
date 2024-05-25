import os
import uuid

from elasticsearch import Elasticsearch

from helpers import calcular_hash, encontra_cpfs, index_to_es
from index_docx import read_docx
from index_pdf import extract_text_from_image_pdf


def main():
    index = 'teste-index2'  # Substitua pelo nome do seu índice
    doc_type = '_doc'  # Tipo de documento, geralmente '_doc' em versões recentes do Elasticsearch
    
    extensions_list = ['.doc', '.docx', '.pdf']
    

    for root, dirs, files in os.walk('.\\dados'):
        for file in files:
                try:
                    # id = str(uuid.uuid4())  # ID do documento
                    
                    content = None
                    file_path = os.path.join(root, file)
                
                    hash = str(calcular_hash(file_path))
                    
                    
                    if file.endswith('.docx'):
                        # Ler o arquivo DOCX
                        content = read_docx(file_path)
                    
                    if file.endswith('.pdf'):
                        content = extract_text_from_image_pdf(file_path)
                        
                        
                    if content:
                        lista_cpfs = encontra_cpfs(content)
                        # lista_nomes = encontra_nomes(content)

                        # print(lista_nomes)

                        body = {
                            'content': str(content),
                            'entidades': lista_cpfs,
                            'hash': hash,
                            'caminho': str(file_path)
                        }
                        
                        # Indexar o conteúdo no Elasticsearch
                        result = index_to_es(es=es, index=index, doc_type=doc_type, id=hash, body=body)


                        print(f'Resultado da indexação: {result}')

                except Exception as e:
                    print(f'\n\n\nError ao processar o arquivo {file}')
                    print(f'\n\n{e}')
                    


if __name__ == '__main__':
    es_host = 'http://localhost:9292'  # Substitua pelo host do seu Elasticsearch

    # Conectar ao Elasticsearch
    es = Elasticsearch([es_host])

    # # Obtenha a lista de todos os índices
    # all_indices = es.indices.get_alias("*").keys()

    # # Apague todos os índices
    # for index in all_indices:
    #     es.indices.delete(index=index)

    main()
