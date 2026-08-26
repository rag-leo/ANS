import requests

import requests

API_BASE_URL = "http://localhost:8000"


def generate_embedding(
    text: str,
) -> dict:
    """
    Calls the ANIS embedding API.
    """

    response = requests.post(
        f"{API_BASE_URL}/embed",
        json={
            "text": text,
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


def search(
    query: str,
    crop: str | None = None,
    category: str | None = None,
    source: str | None = None,
):

    response = requests.post(
        f"{API_BASE_URL}/search",
        json={
            "query": query,
            "crop": crop,
            "category": category,
            "source": source,
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


def health_check() -> dict:
    """
    Calls the ANIS health endpoint.
    """

    response = requests.get(
        f"{API_BASE_URL}/health",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def generate_content(
    query,
    crop=None,
    category=None,
    source=None,
    language="English",
    generation_type="push",
):
    response = requests.post(
        f"{API_BASE_URL}/generate",
        json={
            "query": query,
            "crop": crop,
            "category": category,
            "source": source,
            "language": language,
            "generation_type":generation_type
        },
        timeout=120,
    )

    response.raise_for_status()

    print(response)

    return response.json()


def publish_content(
    article_ids,
    generation_type,
    language,
):

    payload = {
        "article_ids": article_ids,
        "generation_type": generation_type,
        "language": language,
    }

    response = requests.post(
        f"{API_BASE_URL}/publish",
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def get_notification_history():

    response = requests.get(
        f"{API_BASE_URL}/publish/history",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def get_analytics_summary():

    response = requests.get(
        f"{API_BASE_URL}/analytics/summary",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def submit_evaluation(
    payload,
):

    response = requests.post(
        f"{API_BASE_URL}/evaluation/submit",
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()