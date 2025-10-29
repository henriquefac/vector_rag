from src.chuncking.manual_proc_cart import Manual, format_chunk_for_chroma
from configPy import Config
from json import dumps

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

print("======== CHUNCKS FEITOS APENAS COM METADADOS ========")

chunks = list(manual.get_chunks_by_window(window_size=3))
format_chunk = [format_chunk_for_chroma(chunk) for chunk in chunks]

for chunk in format_chunk[:5]:
    print(dumps(chunk, indent=4))
