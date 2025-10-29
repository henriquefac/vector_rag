from src.chuncking.manual_proc_cart.schemas import PDFDict, operations
import re

TITLEPATTERN = re.compile(r"(?i)cap(í|i)tulo [IVLCDM]+")


def is_manual_title_block(block_text: str) -> bool:
    return bool(re.match(TITLEPATTERN, block_text))


def get_name_from_manual(pdf_dict: PDFDict) -> str:
    page_0 = pdf_dict[0]
    first_3 = page_0[:3]

    for block in first_3:

        block_text = operations.get_block_text(block)

        if is_manual_title_block(block_text):
            return block_text

    return operations.get_block_text(first_3[0])
