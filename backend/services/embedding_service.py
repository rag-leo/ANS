from openai import AzureOpenAI

from backend.config.settings import settings


class EmbeddingService:
    """
    Azure OpenAI Embedding Service
    """

    def __init__(self) -> None:

        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )

        self.deployment_name = (
            settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        )

    def generate_embedding(
        self,
        text: str,
    ) -> list:
        response = self.client.embeddings.create(
            model=self.deployment_name,
            input=text,
        )

        return response.data[0].embedding