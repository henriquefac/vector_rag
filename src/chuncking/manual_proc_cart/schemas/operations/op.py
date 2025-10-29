# Operações com os scheps e tipos declarados nos arquivos do diretório
# 1 nível acima
from src.chuncking.manual_proc_cart.schemas import PDFDict, Block
import re

SECTION_HEADER_PATTERN = re.compile(r"(?i)^se(ç|c)ão [IVXLCDM]+\b")
SUBSECTION_HEADER_PATTERN = re.compile(r"(?i)^subse(ç|c)ão [IVXLCDM]+\b")


def mash_pdf_dict(pdf_dict: PDFDict) -> list[Block]:
    list_blocks = []

    for list_b in pdf_dict.values():
        list_blocks.extend(list_b)

    return list_blocks


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


def mergeBlocks(blocos: list[Block]):
    new_lines = "\n\n".join([b.lines for b in blocos])
    merge_block = blocos[0]
    merge_block.lines = new_lines

    return merge_block
