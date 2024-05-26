
import hashlib
import os
import re
import time
from datetime import datetime, timezone
from typing import List

import docx
from docx.document import Document
from docx.opc.coreprops import CoreProperties
from openpyxl import load_workbook


def get_office_metadata(file_path: str) -> dict:
    
    metadata = get_file_metadata(file_path)
    
    if any(file_path.endswith(ext) for ext in ['.doc', '.docx']):
        doc = docx.Document(file_path)
        props:CoreProperties = doc.core_properties
        
        metadatas_doc = {str(p):getattr(props, p) for p in dir(props) if not str(p).startswith('_')}
        
        metadata.update(metadatas_doc)
        
    
    elif any(file_path.endswith(ext) for ext in ['.xls', '.xlsx']):
        wb = load_workbook(file_path)
        properties = wb.properties
        
        for attr in dir(properties):
            if not attr.startswith('__') and not callable(getattr(properties, attr)):
                value = getattr(properties, attr)
                if isinstance(value, (str, int, float, bool, type(None))):
                    metadata[attr] = value
                elif isinstance(value, datetime):
                    metadata[attr] = value.isoformat()
            
    return metadata
        
        
def get_file_metadata(file_path: str) -> dict:
    """
    Get metadata from a file.
    
    :param file_path: The path to the file.
    :return: A dictionary containing the file's metadata.
    """
    metadata = {}

    # Check if file exists
    if not os.path.isfile(file_path):
        return metadata

    # Get file size
    metadata['file_size'] = os.path.getsize(file_path)

    # Get file creation time
    creation_time = os.path.getctime(file_path)
    creation_time_utc = datetime.fromtimestamp(creation_time, timezone.utc).isoformat()
    metadata['file_creation_time'] = creation_time_utc

    # Get file last modification time
    modification_time = os.path.getmtime(file_path)
    modification_time_utc = datetime.fromtimestamp(modification_time, timezone.utc).isoformat()
    metadata['file_modification_time'] = modification_time_utc

    return metadata


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
                
    return list_hashes