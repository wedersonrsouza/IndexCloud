import os
import uuid
from typing import List, Tuple

from elasticsearch import Elasticsearch

from clean_index import delete_index
from create_index import create_index
from helpers import (calculate_hash, find_cpfs, generate_file_hashes,
                     get_file_metadata, get_office_metadata, index_to_es)
from index_docx import read_docx
from index_imagens import extract_text_from_image
from index_pdf import extract_text_from_image_pdf


class Indexer:
    def __init__(self, es_host: str, index_name: str):
        self.es = Elasticsearch([es_host])
        self.index = index_name
        

    def check_already_indexed(self, hash: str) -> dict:
        try:
            query = {"query": {"match": {'hash': hash}}}
            return self.es.search(index=self.index, body=query)
        except Exception as e:
            print(f'Error check alread indexed file')
            print(e)
            
    def update_file_path(self, hash: str, file_paths: List[str]) -> dict:
        try:
            print('\n\n Atualizando arquivos duplicados no Elasticsearch')
            print(file_paths)
            
            result = self.es.update(index=self.index, id=hash, body={"doc": {"path": file_paths}})
            
            return result
                
        except Exception as e:
            # print(f'\n\n\nError update file paths:\n {file_paths}')
            print(f'\n\nError: {e}')

    def index_files(self, directory: str, extensions: List[str]) -> List[str]:
        
        # file_hashes = generate_file_hashes(directory)
        file_hashes = generate_file_hashes(directory, ['.doc', '.docx', '.xls', '.xlsx', '.pdf', '.png', '.jpg', '.jpeg'])
        
        print(file_hashes)
        
        indexed_hashes = []

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('appdata')]
            dirs[:] = [d for d in dirs if not d.startswith('admin')]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    
                    try:
                        file_path = os.path.join(root, file)
                        print(f"\n\n##### -> Indexing file {str(file_path)}")                        
                        
                        hash = str(calculate_hash(file_path)[1])
                        
                        indexed = self.check_already_indexed(hash=hash)
                        
                        if len(indexed['hits']['hits']) >= 1:
                            print(f"\n\n\nFile {file} already indexed, looking for duplicates...")
                            duplicate_files = [item for item in file_hashes if item[1] == hash]
                            
                            duplicate_file_paths = [item[0] for item in duplicate_files]
                            
                            self.update_file_path(hash=hash, file_paths=duplicate_file_paths)
                        
                        else:
                            
                            metadatas = None
                            
                            if any(file.endswith(ext) for ext in ['.doc', '.docx', '.xlsx']):
                                content = read_docx(file_path)
                                
                                metadatas = get_office_metadata(file_path)
                            elif any(file.endswith(ext) for ext in ['.pdf']):
                                content = extract_text_from_image_pdf(file_path)
                                
                                metadatas = get_file_metadata(file_path)
                                
                            # elif any(file.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.bmp']):
                            #     content = extract_text_from_image(file_path)
                            #     metadatas = get_file_metadata(file_path)
                                
                            
                            if content:
                                cpfs = find_cpfs(content)
                                body = {
                                    'content': str(content),
                                    'entities': cpfs,
                                    'hash': hash,
                                    'path': [file_path],
                                    'metadatas': metadatas
                                }
                                result = index_to_es(es=self.es, index=self.index, doc_type='_doc', id=hash, body=body)
                                indexed_hashes.append(hash)
                                
                                print("\n\n\nLooking for duplicates...")
                                duplicate_files = [item for item in file_hashes if item[1] == hash]
                                duplicate_file_paths = [item[0] for item in duplicate_files]
                                
                                self.update_file_path(hash=hash, file_paths=duplicate_file_paths)
                            
                    except Exception as e:
                        print(f'\n\n\nError processing file {file}')
                        print(f'\n\n{e}')
        return indexed_hashes


if __name__ == '__main__':
    es_host = 'http://elasticsearch:9200'
    index_name = 'vla_cloud'
    
    print(f'\n\nExcluindo indice {index_name}')
    response = delete_index(es_host, index_name)
    print(response)
    
    print(f'\n\nCriando novo indice {index_name}')
    response = create_index(es_host, index_name)
    print(response)
    
    indexer = Indexer(es_host=es_host, index_name=index_name)
    
    indexer.index_files(directory='/app/dados/', extensions=['.doc', '.docx', '.xls', '.xlsx', '.pdf'])
    # indexer.index_files(directory='.\\dados_imagens', extensions=['.png'])
