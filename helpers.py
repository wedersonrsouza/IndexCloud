
import hashlib
import os
import re


# Função para calcular o hash de um arquivo
def calcular_hash(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'rb') as arquivo:
            conteudo = arquivo.read()
            return hashlib.sha256(conteudo).hexdigest()
    except Exception as e:
        print(f"Erro ao calcular hash do arquivo {caminho_arquivo}: {str(e)}")
        return None
    
    
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

def index_to_es(es, index, doc_type, id, body):
    try:
        res = es.index(index=index, id=id, body=body, headers={'Content-Type': 'application/json'})
        return res['result']
    except Exception as e:
        print("Erro ao indexar documento:", e)
        
        
def verificar_arquivos(lista_de_arquivos):
    lista_de_arquivos[:] = [arquivo for arquivo in lista_de_arquivos if os.path.exists(arquivo)]
    return lista_de_arquivos


def gerar_hash_arquivos(diretorio):
    lista_hashes = []

    for root, dirs, files in os.walk(diretorio):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                data = f.read()
                hash = hashlib.sha256(data).hexdigest()
                lista_hashes.append((file_path, hash))
                
    # print(lista_hashes)

    return lista_hashes