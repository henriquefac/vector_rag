import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from pprint import pprint

def main():
    client = chromadb.HttpClient(host='localhost', port=8000)
    print("ChromaDB client initialized:", client)

    collection = client.get_or_create_collection(
        name="textos_em_portugues",
        embedding_function=OpenAIEmbeddingFunction(
            api_key=""
            model_name="text-embedding-ada-002",
            api_type="azure",
            api_version="2025-01-01-preview",
            api_base=""
            deployment_id="text-embedding-ada-002"
        )
    )
    print("ChromaDB collection created or retrieved:", collection)

    # Example usage of the ChromaDB client
    collection = client.get_collection("textos_em_portugues")
    print("ChromaDB collection retrieved:", collection)

    collection.add(
        documents=[
            "Esse é um texto que fala sobre culinária. No dia a dia do brasileiro, são muito presentes o arroz e o feijão.",
            "Esse é um texto que fala sobre esportes. O futebol é o esporte mais popular do Brasil.",
            "nhoeauhtnsoathnsaeonhtsoanhts"
        ],
        metadatas=[{"source": ""}, {"source": "test_source"}, {"source": "ushenanhtuea"}],
        ids=["culinária", "esportes", "useaohtnoahtns"]
    )

    results = collection.query(
        query_texts=["bola de futebol", "alimentação", "experiment"],
        n_results=1
    )
    print("ChromaDB query results:")
    pprint(results)


if __name__ == "__main__":
    main()
