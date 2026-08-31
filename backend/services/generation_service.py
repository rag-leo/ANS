import re

from backend.config.generation_config import (
    GENERATION_CONFIG,
)

from backend.config.logging_config import get_logger

from backend.generation.generators import (
    PushGenerator,
    WhatsAppGenerator,
    NewsletterGenerator,
)

from backend.services.retrieval_service import (
    RetrievalService,
)

logger = get_logger(__name__)

_TITLE_CONTENT_PATTERN = re.compile(
    r"TITLE\s*:\s*(?P<title>.*?)\s*CONTENT\s*:\s*(?P<content>.*)",
    re.IGNORECASE | re.DOTALL,
)


class GenerationService:

    def __init__(self):

        self.retrieval_service = (
            RetrievalService()
        )

        self.push_generator = (
            PushGenerator()
        )

        self.whatsapp_generator = (
            WhatsAppGenerator()
        )

        self.newsletter_generator = (
            NewsletterGenerator()
        )

    def generate(
        self,
        request,
    ):

        generation_type = (
            request.generation_type.value
            if hasattr(
                request.generation_type,
                "value",
            )
            else request.generation_type.lower()
        )

        generation_settings = (
            GENERATION_CONFIG[
                generation_type
            ]
        )

        search_results = (
            self.retrieval_service.search(
                query=request.query,
                crop=request.crop,
                category=request.category,
                source=request.source,
                generation_type=generation_type,
                max_age_days=(
                    generation_settings[
                        "max_age_days"
                    ]
                ),
                top_k=(
                    generation_settings[
                        "top_k"
                    ]
                ),
            )
        )

        if not search_results:

            return {
                "title": "No Articles Found",
                "content": "No relevant articles found.",
                "article_count": 0,
                "article_ids": [],
                "source_articles": [],
            }

        max_tokens = generation_settings["max_tokens"]

        if generation_type == "push":

            generated_content = (
                self.push_generator.generate(
                    query=request.query,
                    articles=search_results,
                    language=request.language,
                    crop=request.crop,
                    max_tokens=max_tokens,
                )
            )

        elif generation_type == "whatsapp":

            generated_content = (
                self.whatsapp_generator.generate(
                    query=request.query,
                    articles=search_results,
                    language=request.language,
                    crop=request.crop,
                    max_tokens=max_tokens,
                )
            )

        elif generation_type == "newsletter":

            generated_content = (
                self.newsletter_generator.generate(
                    query=request.query,
                    articles=search_results,
                    language=request.language,
                    crop=request.crop,
                    max_tokens=max_tokens,
                )
            )

        else:

            raise ValueError(
                f"Unsupported generation type: "
                f"{generation_type}"
            )

        logger.debug(
            "Generated content",
            extra={
                "language": request.language,
                "generation_type": generation_type,
            },
        )

        seen = set()

        source_articles = []

        for article in search_results:

            if article["article_id"] in seen:
                continue

            seen.add(
                article["article_id"]
            )

            source_articles.append(
                {
                    "article_id": article["article_id"],
                    "title": article["title"],
                    "source": article["source"],
                    "crop": article["crop"],
                    "score": round(
                        article["score"],
                        4,
                    ),
                }
            )

        title, content = self._parse_generated_content(
            generated_content
        )

        return {
            "generation_type": generation_type,

            "title": title,

            "content": content,

            "article_count": len(
                source_articles
            ),

            "article_ids": [
                article["article_id"]
                for article in source_articles
            ],

            "source_articles":
                source_articles,
        }

    def _parse_generated_content(
        self,
        generated_content: str,
    ) -> tuple[str, str]:
        """
        Splits a "TITLE: ... CONTENT: ..." response into
        (title, content), tolerating case and whitespace
        differences. Falls back to using the first line as
        the title if the model didn't follow the format,
        rather than silently returning an empty title.
        """

        generated_content = generated_content or ""

        match = _TITLE_CONTENT_PATTERN.search(
            generated_content
        )

        if match:
            return (
                match.group("title").strip(),
                match.group("content").strip(),
            )

        logger.warning(
            "Generated content did not follow the "
            "TITLE/CONTENT format; falling back to "
            "heuristic parsing"
        )

        lines = [
            line.strip()
            for line in generated_content.strip().splitlines()
            if line.strip()
        ]

        if not lines:
            return "", ""

        return lines[0], generated_content.strip()
