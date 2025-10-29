from src.chuncking.manual_proc_cart import ChunkManual
import hashlib
from typing import Dict, Any

# Assumindo que ChunkManual foi importada ou definida no mesmo arquivo
# from .manual_classes import ChunkManual


def format_chunk_for_chroma(
    chunk: "ChunkManual", index: int | None = None
) -> Dict[str, Any]:

    id_base = f"{chunk.document_origin or ''}-{chunk.section_origin or ''}-{chunk.text}"

    if index is not None:
        id_base = f"{index}-{id_base}"

    hash_object = hashlib.sha256(id_base.encode("utf-8"))
    unique_id = hash_object.hexdigest()[:32]  # 32 caracteres do hash para brevidade

    metadata = {
        "document_origin": chunk.document_origin,
        "section_origin": chunk.section_origin,
        "subsection_origin": chunk.subsection_origin,
        # Converte listas de strings para uma única string separada por vírgulas,
        # que é segura para o Chroma DB.
        "themes": ", ".join(chunk.themes) if chunk.themes else None,
        "related_norms": (
            ", ".join(chunk.related_norms) if chunk.related_norms else None
        ),
    }

    metadata_clean = {k: v for k, v in metadata.items() if v is not None}

    return {"id": unique_id, "document": chunk.text, "metadata": metadata_clean}
