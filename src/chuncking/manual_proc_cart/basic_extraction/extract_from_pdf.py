from src.chuncking.manual_proc_cart.basic_extraction import extract_blocks_from_pages
from src.chuncking.manual_proc_cart.schemas import PDFDict
from fitz import Document
from pathlib import Path
import fitz


def get_pdf_blocks_by_page(doc: Document) -> PDFDict:
    pages_dict = {}

    for i, page in enumerate(doc.pages()):
        pages_dict[i] = extract_blocks_from_pages(page, i + 1)

    return pages_dict


def get_pdf_blocks(path: Path) -> tuple[PDFDict, float]:

    pdf_dict: PDFDict

    with fitz.open(path) as doc:

        first_page = doc[0]
        dim = first_page.rect
        width = dim.width

        pdf_dict = get_pdf_blocks_by_page(doc)

    return (pdf_dict, width)
