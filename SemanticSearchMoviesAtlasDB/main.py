import os

from dotenv import load_dotenv
from pymongo.collection import Collection
from pymongo.command_cursor import CommandCursor
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import requests
from pymongo.typings import _DocumentType

load_dotenv()

client: MongoClient = MongoClient(os.environ['MONGO_DB_URL'], server_api = ServerApi('1'))

hugging_face_token = os.environ['HUGGING_FACE_TOKEN']
embedding_url = os.environ['EMBEDDING_URL']


def generate_embedding(text: str) -> list[float]:
    response = requests.post(
        embedding_url,
        headers = {"Authorization": "Bearer " + hugging_face_token},
        json = {"inputs": text}
    )
    response.raise_for_status()
    return response.json()


def generateNewCollection() -> None:
    try:
        db = client.get_database("sample_mflix")
        collection = db.get_collection("movies")
        collName = "movies_modified"
        if not db.list_collection_names().__contains__(collName):
            newCollection: Collection[_DocumentType] = db.create_collection("movies_modified")
            for doc in collection.find({'plot': {"$exists": True}}).limit(50):
                doc['plot_embedding_hf'] = generate_embedding(doc['plot'])
                newCollection.insert_one(doc)
    except Exception as e:
        print(e)


def searchInDatabase(query: str, collection_name: Collection[_DocumentType]) -> CommandCursor[_DocumentType]:
    pipeline = [
        {
            "$vectorSearch": {
                "queryVector": generate_embedding(query),  # function that calls the hugging face api to gen embed
                "path": "plot_embedding_hf",  # column that is indexed
                "numCandidates": 100,
                "limit": 4,
                "index": "plot_semantic_search"  # index name
            }
        }
    ]
    return collection_name.aggregate(pipeline)


if __name__ == "__main__":
    # generateNewCollection()
    db = client.get_database("sample_mflix")
    collection = db.get_collection("movies_modified")

    ans: CommandCursor[_DocumentType] = searchInDatabase("dead characters", collection)

    for document in ans:
        print(f"Title: {document['title']}\nPlot: {document['plot']} \n\n")
