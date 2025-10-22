from configPy import Config
from fitz import Document, Page, TextPage
import fitz
from pathlib import Path
from collections import namedtuple

files_dir = Config.get_dir_files()


# PASTA DE ARQUIVOS
manual_dir = files_dir["ChatCorregedoria"]["ManualProcedimentoCartorarios"]

# PASTA OUTPUT DE ARQUIVOS BLOCOS

output_blocks_dir = files_dir.create_dir("output").create_dir("extracted_blocks")

# LISTA DE ARQUIVOS

list_files = [pdf for pdf in manual_dir.iter_files() if pdf.suffix == ".pdf"]


# ESTRUTURA DE UM BLOCO
Block = namedtuple("Block", ["x0", "y0", "x1", "y1", "lines", "number", "type"])


# FUNÇÂO PARA EXTRAIR BLOCOS DE UMA PÁGINA


def extract_blocks_from_pages(page: Page):
    # extrair textpage
    textpage: TextPage = page.get_textpage()
    # extrair blocos
    blocks = [Block(*b) for b in textpage.extractBLOCKS()]

    return blocks


# FUNÇÂO PARA ITERAR SOBRE AS PÁGINAS DE UM OBJETO 'doc'
# E DE CADA UMA, EXTRAIR LISTA DE BLOCOS


def get_blocks_by_pages(doc: Document):
    pages_dict = {}
    for i, page in enumerate(doc.pages()):
        pages_dict[i] = extract_blocks_from_pages(page)
    return pages_dict


def get_pdf_blocks(path: Path):
    # Gerar caminho do output

    pdf_dict: dict[int, list[Block]]

    with fitz.open(path) as doc:

        firs_page = doc[0]
        dim = firs_page.rect
        width = dim.width

        pdf_dict = get_blocks_by_pages(doc)

    return pdf_dict, width


# estrutura de um segmento do pdf
Segment = namedtuple("Segment", ["title", "list_blocks"])


# Filtrar para encontrar campo das referências normativas
def get_normative_references(dict_sections: dict[int, list[Block]]):
    # Procurar Block na ´agina 0 que possui em 'lines' o valor 'Referências Normativas\n'

    list_blocks = dict_sections[0]

    pointer = 0

    ref_nroms_pointer = -1

    section_1_pointer = -1

    this_block: Block

    while pointer < len(list_blocks):
        this_block = list_blocks[pointer]

        if "Referências Normativas\n" in this_block.lines:
            ref_nroms_pointer = pointer
        if "Seção I\n" in this_block.lines:
            section_1_pointer = pointer
        if ref_nroms_pointer > -1 and section_1_pointer > -1:
            ref_norms_segment = Segment(
                "Referências Normativas",
                list_blocks[ref_nroms_pointer + 1 : section_1_pointer],
            )
            # Nova página 0 com as informações removidas
            list_blocks = list_blocks[section_1_pointer:]
            dict_sections[0] = list_blocks

            return ref_norms_segment, dict_sections

        pointer += 1

    raise Exception("Erro ao procurar Referências Normativas")


# Depois de remover segmento das referências normativas, identificar os outros segmentos e onde começa e termia cada um
# def identiy_general_segments(dict_sctions: dict[int, ])


# Primeiro passo, fundir todas as páginas em uma únia lista
def mash_pages(dict_blocks_by_pages: dict[int, list[Block]]):
    list_all_blocks: list[Block] = []
    for i, list_blocks in dict_blocks_by_pages.items():
        list_all_blocks.extend(list_blocks)
    return list_all_blocks


# Identificar segmentos atravêz das márgens. Tudo que estiver entre campos marcados como 'seções' pertencem
# a seção anterior. Se acabar os blocos e ainda for identificado uma seção, tudo pertence a essa seção


def define_segments(list_blocks: list[Block], width):

    pointer = 0

    current_section_pointer: int = -1
    current_section_pointer_builder: int = -1
    continue_this_section_flag: bool = True

    current_block: Block
    x0: float
    x1: float

    left_margin: float
    right_margin: float

    segment_text: str
    segment_blocks: list[Block]

    while pointer < len(list_blocks):
        current_block = list_blocks[pointer]

        if current_block.lines.strip() == "\n":
            pointer += 1
            continue

        x0, x1 = current_block.x0, current_block.x1

        left_margin = x0 / width
        right_margin = (width - x1) / width

        is_it_segment = left_margin > 0.3 and right_margin > 0.3

        if is_it_segment and continue_this_section_flag:

            current_section_pointer = (
                pointer if not current_section_pointer else current_section_pointer
            )
            current_section_pointer_builder = pointer

            pointer += 1
            continue

        if not is_it_segment:
            continue_this_section_flag = False
            pointer += 1
            continue

        # se chegou até aqui, encontrou outro segmento
        # fechar segmento atual

        segment_text = "\n".join(
            [
                b.lines
                for b in list_blocks[
                    current_section_pointer:current_section_pointer_builder
                ]
            ]
        )
        segment_blocks = list_blocks[current_section_pointer_builder:pointer]

        current_section_pointer = pointer
        current_section_pointer_builder = pointer

        continue_this_section_flag = True

        pointer += 1

        yield Segment(segment_text, segment_blocks)

    if not continue_this_section_flag:
        segment_text = "\n".join(
            [
                b.lines
                for b in list_blocks[
                    current_section_pointer:current_section_pointer_builder
                ]
            ]
        )
        segment_blocks = list_blocks[current_section_pointer_builder:pointer]

        current_section_pointer = pointer
        current_section_pointer_builder = pointer

        yield Segment(segment_text, segment_blocks)


if __name__ == "__main__":
    file: Path = manual_dir.get_any(
        "Cap├нtulo IV_MPC CRE-CE_25-09-2025_Ordem Geral dos Servi├зos.pdf"
    )
    # file = list_files[1]
    print(f"--- Arquivo para teste: {file} ---")

    # extrair todos os blocos por página
    dict_all_blocks, width = get_pdf_blocks(file)

    norm, dict_all_blocks = get_normative_references(dict_all_blocks)
    print(norm)
