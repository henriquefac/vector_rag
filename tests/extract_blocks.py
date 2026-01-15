from configPy import Config
from src.chuncking.manual_proc_cart import Manual, ChunkManual

files_dir = Config.get_dir_files()
manual_dir = files_dir["ChatCorregedoria"]["ManualProcedimentoCartorarios"]
list_files_manual = [f for f in manual_dir.list_files().values() if f.suffix == ".pdf"]

chunks: list[ChunkManual] = []


for file in list_files_manual:
    try:

        manual = Manual.create_from_pdf(file)

        list_chunks = list(manual.get_chunks_by_window(window_size=3, overlap_size=1))

        chunks.extend(list_chunks)
    except Exception as e:
        print(f"Erro ao processar o arquvio '{file}': {e}")
