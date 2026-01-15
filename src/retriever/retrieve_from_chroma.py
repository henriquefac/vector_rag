# emcapsula tudo necessário para realizar
# busca em cima de um banco db do chroma

from .utils.queryEngine import getChromaEngine
from .utils import EngineWraper
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.llms.mock import MockLLM

from chromadb.api import ClientAPI

from llama_index.core import Settings

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChromaVectorRetrieverFactory:

    collection_name: str
    chroma_client: ClientAPI
    # função para buscar configurar e criar querye engine
    # utilizando Ollama como embedding model

    @classmethod
    def get(cls, collection_name: str, chroma_client: ClientAPI):
        return cls(collection_name, chroma_client)

    def get_ollama_egine(
        self,
        base_embedding_url: str,
        embedding_model: str,
        llm_model: Optional[str] = None,
        top_key: int = 5,
    ) -> EngineWraper:

        embed_model = OllamaEmbedding(
            model_name=embedding_model,
            base_url=base_embedding_url,
        )

        # provisório
        if llm_model is None:
            llm = MockLLM()
        else:
            raise Exception(
                "Por enquanto não é implementação para suporte do uso de LLMs. Deixe esse campo vazio"
            )

        Settings.llm = llm
        Settings.embed_model = embed_model

        query_factory = getChromaEngine(
            collection_name=self.collection_name,
            client=self.chroma_client,
            embedding_model=embed_model,
            top_key=5,
        )
        query_engine = query_factory()

        return EngineWraper.wrape(query_engine)
