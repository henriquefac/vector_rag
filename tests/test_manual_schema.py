from src.chuncking.manual_proc_cart import Manual
from configPy import Config

files_dir = Config.get_dir_files()
manual_dir = files_dir["ChatCorregedoria"]["ManualProcedimentoCartorarios"]
list_files_manual = [f for f in manual_dir.list_files().values() if f.suffix == ".pdf"]

test_file = list_files_manual[2]

print(f"--- ARQUIVO PARA EXTRAIR OS COMPONENTES: {test_file} ---")
print("--- EXTRAINDO COMPONENTES ---")

manual = Manual.create_from_pdf(test_file)

print("--- TÍTULO DO MANUAL ---")
print(manual.title)
print("--- REFERÊNCIA NORMATIVA ---")
norm_ref = manual.normRef
for i, b in enumerate(norm_ref.content_blocks):
    print(
        f"""    <Bloco {i}: x0={b.x0}, y0={b.y0}, x1={b.x1}, y1={b.y1}>
        {b.lines}
    <\\Bloco>"""
    )
print("--- SEGMENTOS ---")

list_segments = manual.content

for i, section in enumerate(list_segments):
    title = section.title
    themes = section.themes
    subsections = section.subsection
    list_blocks = section.content_blocks

    print(
        f"""  <Section: title={title},
    themes={", ".join(themes)},
    subsectionLentgh={len(subsections)}>
    ${"\n    $".join([b.lines for b in list_blocks])}
    """
    )

    if len(subsections) > 0:
        for i, subsection in enumerate(subsections):
            sub_title = subsection.title
            sub_themes = subsection.themes
            sub_list_block = subsection.content_blocks
            print(
                f"""
        <Subsection: title={sub_title},
        themes={", ".join(themes)}>
            @{"\n        @".join([b.lines for b in sub_list_block])}
        <\\Subsection>
            """
            )
    print("    <\\Section>")
