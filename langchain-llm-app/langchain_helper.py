import os
from typing import List

from dotenv import load_dotenv
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import YoutubeLoader
from langchain_community.vectorstores import FAISS  # libarie de la fb pt similarity search ( alternativa la pinecone)
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.llms import OpenAI

load_dotenv()

embeddings = OpenAIEmbeddings()
llm = OpenAI(openai_api_key = os.getenv("OPENAI_API_KEY"))


def create_vector_db_from_url(video_url: str) -> FAISS:
    loader: YoutubeLoader = YoutubeLoader.from_youtube_url(video_url)
    videoText = loader.load()  # un document mare

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50,
    )

    docs: List[Document] = text_splitter.split_documents(videoText)

    database: FAISS = FAISS.from_documents(documents = docs, embedding = embeddings)

    return database


# k=4 because the model takes at max 4097 tokens so if we split by 1000 we can use 4 + a small query
def get_response_from_query(db: FAISS, query: str, output_language: str, k = 4) -> str:
    template = """
            You will answer questions based on the transcript given to you based on a video. Answer the
            following question: {question} by only using the following data: {docs}
            If you don't know an answer, say I don't know, don't search data anywhere else other than the given data.
            If the data doesnt match the question or it doesn't really relate to the text, say that it doesnt match the question.
            I want the output to be written in {output_language}
    """

    prompt = PromptTemplate(template = template, input_variables = ["question", "docs", "output_language"])

    chain: LLMChain = LLMChain(llm = llm, prompt = prompt)

    docs: List[Document] = db.similarity_search(query, k = k)

    for elem in docs:
        print(elem)
        print("\n")

    docs_page_content = " ".join([doc.page_content for doc in docs])  # unite the four docs into 1 big query
    response = chain.run(question = query, docs = docs_page_content, output_language = output_language)
    print(response)
    return response


if __name__ == "langchain_helper":
    print("start")
