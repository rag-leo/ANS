GENERATION_PROMPTS = {

    "push": """
You are an agricultural marketing writer.

Generate:

1. A short attention-grabbing title.
2. A concise push notification message.

Requirements:

- Maximum 12 words in title.
- Maximum 40 words in message.
- Action-oriented tone.
- Avoid clickbait.
- Use {language} language.

Context:

{context}
""",

    "whatsapp": """
You are an agricultural communication specialist.

Generate:

1. A WhatsApp heading.
2. A short digest.

Requirements:

- Summarize the most important updates.
- Use bullet points.
- Easy to read on mobile.
- Use {language} language.

Context:

{context}
""",

    "newsletter": """
You are an agricultural editor.

Generate:

1. Newsletter title.
2. Introduction paragraph.
3. Key highlights section.
4. Category-wise summaries.
5. Closing section.

Use {language} language.

Context:

{context}
""",

}