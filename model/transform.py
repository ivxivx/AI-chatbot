import os
import streamlit as st
from langchain_community.llms.huggingface_hub import HuggingFaceHub
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceInstructEmbeddings

from config import set_environment

set_environment()

@st.cache_resource
def load_model():
    # repo_id = "google/flan-t5-xxl"
    repo_id = "google/flan-t5-large"
    llm = HuggingFaceHub(repo_id=repo_id, model_kwargs={"max_length": 100, "temperature": 0.1, "max_new_tokens": 250})
    
    return llm

@st.cache_resource
def get_vectorstore(text_chunks):
    embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def extract_docs(uploaded_files):
    texts = ""
    for uploaded_file in uploaded_files:
        with open(uploaded_file.name, 'r') as file:
            texts = file.read()
    
    return texts

def extract_doc(filename):
    with open(os.path.dirname(__file__) + "/" + filename, 'r') as file:
        return file.read()

def chunk_texts(texts):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', ' ', ''],
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    text_chunks = text_splitter.split_text(texts)
    return text_chunks
    
def get_chain(vectorstore):
    llm = load_model()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=vectorstore.as_retriever(),
        memory=memory)

    return conversation_chain
