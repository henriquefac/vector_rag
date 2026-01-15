from llama_index.core.indices.query.query_transform.base import (
    StepDecomposeQueryTransform,
)

from llama_index.core.query_engine import BaseQueryEngine
from llama_index.core.response_synthesizers import get_response_synthesizer

from llama_index.core.schema import NodeWithScore

from .event import QueryMultiStepEvent

from llama_index.core.schema import QueryBundle, TextNode
from llama_index.core.workflow import Context, Workflow, StartEvent, StopEvent, step

from llama_index.core import Settings
from llama_index.core.llms import LLM

from typing import cast, Dict, Any


from typing import Callable


class MultiStepQueryEngineWorkflow(Workflow):

    def combine_queries(
        self,
        query_bundle: QueryBundle,
        prev_reasoning: str,
        index_summary: str,
        llm: LLM,
        previous_queryes: list[str],
    ) -> QueryBundle:
        """Combinar querys usando StepDecomposeQueryTransform"""
        transform_metadata = {
            "raciocinio_anterior": prev_reasoning,
            "resumo_do_index": index_summary,
            "queryes_anteriores": "\n".join(f"- {q}" for q in previous_queryes),
        }
        return StepDecomposeQueryTransform(llm=llm)(
            query_bundle, metadata=transform_metadata
        )

    def default_stop_fn(self, stop_dict: Dict) -> bool:
        """Função de aprada para o multi-step query combiner"""
        query_bundle = cast(QueryBundle, stop_dict.get("query_bundle"))

        if query_bundle is None:
            raise ValueError("Response must be provided to stop function.")

        return "none" in query_bundle.query_str.lower()

    @step
    async def query_multistep(
        self, ctx: Context, ev: StartEvent
    ) -> QueryMultiStepEvent:
        """Executa o processo de multi-step query"""
        prev_reasoning = ""
        cur_response = None
        previous_querys = []
        should_stop = None
        cur_steps = 0

        final_response_metadata: Dict[str, Any] = {"sub_qa": []}

        text_chunks = []
        source_nodes = []

        query = ev.get("query")
        await ctx.store.set("query", ev.get("query"))

        llm = Settings.llm
        stop_fn = self.default_stop_fn

        num_steps = ev.get("num_steps")

        query_factory: Callable[[], BaseQueryEngine] = ev.get("query_factory")
        query_engine = query_factory()

        index_summary = ev.get("index_summary")

        while not should_stop:
            # verificar passos do multistep query
            if num_steps is not None and cur_steps >= num_steps:
                should_stop = True
                break
            elif should_stop:
                break

            updated_query_bundle = self.combine_queries(
                QueryBundle(query_str=query),
                prev_reasoning,
                index_summary,
                llm,
                previous_querys,
            )

            previous_querys.append(updated_query_bundle.query_str)
            print(f"Query criada para o passo - {cur_steps} é: {updated_query_bundle}")

            stop_dict = {"query_bundle": updated_query_bundle}
            if stop_fn(stop_dict):
                should_stop = True
                break

            cur_response = await query_engine.aquery(updated_query_bundle)

            # adicionar resposta atual para o construtor da resposta
            cur_qa_tex = (
                f"\nPergunta: {updated_query_bundle.query_str}\n"
                f"Resposta: {cur_response!s}"
            )
            text_chunks.append(cur_qa_tex)

            # adicionar nodes de fonte
            for source_node in cur_response.source_nodes:
                source_nodes.append(source_node)

            final_response_metadata["sub_qa"].append(
                (updated_query_bundle.query_str, cur_response)
            )

            prev_reasoning += (
                f"- {updated_query_bundle.query_str}\n" f"- {cur_response!s}\n"
            )
            cur_steps += 1
        nodes = [
            NodeWithScore(node=TextNode(text=text_chunk)) for text_chunk in text_chunks
        ]

        return QueryMultiStepEvent(
            nodes=nodes,
            source_nodes=source_nodes,
            final_response_metadata=final_response_metadata,
        )

    @step
    async def synthesize(self, ctx: Context, ev: QueryMultiStepEvent) -> StopEvent:
        """Sintetizar a resposta"""
        response_synthesizer = get_response_synthesizer()
        query = await ctx.store.get("query", default=None)
        final_response = await response_synthesizer.asynthesize(
            query=query,
            nodes=ev.nodes,
            additional_source_nodes=ev.source_nodes,
        )
        final_response.metadata = ev.final_response_metadata

        return StopEvent(result=final_response)
