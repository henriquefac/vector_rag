from src.chuncking.manual_proc_cart.schemas import Block, Section, Subsection
from typing import Union
import re

# para cada bloco componente, identificar subtópicos pertencentes ao componente
# dentre os componentes de um 'Section' ou 'Subsection', caso o texto do bloco
# Não comece com <número>\.<número>, é um subtópico pertencente ao bloco anterior que atende
# a esse requisito

CONTENTPATTERN = re.compile(r"^\s*(\d+\.\d+|\d+\.\d+\.\d+)")


def merge_content_blocks(segment: Union[Section, Subsection]):
    content_blocks: list[Block] = segment.content_blocks

    if isinstance(segment, Section):
        subsections = segment.subsection
        if len(subsections) > 0:
            for sub in subsections:
                merge_content_blocks(sub)

    if len(content_blocks) <= 1:
        return

    merged_blocks: list[Block] = []
    current_main_block: Block = None

    for block in content_blocks:

        is_main_topic = bool(CONTENTPATTERN.match(block.lines.strip()))

        if is_main_topic or not current_main_block:

            if current_main_block:
                merged_blocks.append(current_main_block)

            current_main_block = block.model_copy()
            current_main_block.lines = block.lines

        else:
            current_main_block.lines += "\n\n" + block.lines

    if current_main_block:
        merged_blocks.append(current_main_block)

    segment.content_blocks = merged_blocks

    return segment
