from pathlib import Path
from configPy import Config
from fitz import Document, Page
import fitz

import re

from dataclasses import dataclass, field

files_dir = Config.get_dir_files()
# PASTA DE ARQUIVOS
manual_dir = files_dir["ChatCorregedoria"]["ManualProcedimentoCartorarios"]


# LISTA DE ARQUIVOS

list_files = [pdf for pdf in manual_dir.iter_files() if pdf.suffix == ".pdf"]


@dataclass
class Block:
    x0: float
    y0: float
    x1: float
    y1: float
    lines: str

    max_font_size: float | None = None
    is_bold: bool = False

    @classmethod
    def get(
        cls,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        lines: str,
        max_font: float,
        is_bold: bool,
    ):
        return cls(x0, y0, x1, y1, lines, max_font, is_bold)

    def __str__(self):
        return f"""
[x0 = {self.x0}, y0 = {self.y0}]
[x1 = {self.x1}, y1 = {self.y1}]
[max_font_size = {self.max_font_size}]
[is_bold = {self.is_bold}]
---------- TEXTO ---------
{self.lines}$
----------  FIM  ---------
        """


@dataclass
class Section:
    title: str

    themes: list[str] = field(default_factory=list)

    subsection: list["Subsection"] = field(default_factory=list)

    content_blocks: list[Block] = field(default_factory=list)

    def __str__(self):
        return f"""
title={self.title}, themes={", ".join(self.themes)}
========= CONTTEN_BLOCKS ===========
                {"\n\n".join([str(block) for block in self.content_blocks])}
        """


@dataclass
class Subsection:
    title: str

    themes: list[str] = field(default_factory=list)
    content_blocks: list[Block] = field(default_factory=list)


PDFDict = dict[int, list[Block]]

# -- Padrões de identificação --
SECTION_HEADER_PATTERN = re.compile(r"(?i)^se(ç|c)ão [IVLCDM]+\b")
SUBSECTION_HEADER_PATTERN = re.compile(r"(?i)^subse(ç|c)ão [IVXLCDM]+\b")


# OPERAÇÕES BÁSICAS DE EXTRAÇÃO


def extract_blocks_from_pages(page: Page) -> list[Block]:
    d = page.get_text("dict")
    blocks = []

    for block in d["blocks"]:
        if "lines" not in block:
            continue

        x0, y0, x1, y1 = block["bbox"]

        text_chunks = []
        max_font_size = 0
        bold_found = False

        for line in block["lines"]:
            for span in line["spans"]:
                text_chunks.append(span["text"])
                size = span["size"]
                flags = span["flags"]

                if size > max_font_size:
                    max_font_size = size
                if flags & 2:
                    bold_found = True

        full_text = "\n".join(text_chunks).strip()

        if not full_text or full_text == "\n":
            continue

        blocks.append(
            Block(
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                lines=full_text,
                max_font_size=max_font_size,
                is_bold=bold_found,
            )
        )
    return blocks


def get_blocks_by_page(doc: Document) -> PDFDict:
    pages_dict = {}

    for i, page in enumerate(doc.pages()):
        pages_dict[i] = extract_blocks_from_pages(page)
    return pages_dict


def get_pdf_blocks(path: Path):

    pdf_dict: PDFDict

    with fitz.open(path) as doc:

        first_page = doc[0]
        dim = first_page.rect
        width = dim.width

        pdf_dict = get_blocks_by_page(doc)

    return pdf_dict, width


def mash_pdf_dict(pdf_dict: PDFDict) -> list[Block]:

    list_blocks = []

    for list_b in pdf_dict.values():
        list_blocks.extend(list_b)

    return list_blocks


# -- Ferramentas para identificação e operação com texto --


def get_block_text(block: Block) -> str:
    return block.lines.strip()


def is_section_header(block: Block) -> bool:
    return bool(SECTION_HEADER_PATTERN.match(block.lines.strip()))


def is_subsection_header(block: Block) -> bool:
    return bool(SUBSECTION_HEADER_PATTERN.match(block.lines.strip()))


def is_title_block(block: Block, width: float) -> bool:

    x0, x1 = block.x0, block.x1
    left_margin = x0 / width
    right_margin = (width - x1) / width
    max_font = block.max_font_size

    is_centralized = left_margin > 0.25 and right_margin > 0.25
    right_font = 8 < max_font < 9

    is_title = is_centralized or right_font

    return is_title and not is_section_header(block) and not is_subsection_header(block)


# -------- identificar Referências Normativas ----------------


def get_normative_references(dict_pdf: PDFDict) -> tuple[Section, PDFDict]:
    """
    Busca o bloco de Referências Normativas e o conteúdo subsequente,
    removendo-o da página 0.
    """
    page_0_blocks = dict_pdf[0]

    pointer = 0
    ref_nroms_pointer = -1
    section_1_pointer = -1
    this_block: Block

    while pointer < len(page_0_blocks):
        this_block = page_0_blocks[pointer]
        if "Referências Normativas" in this_block.lines:
            print(this_block)
            ref_nroms_pointer = pointer
        # A detecção da Seção I serve como limite para a Referência Normativa
        if is_section_header(this_block) and "Seção I" in this_block.lines:
            print(this_block)
            section_1_pointer = pointer

        if ref_nroms_pointer > -1 and section_1_pointer > -1:
            # CORREÇÃO: Usar 'content_blocks' no construtor, que é onde a lista de Block deve ir
            ref_norms_segment = Section(
                title="Referências Normativas",
                themes=["Referẽncias normativas do documento"],
                content_blocks=page_0_blocks[ref_nroms_pointer + 1 : section_1_pointer],
            )

            # Nova página 0 com as informações removidas
            page_0_blocks = page_0_blocks[section_1_pointer:]
            dict_pdf[0] = page_0_blocks

            return ref_norms_segment, dict_pdf

        pointer += 1

    raise Exception("Erro ao procurar Referências Normativas")


def extract_sections_and_subsections(
    list_blocks: list[Block], width: float
) -> list[Section]:

    final_sections: list[Section] = []

    current_section: Section | None = None
    current_subsection: Subsection | None = None

    pointer = 0
    num_blocks = len(list_blocks)

    while pointer < num_blocks:
        block = list_blocks[pointer]

        # primeiro passo: Ignorar bloco em branco ou apenas com "\n"

        block_text = get_block_text(block)

        if len(block_text) == 0 or block_text == "\n":
            pointer += 1
            continue

        is_section = is_section_header(block)
        is_subsection = is_subsection_header(block)
        is_title = is_title_block(block, width)

        if is_section:

            if current_section:
                if current_subsection:
                    current_section.subsection.append(current_subsection)
                    current_subsection = None
                final_sections.append(current_section)

            current_section = Section(title=block_text)
            pointer += 1
            continue

        if is_subsection:

            if isinstance(current_subsection, Subsection):

                # Não pode existir subsection sem ter antes um current_section
                current_section.subsection.append(current_subsection)

            current_subsection = Subsection(title=block_text)
            pointer += 1
            continue

        if not isinstance(current_section, Section) and not isinstance(
            current_subsection, Subsection
        ):
            raise ValueError("Deve sempre ter pelo menos um 'Section' ou 'Subsection'")

        # ver se é title
        if is_title:

            if isinstance(current_subsection, Subsection):
                current_subsection.themes.append(block_text)
                pointer += 1
                continue

            current_section.themes.append(block_text)
            pointer += 1
            continue
        # a partir daqui, é texto normal, alocar para ou
        # current_section ou current_subsection
        if isinstance(current_subsection, Subsection):
            current_subsection.content_blocks.append(block)
            pointer += 1
            continue
        current_section.content_blocks.append(block)
        pointer += 1
        continue

    # caso ainda esteja montando um 'Subsection'
    if isinstance(current_subsection, Subsection):
        current_section.subsection.append(current_subsection)
    final_sections.append(current_section)

    return final_sections


if __name__ == "__main__":
    file_teste = list_files[4]
    print("Arquivo de teste para extração dos componentes")

    # começar pelas Referências Normativas
    # extrair pdf como dicionário de blocos
    pdf_dict_blocs, width = get_pdf_blocks(file_teste)

    print("Arquivo extraído como dicionário de blocos")
    print("Buscando Campo das referências normativas")

    norms, pdf_dict_blocs = get_normative_references(pdf_dict_blocs)

    print("--- Referências normativas ---\n")
    print(norms)
