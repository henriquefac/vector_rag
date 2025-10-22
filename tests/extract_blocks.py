from configPy import Config
import fitz

files_dir = Config.get_dir_files()


from dataclasses import dataclass


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
                {self.lines}
----------  FIM  ---------
        """


# PASTA DE ARQUIVOS
manual_dir = files_dir["ChatCorregedoria"]["ManualProcedimentoCartorarios"]

# PASTA OUTPUT DE ARQUIVOS BLOCOS

output_blocks_dir = files_dir.create_dir("output").create_dir("extracted_blocks")

# LISTA DE ARQUIVOS

list_files = [pdf for pdf in manual_dir.iter_files() if pdf.suffix == ".pdf"]


# ESTRUTURA DE UM BLOCO


# FUNÇÂO PARA EXTRAIR BLOCOS DE UMA PÁGINA


def extract_blocks_from_pages(page: fitz.Page) -> list[Block]:
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


if __name__ == "__main__":
    file_test = list_files[4]
    print(f"Arquivo de teste: {file_test}")

    with fitz.open(file_test) as doc:
        for i, page in enumerate(doc):
            blocks = extract_blocks_from_pages(page)
            print(f"\n--- Página {i+1} ---")
            for b in blocks:  # mostrar só os 5 primeiros blocos
                print(b)
