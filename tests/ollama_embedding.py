from ollama import Client
from sklearn.manifold import TSNE
import numpy as np
import matplotlib.pyplot as plt

# Importar a função de similaridade do cosseno
from sklearn.metrics.pairwise import cosine_similarity

# Importações de módulos customizados
from src.chuncking.manual_proc_cart import (
    Manual,
    # get_chunks_with_context,
    get_chunks_only_metadata,
)
from configPy import Config
import pandas as pd

# --- Configuração e Setup ---
client = Client(host="http://localhost:11434")
EMBEDDING_MODEL = "nomic-embed-text"

# Assume-se que esta lógica de diretório e arquivo está correta no seu ambiente
files_dir = Config.get_dir_files()
manual_dir = files_dir["ChatCorregedoria"]["ManualProcedimentoCartorarios"]
list_files_manual = [f for f in manual_dir.list_files().values() if f.suffix == ".pdf"]
test_file = list_files_manual[2]


def get_embedding_for_chunk(text: str) -> np.ndarray:
    """Generates an embedding for a piece of text."""
    response = client.embeddings(model=EMBEDDING_MODEL, prompt=text)
    return np.array(response.embedding)


# --- 1. Geração de Chunks e Embeddings ---
print(f"--- ARQUIVO PARA EXTRAIR OS COMPONENTES: {test_file.name} ---")

manual = Manual.create_from_pdf(test_file)
# Note: Usando get_chunks_with_context, conforme seu último código
chunk_met_only = list(get_chunks_only_metadata(manual))

print(f"--- Encontrados {len(chunk_met_only)} chunks. ---")
chunk_met_only_embedding = np.array(
    [get_embedding_for_chunk(chunk["document"]) for chunk in chunk_met_only]
)
print(
    f"--- Embeddings dos Chunks gerados. Dimensão: {chunk_met_only_embedding.shape} ---"
)

# -----------------------------------------------------------
# --- NOVO BLOCO: Teste de Similaridade de Query ---
# -----------------------------------------------------------

# 1. DEFINIR AS QUERIES DE TESTE
querys = [
    "Quais são os procedimentos para a remessa de autos de processos físicos para o segundo grau de jurisdição?",
    "Quais grupos de pessoas, além das maiores de 80 anos, têm prioridade no atendimento no cartório eleitoral, e qual legislação estabelece essa prioridade?",
    "Em caso de fechamento extraordinário do Cartório Eleitoral, quem deve estabelecê-lo, de que forma o ato deve ser publicado e qual é a informação obrigatória que a portaria deve conter?",
    "De acordo com o Código de Ética e as normas de serviço, quais condutas são vedadas aos servidores nas redes sociais, blogs e nas dependências da Justiça Eleitoral?",
    "Liste as três primeiras das principais rotinas procedimentais e serviços cartorários voltados para atuação administrativa, conforme o item 3.13 do Manual.",
    "Quais são as responsabilidades do Chefe de Cartório em relação à fiscalização do cumprimento da jornada de trabalho e à supervisão de processos paralisados?",
]
print(f"\n--- TOTAL DE QUERIES: {len(querys)} ---")

# 2. GERAR EMBEDDING DAS QUERIES
querys_embedding = [get_embedding_for_chunk(query).reshape(1, -1) for query in querys]
print("--- Embedding das Queries gerado. ---")

# 3. CALCULAR SIMILARIDADE DO COSSENO E ENCONTRAR TOP CHUNKS
top_n = 5
all_query_results = []
query_similarities = []

for idx, (query, query_embedding) in enumerate(zip(querys, querys_embedding)):
    # Calcula a similaridade do cosseno para a query atual
    similarity_array = cosine_similarity(
        query_embedding, chunk_met_only_embedding
    ).flatten()
    query_similarities.append(similarity_array)  # Armazena para o plot da última query

    # Encontra os índices dos top N chunks (do mais similar para o menos)
    top_indices = np.argsort(similarity_array)[::-1][:top_n]

    # Prepara os resultados para o DataFrame
    for chunk_rank, i in enumerate(top_indices):
        # Acessa o chunk original e limpa quebras de linha
        chunk_text = chunk_met_only[i]["document"].replace("\n", " ")
        all_query_results.append(
            {
                "Query Index": idx + 1,
                "Query Text": query[:80] + "...",
                "Rank": chunk_rank + 1,
                "Similarity Score": similarity_array[i],
                "Chunk Index": i,
                "Chunk Snippet": chunk_text[:150] + "...",
            }
        )

# Exibir e Salvar Resultados de Todas as Queries
df_results = pd.DataFrame(all_query_results)
df_results.to_csv("query_chunk_similarities.csv", index=False)
print("--- Tabela de Similaridade Salva em 'query_chunk_similarities.csv' ---")

# Exibe na saída apenas um resumo das colunas mais importantes
print(
    df_results[["Query Index", "Rank", "Similarity Score", "Chunk Snippet"]].to_string()
)


# 5. VISUALIZAÇÃO T-SNE para a ÚLTIMA QUERY
print("\n--- Visualização da Query (t-SNE) ---")

# Seleciona dados da última query para o plot
last_query_embedding = querys_embedding[-1]
last_query_similarity = query_similarities[-1]
last_query_text = querys[-1]
top_indices_last_query = np.argsort(last_query_similarity)[::-1][:top_n]

# Configuração e Treinamento do t-SNE
# O t-SNE é treinado duas vezes, o que é necessário para a visualização,
# pois ele não tem uma função 'transform' que garanta a posição consistente de novos pontos.
tsne = TSNE(n_components=2, random_state=42, perplexity=30)

# 1. Roda o t-SNE nos chunks + query para garantir que a query seja mapeada com o contexto dos chunks
combined_embeddings = np.vstack([chunk_met_only_embedding, last_query_embedding])
combined_reduced_embedding = tsne.fit_transform(combined_embeddings)

query_position = combined_reduced_embedding[-1, :]
chunk_positions = combined_reduced_embedding[:-1, :]

# Geração do Plot
plt.figure(figsize=(12, 10))
plt.scatter(
    chunk_positions[:, 0],
    chunk_positions[:, 1],
    c="gray",
    alpha=0.3,
    label="Chunks (Outros)",
)
plt.scatter(
    query_position[0],
    query_position[1],
    c="red",
    marker="X",
    s=300,
    label="Query (Última)",
    zorder=3,
)
plt.scatter(
    chunk_positions[top_indices_last_query, 0],
    chunk_positions[top_indices_last_query, 1],
    c="blue",
    s=150,
    edgecolor="black",
    label=f"Top {top_n} Chunks Relevantes",
    zorder=2,
)
plt.title("t-SNE: Posição Semântica dos Chunks e da Query")
plt.xlabel("t-SNE Component 1")
plt.ylabel("t-SNE Component 2")
plt.legend()
plt.figtext(
    0.5, 0.01, f"Última Query: {last_query_text}", ha="center", fontsize=9, wrap=True
)
plt.tight_layout(rect=[0, 0.05, 1, 1])  # Ajusta para caber o texto no rodapé
plt.savefig("output_tsne_query_comparison_2.png")

print("--- Gráfico salvo em 'output_tsne_query_comparison.png' ---")
print("--- Processo concluído! ---")
