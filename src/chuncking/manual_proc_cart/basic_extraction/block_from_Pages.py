from fitz import Page
from src.chuncking.manual_proc_cart.schemas import Block


def extract_blocks_from_pages(page: Page, numPage: int) -> list[Block]:
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
                page=numPage,
                max_font_size=max_font_size,
                is_bold=bold_found,
            )
        )

    return blocks
