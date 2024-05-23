import os
import streamlit as st
from langchain_community.llms.huggingface_hub import HuggingFaceHub
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain import PromptTemplate
from transformers import AutoTokenizer, TextStreamer, pipeline
from auto_gptq import AutoGPTQForCausalLM
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline

from config import set_environment

set_environment()

@st.cache_resource
def load_model():
    # repo_id = "google/flan-t5-xxl"
    # repo_id = "google/flan-t5-large"
    # repo_id = "TheBloke/Llama-2-13B-chat-GPTQ"
    # llm = HuggingFaceHub(repo_id=repo_id, model_kwargs={"max_length": 100, "temperature": 0.1, "max_new_tokens": 250})
    
    model_name_or_path = "TheBloke/Llama-2-13B-chat-GPTQ"
    model_basename = "model"

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)

    model = AutoGPTQForCausalLM.from_quantized(
        model_name_or_path,
        revision="gptq-4bit-128g-actorder_True",
        model_basename=model_basename,
        use_safetensors=True,
        trust_remote_code=True,
        inject_fused_attention=False,
        device="cpu",
        quantize_config=None,
    )

    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    text_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=1024,
        temperature=0,
        top_p=0.95,
        repetition_penalty=1.15,
        streamer=streamer,
    )

    llm = HuggingFacePipeline(pipeline=text_pipeline, model_kwargs={"temperature": 0})

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

def generate_prompt(prompt: str, system_prompt: str) -> str:
    return f"""
        [INST] <>
        {system_prompt}
        <>

        {prompt} [/INST]
        """.strip()

def get_chain(vectorstore):
    llm = load_model()
    # memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    # conversation_chain = ConversationalRetrievalChain.from_llm(
    #     llm=llm, 
    #     retriever=vectorstore.as_retriever(),
    #     memory=memory)

    # return conversation_chain

    # 2024-05-18 question: talk about yourself; bot only returns hobbies.
    SYSTEM_PROMPT = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
    If you were asked about yourself, you should answer with your name, hobbies and latest work experience based on the context below. If you were asked with other questions, you should answer based on the context below"""

    template = generate_prompt(
        """
    {context}

    Question: {question}
    """,
        system_prompt=SYSTEM_PROMPT,
    )
  
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    return qa_chain
