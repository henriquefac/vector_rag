from src.chuncking.manual_proc_cart.schemas import (
    Section,
    Subsection,
    PDFDict,
    operations,
)
from src.chuncking.manual_proc_cart.schemas.operations import (
    is_section_header,
    is_subsection_header,
    is_title_block,
    get_block_text,
)


def extract_sections_and_subsections(pdf_dict: PDFDict, width: float) -> list[Section]:

    list_blocks = operations.mash_pdf_dict(pdf_dict)

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

            if not   isinstance(current_section, Section):
                raise ValueError("Não pode existir Subsection sem ter antes um 'Section'")
            
            if current_subsection:
                current_section.subsection.append(current_subsection)
                current_subsection = None

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
