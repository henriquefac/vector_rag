from src.retriever.multi_steep_querry import MultiStepQueryEngineWorkflow
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import StorageContext, VectorStoreIndex, Settings

from chromadb import HttpClient
import asyncio

COLLECTION_NAME = "manual_cartorarios"

# informações da llm
BASE_EMBEDDING = "http://10.10.0.99:11434"
EMBEDDING_MODEL = "nomic-embed-text"

LLM_MODEL = "llama3.2:3b"

embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL, base_url=BASE_EMBEDDING)

llm = Ollama(
    tempeture=1.2,
    context_window=3000,
    base_url=BASE_EMBEDDING,
    model=LLM_MODEL,
    request_timeout=120.0,
)

Settings.llm = llm

client = HttpClient(host="localhost", port=8000)
collections = client.get_or_create_collection(COLLECTION_NAME)

vector_store = ChromaVectorStore(chroma_collection=collections)
store_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    store_context=store_context,
    embed_model=embed_model,
)


async def main():
    w = MultiStepQueryEngineWorkflow(timeout=2000)

    # parâmetros da query
    num_steps = 3
    index_summary = "Usado para auxiliar na resposta de perguntas feitas por funcionários do Tribunal Regional Eleitoral"

    query_ptbr = "Quais são as condições de elegibilidade e inelegibilidade que precisam ser verificadas no momento do pedido de registro de candidatura?"

    result = await w.run(
        query=query_ptbr,
        collection_name=COLLECTION_NAME,
        index_summary=index_summary,
        num_steps=num_steps,
    )

    print(f"{"/"*20}RESULTADO FINAL{"/"*20}")
    print(f"Contexto do index: {index_summary}")
    print(f"Query do usuário: {query_ptbr}")
    print("RESPOSTA:")
    print(str(result))
    print(f"{"/"*20}SUBQUERYS CRIADAS{"/"*20}")
    sub_qa = result.metadata["sub_qa"]
    tuples = [(t[0], t[1].response) for t in sub_qa]

    print(f"{'/'*20}NODES POR SUBQUERY{'/'*20}")
    for i, (subquery, response) in enumerate(sub_qa, 1):
        print(f"\n>>> Subquery {i}: {subquery}\n")

        for j, node in enumerate(response.source_nodes, 1):
            text_preview = node.node.text[:300].replace("\n", " ") + "..."
            score = getattr(node, "score", "N/A")
            meta = node.node.metadata

            print(f"--- Node {j} ---")
            print(f"Score: {score}")
            print(f"Documento: {meta.get('document', 'desconhecido')}")
            print(f"Seção: {meta.get('section', 'N/A')}")
            print(f"Texto: {text_preview}")
            print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot run" in str(e):
            print("O loop assícrono já está rodando. Executando diretamente...")
            asyncio.get_event_loop().run_until_complete(main())
        else:
            raise e
