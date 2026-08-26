from backend.config.generation_config import (
    GENERATION_CONFIG,
)

from backend.generation.generators import (
    PushGenerator,
    WhatsAppGenerator,
    NewsletterGenerator,
)

from backend.services.retrieval_service import (
    RetrievalService,
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

        if generation_type == "push":

            generated_content = (
                self.push_generator.generate(
                    query=request.query,
                    articles=search_results,
                    language=request.language,
                    crop=request.crop,
                )
            )

        elif generation_type == "whatsapp":

            generated_content = (
                self.whatsapp_generator.generate(
                    query=request.query,
                    articles=search_results,
                    language=request.language,
                    crop=request.crop,
                )
            )

        elif generation_type == "newsletter":

            generated_content = (
                self.newsletter_generator.generate(
                    query=request.query,
                    articles=search_results,
                    language=request.language,
                    crop=request.crop,
                )
            )

        else:

            raise ValueError(
                f"Unsupported generation type: "
                f"{generation_type}"
            )

        print(
            f"Language received = {request.language}"
        )    

        print(
            f"Generation type = {generation_type}"
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

        return {
            "generation_type": generation_type,

            "title": self._extract_title(
                generated_content
            ),

            "content": self._extract_content(
                generated_content
            ),

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
    def _extract_title(
        self,
        generated_content: str,
    ) -> str:

        if "TITLE:" not in generated_content:

            return ""

        start = (
            generated_content.find(
                "TITLE:"
            ) + len("TITLE:")
        )

        end = (
            generated_content.find(
                "CONTENT:"
            )
        )

        if end == -1:

            return (
                generated_content[start:]
                .strip()
            )

        return (
            generated_content[
                start:end
            ]
            .strip()
        )


    def _extract_content(
        self,
        generated_content: str,
    ) -> str:

        if "CONTENT:" not in (
            generated_content
        ):

            return generated_content

        start = (
            generated_content.find(
                "CONTENT:"
            ) + len("CONTENT:")
        )

        return (
            generated_content[start:]
            .strip()
        )    