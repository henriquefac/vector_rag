from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Document
from chromadb import HttpClient

from configPy import EnvManager

import hashlib

from configPy import Config
from src.chuncking.manual_proc_cart import Manual

openai_env = EnvManager.openai_env()

AZURE_API_KEY = openai_env.AZURE_API_KEY
AZURE_API_BASE = openai_env.AZURE_API_BASE
AZURE_API_VERSION = openai_env.AZURE_API_VERSION

EMBEDDING_MODEL = openai_env.EMBEDDING_MODEL
LLM_MODEL = openai_env.MODEL_NAME


COLLECTION_NAME = "manual_cartorarios"


# arquivos
files_dir = Config.get_dir_files()
manual_dir = files_dir["ChatCorregedoria"]["ManualProcedimentoCartorarios"]
list_files_manual = [f for f in manual_dir.list_files().values() if f.suffix == ".pdf"]

# Modelo de embedding

embed_model = AzureOpenAIEmbedding(
    model=EMBEDDING_MODEL,
    deployment_name=EMBEDDING_MODEL,
    api_key=AZURE_API_KEY,
    azure_endpoint=AZURE_API_BASE,
    api_version=AZURE_API_VERSION,
)


# cliente chromadb
client = HttpClient(host="localhost", port=8000)
collections = client.get_or_create_collection(COLLECTION_NAME)

# llamaIndex
vector_store = ChromaVectorStore(chroma_collection=collections)
store_context = StorageContext.from_defaults(vector_store=vector_store)


existing_data = collections.get(include=["metadatas"])
existing_ids = set()

if existing_data and "metadatas" in existing_data:
    for meta in existing_data["metadatas"]:
        if meta and "chunk_id" in meta:
            existing_ids.add(
                meta["chunk_id"]
            )  # Criar lista de Documents a partir dos chunks

documents: list[Document] = []

for file in list_files_manual:
    # particionar documentos
    manual = Manual.create_from_pdf(file)

    # Extrair chunks
    for chunk in manual.get_chunks_by_window(window_size=3, overlap_size=1):
        hasher = hashlib.sha256()
        hasher.update(chunk.text.encode("utf-8"))

        chunk_id = hasher.hexdigest()

        if chunk_id in existing_data:
            continue

        documents.append(
            Document(
                text=chunk.text.strip(),
                metadata={
                    "chunk_id": chunk_id,
                    "document": chunk.document_origin,
                    "section": chunk.section_origin,
                    "subsection": chunk.subsection_origin,
                    "norms": chunk.get_norms(),
                },
            )
        )

# criar indexes
for i, doc in enumerate(documents):
    if not isinstance(doc.metadata.get("norms"), str):
        # O SEU CÓDIGO DE DEBUG ESTÁ AQUI
        print(f"//////////////////////DOCUMENTO {i+1}/////////////////////")
        print(doc)
        print(f"Metadado 'norms' (Valor): {doc.metadata.get('norms')}")
        # Adicione este print para verificar o tipo:
        print(f"Metadado 'norms' (Tipo): {type(doc.metadata.get('norms'))}")

index = VectorStoreIndex.from_documents(
    documents=documents, storage_context=store_context, embed_model=embed_model
)
