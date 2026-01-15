from llama_index.embeddings.ollama.base import BaseEmbedding
from llama_index.core.query_engine import BaseQueryEngine, RetrieverQueryEngine
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.retrievers.bm25 import BM25Retriever

from llama_index.core.schema import TextNode

from chromadb.api import ClientAPI

from typing import Callable

from .node_postprocess import ContextFormatterPostprocess, HashDeduplicationPostprocess


def getChromaEngine(
    collection_name: str,
    client: ClientAPI,
    embedding_model: BaseEmbedding,
    top_key=5,
) -> Callable[[], BaseQueryEngine]:
    collection = client.get_or_create_collection(collection_name)

    vector_store = ChromaVectorStore(chroma_collection=collection)
    store_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        store_context=store_context,
        embed_model=embedding_model,
    )

    default_postprocess = [
        HashDeduplicationPostprocess(),
        ContextFormatterPostprocess(),
    ]

    query_engine = index.as_query_engine(
        similarity_top_k=top_key, node_postprocessors=default_postprocess
    )

    def function():
        return query_engine

    return function


def getHybridEngine(
    collection_name: str,
    embedding_model: BaseEmbedding,
    base: str = "localhost",
    port: int = 8000,
    top_key: int = 5,
    bm25_wight: float = 0.5,
) -> Callable[[], BaseEmbedding]:

    client = HttpClient(host=base, port=port)
    collection = client.get_or_create_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    store_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        store_context=store_context,
        embed_model=embedding_model,
    )
    data = collection.get(include=["documents", "metadatas"])

    # Construa TextNodes para o BM25
    nodes = [
        TextNode(text=doc, metadata=meta)
        for doc, meta in zip(data["documents"], data["metadatas"])
        if doc  # evita documentos vazios
    ]

    # Popule o docstore com esses nodes
    index.docstore.add_documents(nodes)

    def hybrid_engine_factory() -> BaseEmbedding:
        vector_retriever = index.as_retriever(similarity_top_k=top_key)

        bm25_retriever = BM25Retriever.from_defaults(
            docstore=index.docstore,
            similarity_top_k=top_key,
        )

        hybrid_retriever = QueryFusionRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            mode="reciprocal_rerank",
            retriever_weights=[1 - bm25_wight, bm25_wight],
            similarity_top_k=top_key,
            use_async=True,
        )

        query_engine = RetrieverQueryEngine(retriever=hybrid_retriever)

        return query_engine

    return hybrid_engine_factory
