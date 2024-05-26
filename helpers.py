
import hashlib
import os
import re
from typing import List


# Função para calcular o hash de um arquivo
def calculate_hash(filepath):
    try:
        with open(filepath, 'rb') as arquivo:
            conteudo = arquivo.read()
            return hashlib.sha256(conteudo).hexdigest()
    except Exception as e:
        print(f"Erro ao calcular hash do arquivo {filepath}: {str(e)}")
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

def find_cpfs(texto: List[str]) -> List[str]:
    cpfs = re.findall(r'\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11}', texto)
    cpfs_validos = [cpf for cpf in cpfs if valida_cpf(cpf)]
    return cpfs_validos

def index_to_es(es, index, doc_type, id, body):
    try:
        res = es.index(index=index, id=id, body=body, headers={'Content-Type': 'application/json'})
        return res['result']
    except Exception as e:
        print("Error index document:", e)
        
        

def generate_file_hashes(destination_path: str) -> List[str]:
    list_hashes = []

    for root, dirs, files in os.walk(destination_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                data = f.read()
                hash = hashlib.sha256(data).hexdigest()
                list_hashes.append((file_path, hash))
                
    # print(list_hashes)

    return list_hashes