from openai import AzureOpenAI

from backend.config.settings import settings

from backend.generation.prompt_builder import (
    PromptBuilder,
)


class PushGenerator:

    def __init__(self):

        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )

    def generate(
        self,
        query: str,
        articles: list[dict],
        language: str,
    ) -> str:

        prompt = (
            PromptBuilder.build_push_prompt(
                query=query,
                articles=articles,
                language=language,
            )
        )

        response = (
            self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.3,
            )
        )

        return (
            response.choices[0]
            .message.content
        )


class WhatsAppGenerator:

    def __init__(self):

        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )

    def generate(
        self,
        query: str,
        articles: list[dict],
        language: str,
    ) -> str:

        prompt = (
            PromptBuilder.build_whatsapp_prompt(
                query=query,
                articles=articles,
                language=language,
            )
        )

        response = (
            self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.3,
            )
        )

        return (
            response.choices[0]
            .message.content
        )


class NewsletterGenerator:

    def __init__(self):

        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )

    def generate(
        self,
        query: str,
        articles: list[dict],
        language: str,
    ) -> str:

        prompt = (
            PromptBuilder.build_newsletter_prompt(
                query=query,
                articles=articles,
                language=language,
            )
        )

        response = (
            self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.3,
            )
        )

        return (
            response.choices[0]
            .message.content
        )