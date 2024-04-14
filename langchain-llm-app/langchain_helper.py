import os
from typing import List

from dotenv import load_dotenv
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import YoutubeLoader
from langchain_community.vectorstores import FAISS  # Similary search lirary
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.llms import OpenAI

load_dotenv()

embeddings = OpenAIEmbeddings()
llm = OpenAI(openai_api_key = os.getenv("OPENAI_API_KEY"))


def create_vector_db_from_url(video_url: str) -> FAISS:
    """
    Create a vector database from a video URL.
    :param video_url:
    :return db:
    """

    loader: YoutubeLoader = YoutubeLoader.from_youtube_url(video_url)
    videoText = loader.load()  # load text

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50,
    )

    # Split text into chunks
    docs: List[Document] = text_splitter.split_documents(videoText)

    # Create embeddings
    database: FAISS = FAISS.from_documents(documents = docs, embedding = embeddings)

    return database


def get_response_from_query(db: FAISS, query: str, output_language: str, k = 4) -> str:
    """
     Get response from query and force llm to give answer based on that data
    :param db:
    :param query: user query
    :param output_language: RO/EN/FR etc
    :param k: number of documents to extract
    :return:
    """
    template = """
            You will answer questions based on the transcript given to you based on a video. Answer the
            following question: {question} by only using the following data: {docs}
            If you don't know an answer, say I don't know, don't search data anywhere else other than the given data.
            If the data doesnt match the question or it doesn't really relate to the text, say that it doesnt match the question.
            I want the output to be written in {output_language}
    """

    prompt = PromptTemplate(template = template, input_variables = ["question", "docs", "output_language"])

    docs: List[Document] = db.similarity_search(query, k = k)
    docs_page_content = " ".join([doc.page_content for doc in docs])  # unite the b docs into 1 big query

    chain: LLMChain = LLMChain(llm = llm, prompt = prompt)
    # Get response from llm
    response = chain.run(question = query, docs = docs_page_content, output_language = output_language)
    return response

