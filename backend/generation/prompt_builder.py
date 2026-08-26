class PromptBuilder:

    @staticmethod
    def _build_article_text(
        articles: list[dict],
    ) -> str:

        return "\n\n".join(

            f"""
Article {index + 1}

Similarity Score:
{round(article.get('score', 0), 4)}

Title:
{article['title']}

Crop:
{article.get('crop')}

Category:
{article.get('category')}

Source:
{article.get('source')}

Content:
{article['content'][:1200]}
"""

            for index, article
            in enumerate(articles)

        )

    @staticmethod
    def build_push_prompt(
        query: str,
        articles: list[dict],
        language: str,
        crop: str | None,
    ) -> str:
        article_text = (
            PromptBuilder._build_article_text(
                articles
            )
        )

        return f"""
You are an agricultural communication specialist.

User Query:
{query}

IMPORTANT LANGUAGE INSTRUCTION:

Generate the ENTIRE response ONLY in {language}.

Requested Output Language = {language}

The source articles may be written in Marathi.
You MUST translate the information into the requested language.

Do NOT preserve the source article language.

If language is Marathi:
- Generate only Marathi.
- Do not generate Hindi.
- Do not generate English.

If language is English:
- Generate only English.
- Do not generate Marathi.
- Do not generate Hindi.

Translate information from the source articles if required.

The output language must strictly follow the requested language.

Before returning the response, verify that both TITLE and CONTENT are entirely in {language}.

CROP FOCUS REQUIREMENT

User Selected Crop:
{crop}

The retrieved articles may contain information
about multiple crops.

Focus only on information relevant to {crop}.

Ignore information related to other crops unless
it directly impacts {crop}.

If the selected crop is mentioned together with
other crops, prioritize the selected crop while
generating TITLE and CONTENT.

TASK:

Generate a push notification.

Return output in the following format:

TITLE:
<short attention-grabbing headline>

CONTENT:
<short notification message>

IMPORTANT RULES:

1. Focus only on the provided articles.
2. Use only factual information.
3. Do not invent information.
4. Title should be maximum 10 words.
5. Content should be maximum 40 words.
6. Create an attention-grabbing but professional title.
7. Use simple farmer-friendly language.
8. Output only TITLE and CONTENT.
9. Before returning the response, verify that both TITLE and CONTENT are entirely in {language}

Retrieved Articles:

{article_text}
"""

    @staticmethod
    def build_whatsapp_prompt(
        query: str,
        articles: list[dict],
        language: str,
        crop: str | None,
    ) -> str:

        article_text = (
            PromptBuilder._build_article_text(
                articles
            )
        )

        return f"""
You are an agricultural communication specialist.

OUTPUT LANGUAGE REQUIREMENT

Requested Language: {language}

The retrieved source articles may be written in Marathi.

Your first task is to translate all information from the source articles into {language}.

Your second task is to generate the WhatsApp communication.

The final TITLE and CONTENT must contain ONLY {language} text.

If the requested language is Hindi:
- Use standard Hindi.
- Translate all Marathi text into Hindi.
- Do not use Marathi words.
- Do not mix Marathi and Hindi.

Any Marathi text in the final output should be considered an error.

Return TITLE and CONTENT entirely in {language}.

CROP FOCUS REQUIREMENT

User Selected Crop:
{crop}

The retrieved articles may contain information
about multiple crops.

Focus only on information relevant to {crop}.

Ignore information related to other crops unless
it directly impacts {crop}.

If the selected crop is mentioned together with
other crops, prioritize the selected crop while
generating TITLE and CONTENT.

TITLE:
<daily update heading>

CONTENT:
<digest content>

IMPORTANT RULES:

1. Focus primarily on information relevant to the query.
2. Prioritize articles with higher similarity scores.
3. Only use facts found in the provided articles.
4. Do not invent information.
5. Use bullet points where appropriate.
6. Use farmer-friendly language.
7. Maximum 150 words.
8. Avoid repetition.
9. Output only TITLE and CONTENT.

Retrieved Articles:

{article_text}
"""

    @staticmethod
    def build_newsletter_prompt(
        query: str,
        articles: list[dict],
        language: str,
        crop: str | None,
    ) -> str:

        article_text = (
            PromptBuilder._build_article_text(
                articles
            )
        )

        return f"""
You are an agricultural editor creating a professional newsletter.

User Query:
{query}

IMPORTANT LANGUAGE INSTRUCTION:

Generate the ENTIRE response ONLY in {language}.

If language is Hindi:
- Generate only Hindi.
- Do not generate Marathi.
- Do not generate English.

If language is Marathi:
- Generate only Marathi.
- Do not generate Hindi.
- Do not generate English.

If language is English:
- Generate only English.
- Do not generate Marathi.
- Do not generate Hindi.

Translate information from the source articles if required.
The output language must strictly follow the requested language.

Before returning the response, verify that both TITLE and CONTENT are entirely in {language}.

CROP FOCUS REQUIREMENT

User Selected Crop:
{crop}

The retrieved articles may contain information
about multiple crops.

Focus only on information relevant to {crop}.

Ignore information related to other crops unless
it directly impacts {crop}.

If the selected crop is mentioned together with
other crops, prioritize the selected crop while
generating TITLE and CONTENT.

TASK:

Generate a newsletter.

Return output in the following format:

TITLE:
<newsletter title>

CONTENT:
<introduction>

<key highlights>

<important developments>

<closing summary>

IMPORTANT RULES:

1. Focus on the most important developments.
2. Only use facts present in the articles.
3. Do not invent information.
4. Organize information logically.
5. Avoid repeating the same information.
6. Use professional language.
7. Maximum 500 words.
8. Output only TITLE and CONTENT.

Retrieved Articles:

{article_text}
"""