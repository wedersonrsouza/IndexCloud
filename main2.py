import os
import uuid
from typing import List, Tuple

from elasticsearch import Elasticsearch

from helpers import (calculate_hash, find_cpfs, generate_file_hashes,
                     index_to_es)
from index_docx import read_docx
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
            
    def update_file_path(self, hash: str, file_paths: List[str]) -> dict:
        try:
            return self.es.update(index=self.index, id=hash, body={"doc": {"path": file_paths}})
                
        except Exception as e:
            # print(f'\n\n\nError update file paths:\n {file_paths}')
            print(f'\n\nError: {e}')

    def index_files(self, directory: str, extensions: List[str]) -> List[str]:
        
        file_hashes = generate_file_hashes(directory)
        indexed_hashes = []

        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    print(f"Indexing file {file}")
                    try:
                        file_path = os.path.join(root, file)
                        hash = str(calculate_hash(file_path))
                        indexed = self.check_already_indexed(hash=hash)

                        if indexed['_shards']['successful'] >= 1:
                            print("\n\n\nFile already indexed, looking for duplicates...")
                            duplicate_files = [item for item in file_hashes if item[1] == hash]
                            duplicate_file_paths = [item[0] for item in duplicate_files]
                            self.update_file_path(hash=hash, file_paths=duplicate_file_paths)
                        else:
                            content = read_docx(file_path) if file.endswith('.docx') else extract_text_from_image_pdf(file_path)
                            if content:
                                cpfs = find_cpfs(content)
                                body = {
                                    'content': str(content),
                                    'entities': cpfs,
                                    'hash': hash,
                                    'path': [file_path]
                                }
                                result = index_to_es(es=self.es, index=self.index, doc_type='_doc', id=hash, body=body)
                                if result:
                                    indexed_hashes.append(hash)
                    except Exception as e:
                        print(f'\n\n\nError processing file {file}')
                        print(f'\n\n{e}')
        return indexed_hashes


if __name__ == '__main__':
    es_host = 'http://localhost:9292'
    indexer = Indexer(es_host=es_host, index_name='teste-index2')
    indexer.index_files(directory='.\\dados', extensions=['.doc', '.docx', '.pdf'])
