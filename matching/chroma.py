from typing import Any, Dict, List
import chromadb
from google.cloud import firestore


class FirebaseClient:
    def __init__(self):
        self.client = firestore.Client()

    def get_collection_data(self, collection_name):
        collection_ref = self.client.collection(collection_name)
        return collection_ref.stream()


class ChromaDBClient:
    def __init__(self):
        self.client = chromadb.Client()

    def create_collection(self, name):
        return self.client.create_collection(name=name)

    def add_documents_to_collection(self, collection, ids, documents, metadatas):
        collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def query_collection(self, collection, query_texts, n_results):
        return collection.query(query_texts=query_texts, n_results=n_results)


class DataProcessor:
    @staticmethod
    def transform_data(data):
        ids, documents, metadatas = [], [], []
        for i, element in enumerate(data):
            data_ = element.to_dict()
            id_ = str(i)
            ids.append(id_)
            document = " ".join(data_.get("description", []))
            documents.append(document)
            metadatas.append({"type": "description"})
        return ids, documents, metadatas
    
    @staticmethod
    def get_tags_from_artists(artists_data: firestore.QuerySnapshot, count: int = 10) -> List[str]:
        tags_list = []
        for i, artist in enumerate(artists_data):
            if i >= count:
                break
            artist_data: Dict[str, Any] = artist.to_dict()
            tags_list.extend(artist_data.get("tags", []))
        return tags_list


class ResultsExporter:
    @staticmethod
    def export_results_to_csv(result_df, filename):
        result_df.to_csv(filename, index=False)
