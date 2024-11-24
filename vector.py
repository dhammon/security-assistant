#!/bin/python3
print("[+] Importing packages...")
from langchain_community.document_loaders import UnstructuredPDFLoader, UnstructuredExcelLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from os import walk

## Load Files
print("[+] Loading file(s)...")
data = []
files = next(walk('files'))[2]
for file in files:
    split_file = file.rsplit(".", 1)
    ext = split_file[-1]
    if ext in ["xls", "xlsx", "csv"]:
        print("[!] Adding file "+file)
        loader = UnstructuredExcelLoader(file_path="files/"+file)
        data.extend(loader.load())
    if ext in ["pdf"]:
        print("[!] Adding file "+file)
        loader = UnstructuredPDFLoader(file_path="files/"+file)
        data.extend(loader.load())


## Split text into chunks
print("[+] Chunking...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(data)
print(f"[!] Text split into {len(chunks)} chunks")

## Create vector database
print("[+] Creating vector database...")
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="nomic-embed-text"),
    collection_name="local-rag",
    persist_directory="db"
)

print("[+] Done!")
