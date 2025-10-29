from .schemas import Section
from .basic_extraction import get_pdf_blocks
from .components_extraction import (
    get_normative_references,
    get_name_from_manual,
    extract_sections_and_subsections,
)

from .merge_blocks import merge_content_blocks
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ChunkManual:

    text: str

    # metadados

    document_origin: str | None

    section_origin: str | None

    subsection_origin: str | None

    themes: list[str] = field(default_factory=list)

    related_norms: list[str] = field(default_factory=list)

    @classmethod
    def getChunk(
        cls,
        text: str,
        document_origin: str | None,
        section_origin: str | None,
        subsection_origin: str | None,
        themes: list[str] = [],
        norms: list[str] = [],
    ):
        related_norms = [n for n in norms if n in text]

        header = []

        if document_origin:
            header.append(document_origin)
        if themes:
            header.extend(themes)

        final_text = f"{"-".join(header)}\n\n{text}"

        return cls(
            text=final_text,
            document_origin=document_origin,
            section_origin=section_origin,
            subsection_origin=subsection_origin,
            themes=themes,
            related_norms=related_norms,
        )


@dataclass
class Manual:

    # Título do Manual
    title: str

    # Referências Normativas
    normRef: Section

    # Conteúdo do Manual (Lista dos blocos)
    content: list[Section] = field(default_factory=list)

    @classmethod
    def create_from_pdf(cls, pdf: Path):
        pdf_dict, width = get_pdf_blocks(pdf)

        # procurar nome
        name = get_name_from_manual(pdf_dict)

        # buscar
        norm = get_normative_references(pdf_dict)

        listSection = [
            merge_content_blocks(sec)
            for sec in extract_sections_and_subsections(pdf_dict, width)
        ]

        return cls(name, norm, listSection)

    def get_norm_ref(self):
        norms = self.normRef

        conteudo = norms.content_blocks

        contet_text = "---".join(
            [b.lines.replace("\n", "---").strip() for b in conteudo]
        )

        return contet_text.split("---")

    def get_chunks(self):

        doc_name = self.title
        themes = []

        for section in self.content:
            title_section = section.title
            themes_section = section.themes

            themes = []

            if themes_section:
                themes.extend(themes_section)

            for b in section.content_blocks:
                yield ChunkManual.getChunk(
                    text=b.lines,
                    document_origin=doc_name,
                    section_origin=title_section,
                    subsection_origin=None,
                    themes=themes,
                    norms=self.get_norm_ref(),
                )

            subsections = section.subsection

            if len(subsections) < 1:
                continue

            for sub in subsections:
                title_subsection = sub.title
                themes_subsection = sub.themes

                if themes_subsection:
                    themes.extend(themes_subsection)

                for b in sub.content_blocks:
                    yield ChunkManual.getChunk(
                        text=b.lines,
                        document_origin=title_section,
                        section_origin=title_section,
                        subsection_origin=title_subsection,
                        themes=themes,
                        norms=self.get_norm_ref(),
                    )

    def get_chunks_by_window(self, window_size: int = 2, overlap_size: int = 1):

        if overlap_size >= window_size:
            overlap_size = window_size - 1

            if overlap_size < 0:
                overlap_size = 0

        stride = window_size - overlap_size

        if stride < 1:
            stride = 1

        doc_name = self.title
        norms = self.get_norm_ref()

        for section in self.content:
            title_section = section.title

            themes = []

            if section.themes:
                themes.extend(section.themes)

            content_blocks = section.content_blocks
            len_content = len(section.content_blocks)

            for i in range(0, len_content - overlap_size, stride):
                window_blocks = content_blocks[i : i + window_size]

                if not window_size:
                    continue

                text = "\n\n".join([b.lines for b in window_blocks])

                yield ChunkManual.getChunk(
                    text=text,
                    document_origin=doc_name,
                    section_origin=title_section,
                    subsection_origin=None,
                    themes=themes,
                    norms=norms,
                )

            subsections = section.subsection

            if not subsections:
                continue

            for sub in subsections:
                title_subsection = sub.title
                themes_subsection = sub.themes

                if themes_subsection:
                    themes.extend(themes_subsection)

                sub_content_blocks = sub.content_blocks
                len_sub_content = len(sub_content_blocks)

                for i in range(0, len_sub_content - overlap_size, stride):
                    window_blocks = sub_content_blocks[i : i + window_size]

                    if not window_blocks:
                        continue

                    text = "\n\n".join([b.lines for b in window_blocks])

                    yield ChunkManual.getChunk(
                        text=text,
                        document_origin=doc_name,
                        section_origin=title_section,
                        subsection_origin=title_subsection,
                        themes=themes,
                        norms=norms,
                    )
