"""
Azure OpenAI Connectivity Test

Purpose:
- Validate Azure OpenAI configuration
- Validate endpoint connectivity
- Validate embedding deployment
- Verify authentication

Run:
    python -m tests.test_openai_connection
"""

from openai import AzureOpenAI

from backend.config.settings import settings


def test_embedding_connection() -> None:
    """
    Test Azure OpenAI embedding deployment.
    """

    print("\n" + "=" * 60)
    print("AZURE OPENAI CONNECTIVITY TEST")
    print("=" * 60)

    print(f"Endpoint   : {settings.AZURE_OPENAI_ENDPOINT}")
    print(f"Deployment : {settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}")
    print(f"API Version: {settings.AZURE_OPENAI_API_VERSION}")

    client = AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )

    response = client.embeddings.create(
        model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        input="Wheat farming in Maharashtra",
    )

    embedding = response.data[0].embedding

    print("\n✅ Azure OpenAI Connection Successful")
    print(f"Embedding Dimensions: {len(embedding)}")
    print(f"First 5 Values: {embedding[:5]}")


if __name__ == "__main__":
    try:
        test_embedding_connection()

    except Exception as ex:
        print("\n❌ Azure OpenAI Connection Failed")
        print(f"Error: {str(ex)}")
        raise