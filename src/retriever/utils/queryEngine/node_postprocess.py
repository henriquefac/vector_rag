from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, TextNode, QueryBundle
from typing import List, Optional


class ContextFormatterPostprocess(BaseNodePostprocessor):

    def _postprocess_nodes(
        self, nodes: List[NodeWithScore], query_bundle: Optional[QueryBundle]
    ) -> List[NodeWithScore]:

        for node_with_score in nodes:
            meta = node_with_score.metadata
            original_text = node_with_score.text

            formatted_text = (
                f"[INFORMAÇÂO DE CONTEXTO - Documento: {meta.get("document", "Desconhecido")}]\n"
                f"[Seção: {meta.get('section', 'N/A')}]\n\n"
                f"{original_text}"
            )
            if isinstance(node_with_score.node, TextNode):
                node_with_score.node.set_content(formatted_text)
        return nodes


class HashDeduplicationPostprocess(BaseNodePostprocessor):
    def _postprocess_nodes(
        self, nodes: List[NodeWithScore], query_bundle: Optional[QueryBundle]
    ) -> List[NodeWithScore]:
        seen_ids = set()
        unique_nodes = []

        for node_with_score in nodes:
            chunk_id = node_with_score.metadata.get("chunk_id")
            if chunk_id and chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                unique_nodes.append(node_with_score)
            elif not chunk_id:
                unique_nodes.append(node_with_score)
        return unique_nodes
