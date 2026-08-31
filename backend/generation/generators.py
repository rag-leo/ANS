from openai import AzureOpenAI
from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.config.logging_config import get_logger
from backend.config.settings import settings

from backend.generation.language_check import (
    matches_expected_language,
)

from backend.generation.prompt_builder import (
    PromptBuilder,
)

logger = get_logger(__name__)

# Transient errors worth retrying. Auth/validation errors
# (AuthenticationError, BadRequestError, ...) are not retried
# since a retry can't fix them.
_RETRYABLE_ERRORS = (
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    InternalServerError,
)

_LANGUAGE_RETRY_REMINDER = (
    "\n\nSTRICT REMINDER: your previous response was not "
    "entirely in {language}. Respond ONLY in {language}, "
    "using no other language or script anywhere in the output."
)


class BaseGenerator:

    def __init__(self) -> None:

        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )

    @retry(
        retry=retry_if_exception_type(_RETRYABLE_ERRORS),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def _complete(
        self,
        prompt: str,
        max_tokens: int,
    ) -> str:

        response = self.client.chat.completions.create(
            model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.3,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content or ""

    def _complete_with_language_check(
        self,
        prompt: str,
        max_tokens: int,
        language: str,
    ) -> str:

        text = self._complete(prompt, max_tokens)

        if matches_expected_language(text, language):
            return text

        logger.warning(
            "Generated output did not match the expected "
            "language script, retrying once",
            extra={"language": language},
        )

        retry_prompt = prompt + _LANGUAGE_RETRY_REMINDER.format(
            language=language
        )

        text = self._complete(retry_prompt, max_tokens)

        if not matches_expected_language(text, language):
            logger.warning(
                "Generated output still did not match the "
                "expected language script after retry",
                extra={"language": language},
            )

        return text


class PushGenerator(BaseGenerator):

    def generate(
        self,
        query: str,
        articles: list[dict],
        language: str,
        crop: str | None,
        max_tokens: int = 200,
    ) -> str:

        prompt = (
            PromptBuilder.build_push_prompt(
                query=query,
                articles=articles,
                language=language,
                crop=crop,
            )
        )

        return self._complete_with_language_check(
            prompt,
            max_tokens,
            language,
        )


class WhatsAppGenerator(BaseGenerator):

    def generate(
        self,
        query: str,
        articles: list[dict],
        language: str,
        crop: str | None,
        max_tokens: int = 500,
    ) -> str:

        prompt = (
            PromptBuilder.build_whatsapp_prompt(
                query=query,
                articles=articles,
                language=language,
                crop=crop,
            )
        )

        return self._complete_with_language_check(
            prompt,
            max_tokens,
            language,
        )


class NewsletterGenerator(BaseGenerator):

    def generate(
        self,
        query: str,
        articles: list[dict],
        language: str,
        crop: str | None,
        max_tokens: int = 1200,
    ) -> str:

        prompt = (
            PromptBuilder.build_newsletter_prompt(
                query=query,
                articles=articles,
                language=language,
                crop=crop,
            )
        )

        return self._complete_with_language_check(
            prompt,
            max_tokens,
            language,
        )
