from src.chuncking import manual_proc_cart
from configPy import Config

files_dir = Config.get_dir_files()
manual_dir = files_dir["ChatCorregedoria"]["ManualProcedimentoCartorarios"]
list_files_manal = [f for f in manual_dir.list_files().values() if f.suffix == ".pdf"]

test_file = list_files_manal[2]

# buscar referências normativas
print(f"--- ARQUIVO PDF PARA TESTAR O MÓDULO: {test_file} ---")
print("--- EXTRAINDO REPRESENTAÇÃO EM BLOCOS DA ESTRUTURA DO PDF ---")

list_sections = []

# extrair PDFDict e adquirir tamanho
pdf_dict, width = manual_proc_cart.basic_extraction.get_pdf_blocks(test_file)
norms = manual_proc_cart.components_extraction.get_normative_references(pdf_dict)

list_sections.append(norms)


list_sections.extend(
    manual_proc_cart.components_extraction.extract_sections_and_subsections(
        pdf_dict, width
    )
)

print(list_sections[1])
