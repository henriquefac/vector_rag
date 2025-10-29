from src.chuncking.manual_proc_cart.schemas import PDFDict, Section, Block, operations
import re

# Padrão expecializado
NORMATIVE_PATTERN = re.compile(r"(?i)^(refer(ê|e)ncia(s)?|normativa(s)?)")


def get_normative_references(dict_pdf: PDFDict) -> Section:

    page_0_blocks = dict_pdf[0]

    pointer = 0
    ref_norm_pointer = 1
    section_1_pointer = -1
    this_block: Block

    while pointer < len(page_0_blocks):
        this_block = page_0_blocks[pointer]
        block_tex = this_block.lines

        is_norm_ref = re.match(NORMATIVE_PATTERN, block_tex)

        is_section = operations.is_section_header(this_block)

        if is_norm_ref:
            ref_norm_pointer = pointer

        if is_section:
            section_1_pointer = pointer

        if ref_norm_pointer > -1 and section_1_pointer > -1:

            ref_norm_segment = Section(
                title="Referências Normativas",
                themes=["Referências Normativas do documento"],
                content_blocks=page_0_blocks[ref_norm_pointer + 1 : section_1_pointer],
            )

            # alteração do objeto in place
            page_0_blocks = page_0_blocks[section_1_pointer:]
            dict_pdf[0] = page_0_blocks

            return ref_norm_segment
        pointer += 1

    raise Exception("Erro ao procurar Referências Normativas")
