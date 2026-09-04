# backend/services/llm_metadata_service.py

import json

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

logger = get_logger(__name__)

# Same taxonomy MetadataService's keyword rules target, so tagging is
# consistent across sources regardless of which one (keyword or LLM)
# produced it historically. Category names and crop names (translated
# from MetadataService.KEYWORD_CROPS) are both held fixed rather than
# left open-ended, so crop-filtered search stays an exact match across
# every source instead of accumulating free-text variants.
CATEGORIES = [
    "Weather",
    "Market Intelligence",
    "Policy",
    "Technology",
    "Politics",
    "Administration",
    "Livestock",
    "Research",
    "Crop Advisory",
    "General",
]

CROPS = [
    "Cotton",
    "Soybean",
    "Sugarcane",
    "Pigeon Pea",
    "Chickpea",
    "Wheat",
    "Banana",
    "Grape",
    "Onion",
    "Maize",
    "Tomato",
    "Chili",
    "Pomegranate",
    "Groundnut",
    "Rice",
    "Potato",
]

_CROPS_BY_LOWER = {crop.lower(): crop for crop in CROPS}

_RETRYABLE_ERRORS = (
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    InternalServerError,
)

_SYSTEM_PROMPT = f"""You classify Indian agriculture news articles from their \
title and an excerpt.

Respond with a single JSON object with exactly two fields:
- "category": exactly one value from this list: {CATEGORIES}
- "crop": a list of zero or more values from this list: {CROPS} — only \
crops the article substantively discusses, not incidental mentions. Use \
an empty list if no crop from this list is a real subject of the article.

Only use values from the two lists above — never invent a category or \
crop name. If nothing fits clearly, use category "General". Respond with \
JSON only, no other text."""


class LLMMetadataService:
    """
    Crop/category classification via a small LLM deployment, used in
    place of MetadataService's keyword rules (which are Marathi-only
    and don't generalize to English sources or future languages).
    Classifies from title + a short excerpt (the article's first
    chunk), not the full article — see Stage 9 discussion for why a
    short excerpt is sufficient for this task.
    """

    def __init__(self) -> None:

        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )

        self.deployment_name = (
            settings.AZURE_OPENAI_CLASSIFICATION_DEPLOYMENT
        )

    @retry(
        retry=retry_if_exception_type(_RETRYABLE_ERRORS),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def _complete(self, title: str, excerpt: str) -> str:

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nExcerpt:\n{excerpt}",
                },
            ],
            temperature=0,
            max_tokens=200,
            response_format={"type": "json_object"},
        )

        return response.choices[0].message.content or ""

    def extract_metadata(self, title: str, excerpt: str) -> dict:
        """
        Same return shape as MetadataService.extract_metadata (crop,
        category, keywords) so callers don't need to branch on which
        tagger produced it. `confidence` isn't included — there's no
        per-crop score to report from a single classification call.

        Falls back to category "General", crop [] on any API or
        parsing failure, logged rather than raised, so one article's
        classification hiccup doesn't take down the whole batch (the
        pipeline's per-article isolation would catch a raised
        exception anyway, but a fallback here means the article still
        gets ingested with a safe default instead of being skipped).
        """

        title = title or ""
        excerpt = excerpt or ""

        try:
            raw_response = self._complete(title, excerpt)
            parsed = json.loads(raw_response)

        except Exception:
            logger.exception(
                "LLM classification failed; falling back to General",
                extra={"title": title[:70]},
            )
            return {"crop": [], "category": "General", "keywords": []}

        category = parsed.get("category")

        if category not in CATEGORIES:
            logger.warning(
                "LLM returned a category outside the taxonomy; "
                "falling back to General",
                extra={"title": title[:70], "returned_category": category},
            )
            category = "General"

        raw_crops = parsed.get("crop") or []

        if not isinstance(raw_crops, list):
            raw_crops = []

        crops = []

        for value in raw_crops:

            canonical = _CROPS_BY_LOWER.get(str(value).strip().lower())

            if canonical and canonical not in crops:
                crops.append(canonical)

        return {"crop": crops, "category": category, "keywords": crops}
