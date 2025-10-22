import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from pprint import pprint
from configPy import EnvManager

openai_env = EnvManager.openai_env()


def main():
    client = chromadb.HttpClient(host="localhost", port=8000)
    print("ChromaDB client initialized:", client)

    collection = client.get_or_create_collection(
        name="textos_em_portugues",
        embedding_function=OpenAIEmbeddingFunction(
            api_key=openai_env.AZURE_OPENAI_API_KEY,
            model_name=openai_env.EMBEDDING_MODEL,
            api_type="azure",
            api_version=openai_env.AZURE_OPENAI_API_VERSION,
            api_base=openai_env.AZURE_ENDPOINT,
            deployment_id=openai_env.EMBEDDING_MODEL,
        ),
    )
    print("ChromaDB collection created or retrieved:", collection)

    # Example usage of the ChromaDB client
    collection = client.get_collection("textos_em_portugues")
    print("ChromaDB collection retrieved:", collection)

    collection.add(
        documents=[
            "tnarywjsydutmxk",
            "Esse é um texto que fala sobre culinária. No dia a dia do brasileiro, são muito presentes o arroz e o feijão.",
            "Esse é um texto que fala sobre esportes. O futebol é o esporte mais popular do Brasil.",
            "nhoeauhtnsoathnsaeonhtsoanhts",
        ],
        metadatas=[
            {"source": "brwsoabuao"},
            {"source": ""},
            {"source": "test_source"},
            {"source": "ushenanhtuea"},
        ],
        ids=["estags", "culinária", "esportes", "useaohtnoahtns"],
    )

    results = collection.query(
        query_texts=["tnarywjsydutmxk", "bola de futebol", "alimentação", "experiment"],
        n_results=1,
    )
    print("ChromaDB query results:")
    pprint(results)


if __name__ == "__main__":
    main()
