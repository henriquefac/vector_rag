# from src.retriever.multi_steep_querry import MultiStepQueryEngineWorkflow
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import StorageContext, VectorStoreIndex

from chromadb import HttpClient

COLLECTION_NAME = "manual_cartorarios"

# informações da llm
BASE_EMBEDDING = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"

embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL, base_url=BASE_EMBEDDING)

client = HttpClient(host="localhost", port=8000)
collections = client.get_or_create_collection(COLLECTION_NAME)

vector_store = ChromaVectorStore(chroma_collection=collections)
store_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    store_context=store_context,
    embed_model=embed_model,
)

# Cira um retriever que buscará os % nós mais similares
retriever = index.as_retriever(similarity_top_k=5)


query_ptbr = (
    "Quais são as condições de elegibilidade e inelegibilidade que precisam ser verificadas no momento do pedido de registro de candidatura?",
)


similar_nodes = retriever.retrieve(query_ptbr[0])

print(f"Resultados encontrados ({len(similar_nodes)}):")

# Iterar sobre os resultados para ver as informações e o score
for i, node_with_score in enumerate(similar_nodes):
    node = node_with_score.node
    print(f"\n--- Resultado {i+1} (Score: {node_with_score.score:.4f}) ---")
    print(f"Seção: {node.metadata.get('section')}")
    print(f"Normas Relacionadas: {node.metadata.get('norms')}")
    # Mostrar um trecho do texto
    print(f"Trecho: {node.text}...")

    # Operação de Filtragem (Exemplo: apenas se o score for alto)
    if node_with_score.score > 0.8:
        print("** Alta Relevância! **")
