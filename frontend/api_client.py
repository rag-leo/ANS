import requests
import streamlit as st

DEFAULT_BACKEND_URL = "http://localhost:8000"


def get_backend_url() -> str:
    """
    Retrieves backend API URL from Streamlit secrets.

    Falls back to localhost for local development.
    """

    try:
        return st.secrets["BACKEND_API_URL"]
    except Exception:
        return DEFAULT_BACKEND_URL


BACKEND_URL = get_backend_url()

# Must match the backend's settings.API_PREFIX.
API_PREFIX = "/api"


def generate_embedding(
    text: str,
) -> dict:
    """
    Calls the ANIS embedding API.
    """

    response = requests.post(
        f"{BACKEND_URL}{API_PREFIX}/embed",
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
        f"{BACKEND_URL}{API_PREFIX}/search",
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
        f"{BACKEND_URL}/health",
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
        f"{BACKEND_URL}{API_PREFIX}/generate",
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
        f"{BACKEND_URL}{API_PREFIX}/publish",
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def get_notification_history():

    response = requests.get(
        f"{BACKEND_URL}{API_PREFIX}/publish/history",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def get_analytics_summary():

    response = requests.get(
        f"{BACKEND_URL}{API_PREFIX}/analytics/summary",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def submit_evaluation(
    payload,
):

    response = requests.post(
        f"{BACKEND_URL}{API_PREFIX}/evaluation/submit",
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def get_test_cases():

    response = requests.get(
        f"{BACKEND_URL}{API_PREFIX}/evaluation/test-cases",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def get_evaluation_summary():

    response = requests.get(
        f"{BACKEND_URL}{API_PREFIX}/evaluation/summary",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def get_evaluation_by_generation_type():

    response = requests.get(
        f"{BACKEND_URL}{API_PREFIX}/evaluation/by-generation-type",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def get_evaluation_by_language():

    response = requests.get(
        f"{BACKEND_URL}{API_PREFIX}/evaluation/by-language",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def get_lowest_rated_evaluations():

    response = requests.get(
        f"{BACKEND_URL}{API_PREFIX}/evaluation/lowest-rated",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()
