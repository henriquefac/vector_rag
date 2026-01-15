from src.retriever import ChromaVectorRetrieverFactory
from chromadb import HttpClient


COLLECTION_NAME = "manual_cartorarios"
# informações da llm
BASE_EMBEDDING = "localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"


client = HttpClient()

chromaFactory = ChromaVectorRetrieverFactory.get(COLLECTION_NAME, client)
chromaOllamaEngine = chromaFactory.get_ollama_egine(BASE_EMBEDDING, EMBEDDING_MODEL)

query_ptbr = "Quais são as condições de elegibilidade e inelegibilidade que precisam ser verificadas no momento do pedido de registro de candidatura?"

response = chromaOllamaEngine.get_full_context_by_query(query_ptbr)
print(response["context"])
