from configPy import EnvManager
from openai import AzureOpenAI

openai_env = EnvManager.openai_env()

client = AzureOpenAI(
    api_key=openai_env.AZURE_OPENAI_API_KEY,
    api_version=openai_env.AZURE_OPENAI_API_VERSION,
    azure_endpoint=openai_env.AZURE_ENDPOINT,
    azure_deployment=openai_env.EMBEDDING_MODEL,
)


texts = [
    "A Justiça Eleitoral é responsável pela organização das eleições no Brasil.",
    "O autoatendimento do eleitor permite atualização cadastral online.",
]


response = client.embeddings.create(
    model=openai_env.EMBEDDING_MODEL,  # ⚠️ nome do deployment, não o nome do modelo OpenAI!
    input=texts,
)

for i, emb in enumerate(response.data):
    print(f"\nTexto {i+1}: {texts[i][:50]}...")
    print(f"Tamanho do embedding: {len(emb.embedding)}")
    print(f"Primeiros 5 valores: {emb.embedding[:5]}")
