from configPy import EnvManager
from litellm import completion

azure_env = EnvManager.openai_env()
azure_deployment = azure_env.MODEL_NAME

response = completion(
    model=f"azure/{azure_deployment}",
    messages=[{"role": "user", "content": "Bom dia do litellm"}],
    api_key=azure_env.AZURE_API_KEY,
    api_base=azure_env.AZURE_API_BASE,
    api_version=azure_env.AZURE_API_VERSION,
)

print(response)
