import os

import requests
from dotenv import load_dotenv
from pymongo.collection import Collection
from pymongo.command_cursor import CommandCursor
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.typings import _DocumentType as DocType

load_dotenv()

client: MongoClient = MongoClient(os.environ['MONGO_DB_URL'], server_api = ServerApi('1'))

hugging_face_token = os.environ['HUGGING_FACE_TOKEN']
embedding_url = os.environ['EMBEDDING_URL']


def generate_embedding(text: str) -> list[float]:
    """
    Generates embedding for given text using the hugging face api:
    :param text: User input
    :return: list of embeddings
    """

    response = requests.post(
        embedding_url,
        headers = {"Authorization": "Bearer " + hugging_face_token},
        json = {"inputs": text}
    )
    response.raise_for_status()
    return response.json()


def generateNewCollection(dName: str, cName: str, newCName: str, colToSearch: str, embedding_column_name: str) -> None:
    """
    Generates new collection for given collection name and new column name.
    :param dName: Database name
    :param cName: Collection name
    :param newCName: New Collection name
    :param colToSearch: Column to search for
    :param embedding_column_name:  Column to add with embedding
    :return:
    """

    try:
        db = client.get_database(dName)
        collection = db.get_collection(cName)
        collName = newCName
        if not db.list_collection_names().__contains__(collName):
            newCollection: Collection[DocType] = db.create_collection(newCName)
            for doc in collection.find({colToSearch: {"$exists": True}}).limit(50):
                doc[embedding_column_name] = generate_embedding(doc[colToSearch])
                newCollection.insert_one(doc)
    except Exception as e:
        print(e)


def searchInDatabase(query: str, indexedColumnName: str, indexName: str, collection_name: Collection[DocType],
                     documentLimit: int = 4):
    """
    Searches given collection for given query and indexed column name and index name.
    :param query: User input eg. "outer space"
    :param indexedColumnName:  nane if the column that is indexed
    :param indexName:  name of the index for that column
    :param collection_name: name of the collection
    :param documentLimit (optional): output size
    :return:
    """
    pipeline = [
        {
            "$vectorSearch": {
                "queryVector": generate_embedding(query),  # function that calls the hugging face api to gen embed
                "path": indexedColumnName,  # column that is indexed
                "numCandidates": 100,
                "limit": documentLimit,
                "index": indexName  # index name
            }
        }
    ]
    return collection_name.aggregate(pipeline)


def printOutput(answer: CommandCursor[DocType]):
    for document in answer:
        print(f"Title: {document['title']}\nPlot: {document['plot']} \n\n")


if __name__ == "__main__":
    generateNewCollection(dName = "sample_mflix", cName = "movies", newCName = "movies_modified", colToSearch = "plot",
                          embedding_column_name = "plot_embedding_hf")
    db = client.get_database("sample_mflix")
    collection = db.get_collection("movies_modified")

    ans: CommandCursor[DocType] = searchInDatabase(query = "dead characters",
                                                   indexedColumnName = "plot_embedding_hf",
                                                   indexName = "plot_semantic_search",
                                                   collection_name = collection)

    printOutput(ans)
