from ollama import Client
import numpy as np
import json

# Importar a função de similaridade do cosseno
from sklearn.metrics.pairwise import cosine_similarity

# Importações de módulos customizados
from src.chuncking.manual_proc_cart import (
    Manual,
)
from configPy import Config


# --- Configuração e Setup ---
client = Client(host="http://localhost:11434")
EMBEDDING_MODEL = "nomic-embed-text"

# Assume-se que esta lógica de diretório e arquivo está correta no seu ambiente
files_dir = Config.get_dir_files()
manual_dir = files_dir["ChatCorregedoria"]["ManualProcedimentoCartorarios"]
list_files_manual = [f for f in manual_dir.list_files().values() if f.suffix == ".pdf"]
test_file = list_files_manual[2]

# saída
output_dir_queryes = files_dir.create_dir("output_queryes")
output_path = output_dir_queryes.create_file_path("output", "txt", overwrite=True)


def get_embedding_for_chunk(text: str) -> np.ndarray:
    """Generates an embedding for a piece of text."""
    response = client.embeddings(model=EMBEDDING_MODEL, prompt=text)
    return np.array(response.embedding)


# --- 1. Geração de Chunks e Embeddings ---
print(f"--- ARQUIVO PARA EXTRAIR OS COMPONENTES: {test_file.name} ---")

manual = Manual.create_from_pdf(test_file)
# Note: Usando get_chunks_with_context, conforme seu último código
chunk_context = list(manual.get_chunks_by_window(window_size=3, overlap_size=1))
# extrair apenas texto dos chunks

chunks = chunk_context

chunk_text = [chunk.text for chunk in chunks]
chunk_text_embedding = [get_embedding_for_chunk(text) for text in chunk_text]

# 1. DEFINIR AS QUERIES DE TESTE
querys = [
    "Quais são as condições de elegibilidade e inelegibilidade que precisam ser verificadas no momento do pedido de registro de candidatura?",
    "Quem tem legitimidade para protocolar o pedido de registro de candidatura no CANDex e quais dados precisam ser informados por quem subscreve o pedido?",
    "Como funciona o prazo e o procedimento para substituição de candidatura em caso de indeferimento, renúncia ou falecimento após o registro?",
    "O que acontece se o partido não cumprir a cota mínima de gênero ao apresentar o DRAP? Há indeferimento imediato?",
    "Como é processada uma Ação de Impugnação de Registro de Candidatura (AIRC)? Quem pode impugnar e qual é o prazo para isso?",
]
print(f"\n--- TOTAL DE QUERIES: {len(querys)} ---")

# 2. GERAR EMBEDDING DAS QUERIES
querys_embedding = [get_embedding_for_chunk(query).reshape(1, -1) for query in querys]
print("--- Embedding das Queries gerado. ---")

top_n = 5
all_query_results = []
query_similarities = []

for idx, (query, query_embedding) in enumerate(zip(querys, querys_embedding)):
    results = []

    similarity_array = cosine_similarity(
        query_embedding, chunk_text_embedding
    ).flatten()

    top_indices = np.argsort(similarity_array)[::-1][:top_n]

    for chunk_rank, i in enumerate(top_indices):

        text = chunk_text[i]
        results.append(
            {
                "Query_index": int(idx + 1),
                "Query_text": query,
                "Rank": int(chunk_rank + 1),
                "Similarity_score": float(similarity_array[i]),
                "Chunk_index": int(i),
                "Chunk_text": text,
            }
        )

    all_query_results.append(results)


print(json.dumps(all_query_results, indent=4))

with open(output_path, "w") as t:
    t.write("")

for i, query in enumerate(all_query_results):
    text = f"PROMPT : {query[0]["Query_text"]}\n\n CONTEXTO:\n"

    for res in query:
        text += f"""
{res["Chunk_text"]}
        """
    text += "\n"
    with open(output_path, "a") as tex:
        tex.write(text)
