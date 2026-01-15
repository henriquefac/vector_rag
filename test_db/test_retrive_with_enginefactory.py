from src.retriever.utils.queryEngine.query_engine_factory import (
    # getHybridEngine,
    getChromaEngine,
)
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.llms.mock import MockLLM
from llama_index.core import Settings

import asyncio
import nest_asyncio

nest_asyncio.apply()

COLLECTION_NAME = "manual_cartorarios"

# informações da llm
BASE_EMBEDDING = "localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"


embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL, base_url=BASE_EMBEDDING)

mock_llm = MockLLM()
Settings.llm = mock_llm
Settings.embed_model = embed_model

query_factory = getChromaEngine(COLLECTION_NAME, embed_model)

query_engine = query_factory()


async def run_query():
    """Função assíncrona para executar a busca."""

    query_ptbr = "Quais são as condições de elegibilidade e inelegibilidade que precisam ser verificadas no momento do pedido de registro de candidatura?"

    print(f"Buscando por: **{query_ptbr}**")

    # 3. Executa a busca
    # Usamos .aquery (assíncrono) pois é a forma padrão no LlamaIndex
    response = await query_engine.aquery(query_ptbr)

    # 4. Exibe o resultado
    print("\n--- RESPOSTA ---")
    print(str(response))
    print("----------------")


if __name__ == "__main__":
    # Garante que a função assíncrona seja executada
    asyncio.run(run_query())
