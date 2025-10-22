from configPy import Config, DirManager
from pathlib import Path
import unicodedata

files_dir = Config.get_dir_files()


# fix encoding
def fix_enconding(text: str) -> str:
    return text.encode("utf-8").decode("utf-8")


def normalize_char(c):
    # Retorna o caractere sem acento (base)
    normalized = unicodedata.normalize("NFD", c)
    print(normalized)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def remove_accents(input_str: str) -> str:
    # Remove acentos de toda a string
    return "".join(normalize_char(c) for c in input_str)


def nromalize_file_name(path: Path) -> None:

    pass


def normalize_dir_name(dir: DirManager) -> None:

    pass


if __name__ == "__main__":
    dir_chat = files_dir["ChatCorregedoria"]
    manual = dir_chat["ManualProcedimentoCartorarios"]
    first_file = next(manual.iter_files())
    name = first_file.name
    print(name)
    name = fix_enconding(name)
    print(name)
    name = remove_accents(name)
    print(name)
