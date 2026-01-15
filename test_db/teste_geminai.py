from src.retriever.utils.queryEngine.query_engine_factory import (
    getHybridEngine,
)
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.mock import MockLLM
from llama_index.core import Settings
from llama_index.core.prompts import PromptHelper  # <<< Adicionado PromptHelper

import asyncio
import nest_asyncio

nest_asyncio.apply()

COLLECTION_NAME = "manual_cartorarios"
BASE_EMBEDDING = "http://localhost:11434"  # Corrigindo a URL
EMBEDDING_MODEL = "nomic-embed-text"

# Define um valor GRANDE para o contexto no PromptHelper
GRANDE_CONTEXT_WINDOW = 32768

embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL, base_url=BASE_EMBEDDING)
mock_llm = MockLLM()
Settings.llm = mock_llm  # Define o LLM para evitar erro de chave OpenAI
Settings.embed_model = embed_model

# 1. Cria o PromptHelper com a janela de contexto grande
# ESTE OBJETO FAZ O CÁLCULO QUE ESTÁ FALHANDO
prompt_helper = PromptHelper(
    context_window=GRANDE_CONTEXT_WINDOW,
    num_output=256,
)

# 2. Passa o prompt_helper para o factory
# ASSUMIMOS que o getHybridEngine usa este objeto para construir os componentes internos.
query_factory = getHybridEngine(
    COLLECTION_NAME, embed_model, prompt_helper=prompt_helper
)

query_engine = query_factory()


# O código de run_query permanece o mesmo...
async def run_query():
    # ...
    query_ptbr = "Quais são as condições de elegibilidade e inelegibilidade que precisam ser verificadas no momento do pedido de registro de candidatura?"
    print(f"Buscando por: **{query_ptbr}**")
    response = await query_engine.aquery(query_ptbr)
    print("\n--- RESPOSTA ---")
    print(str(response))
    print("----------------")


if __name__ == "__main__":
    asyncio.run(run_query())
