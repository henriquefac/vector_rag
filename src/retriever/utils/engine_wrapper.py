import asyncio
from dataclasses import dataclass
from llama_index.core.query_engine import BaseQueryEngine

# Necessário para rodar asyncio em contextos não-async (como scripts ou Jupyter)
import nest_asyncio

try:
    nest_asyncio.apply()
except Exception:
    pass


@dataclass
class EngineWraper:
    query_engine: BaseQueryEngine

    @classmethod
    def wrape(cls, engine: BaseQueryEngine) -> "EngineWraper":
        return cls(engine)

    async def aquery(self, query_ptbr: str):
        # O LlamaIndex usa .aquery() para chamadas assíncronas
        return await self.query_engine.aquery(query_ptbr)

    def query(self, query_ptbr: str):
        # Garante loop de eventos para rodar a tarefa assíncrona
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Roda a função assíncrona até a conclusão e retorna o resultado.
        return loop.run_until_complete(self.aquery(query_ptbr))

    def get_full_context_by_query(self, query_ptbr: str):
        response = self.query(query_ptbr=query_ptbr)

        context_ = []

        metadata = {}

        for source_node in response.source_nodes:
            # adicionar texto
            context_.append(source_node.text)

            for key, item in source_node.metadata.items():
                metadata.setdefault(key, set()).add(item)

        return {"context": "\n\n".join(context_), "metadata": metadata}
