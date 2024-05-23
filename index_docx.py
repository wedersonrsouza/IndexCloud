from docx import Document
from elasticsearch import Elasticsearch
import os
import uuid
import re
import spacy


def encontra_nomes(texto):
    # Carregue o modelo de linguagem português do spaCy
    nlp = spacy.load('pt_core_news_sm')

    # Processe o texto
    doc = nlp(texto)

    lista_nomes = []
    # Itere sobre as entidades e imprima as que são pessoas
    for entidade in doc.ents:
        if entidade.label_ == 'PER':
            # print(entidade.text)
            lista_nomes.append(entidade.text)

    return lista_nomes

def valida_cpf(cpf):
    cpf = [int(digit) for digit in cpf if digit.isdigit()]
    if len(cpf) != 11:
        return False
    for i in range(9, 11):
        value = sum((cpf[num] * ((i+1) - num) for num in range(0, i)))
        digit = ((10 * value) % 11) % 10
        if digit != cpf[i]:
            return False
    return True

def encontra_cpfs(texto):
    cpfs = re.findall(r'\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11}', texto)
    cpfs_validos = [cpf for cpf in cpfs if valida_cpf(cpf)]
    return cpfs_validos

def read_docx(file_path):
    doc = Document(file_path)
    result = ' '.join([p.text for p in doc.paragraphs])
    return result

def index_to_es(es, index, doc_type, id, body):
    res = es.index(index=index, doc_type=doc_type, id=id, body=body)
    return res['result']

def main():
    index = 'teste-index2'  # Substitua pelo nome do seu índice
    doc_type = '_doc'  # Tipo de documento, geralmente '_doc' em versões recentes do Elasticsearch


    for root, dirs, files in os.walk('.\\dados'):
        for file in files:
            if file.endswith('.docx'):

                try:

                    id = str(uuid.uuid4())  # ID do documento

                    file_path = root+'\\'+file

                    # Ler o arquivo DOCX
                    content = read_docx(file_path)

                    lista_cpfs = encontra_cpfs(content)
                    # lista_nomes = encontra_nomes(content)

                    # print(lista_nomes)

                    body = {
                        'content': content,
                        'entidades': lista_cpfs
                    }

                    # Indexar o conteúdo no Elasticsearch
                    result = index_to_es(es, index, doc_type, id, body)



                    print(f'Resultado da indexação: {result}')

                except:
                    print(f'Arquivo {file} nao indexado')


if __name__ == '__main__':
    es_host = 'localhost:9292'  # Substitua pelo host do seu Elasticsearch

    # Conectar ao Elasticsearch
    es = Elasticsearch([es_host])

    # Obtenha a lista de todos os índices
    all_indices = es.indices.get_alias("*").keys()

    # Apague todos os índices
    for index in all_indices:
        es.indices.delete(index=index)

    main()
