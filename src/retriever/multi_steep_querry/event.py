from llama_index.core.workflow import Event
from typing import Dict, List, Any
from llama_index.core.schema import NodeWithScore


class QueryMultiStepEvent(Event):
    """
    Event contendo os resultados de um processo de query multi-step

    Atributos:
        nodes (List[NodeWithScore]): Lista de nodes com seus scores (pontuação quanto a relevância) associados a si
        source_nodes (List[NodeWithScore]) : Lista de nodes fontes com seus valores se score associados
        final_response_metadata (Disc[str, Any]): Metadata associado a resposta final
    """

    nodes: List[NodeWithScore]
    source_nodes: List[NodeWithScore]
    final_response_metadata: Dict[str, Any]
