from configPy import Config
from src.chuncking.manual_proc_cart import Manual

files_dir = Config.get_dir_files()
manual_dir = files_dir["ChatCorregedoria"]["ManualProcedimentoCartorarios"]
test_file = manual_dir.get_any(
    "Cap├нtulo XXV_MPC CRE-CE_25-09-2025_Presta├з├гo de Contas de Campanha.pdf"
)

manual = Manual.create_from_pdf(test_file)

for section in manual.content:
    print(section.title)

chuncks = list(manual.get_chunks_by_window(window_size=3, overlap_size=1))
