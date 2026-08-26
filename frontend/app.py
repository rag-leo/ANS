import logging
from datetime import date
from typing import Optional

import httpx
import streamlit as st

from api_client import (
    search,
    generate_content,
    publish_content,
    get_notification_history,
    get_analytics_summary,
    submit_evaluation,
)


# ==========================================================
# Configuration
# ==========================================================

APP_TITLE = "Agri-News Intelligence System"
APP_SUBTITLE = "AI Notification & Information Generation using the News knowledge-base"

DEFAULT_BACKEND_URL = "http://localhost:8000"


# ==========================================================
# Logging
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================================
# Backend Configuration
# ==========================================================

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


# ==========================================================
# Backend Health Check
# ==========================================================

def check_backend_health() -> tuple[bool, Optional[str]]:
    """
    Checks if FastAPI backend is reachable.

    Returns:
        (is_healthy, error_message)
    """

    try:

        with httpx.Client(timeout=5.0) as client:

            response = client.get(
                f"{BACKEND_URL}/health"
            )

            response.raise_for_status()

            data = response.json()

            if data.get("status") == "healthy":
                return True, None

            return False, "Backend returned an unexpected status."

    except httpx.ConnectError:
        logger.exception("Unable to connect to Backend API")
        return False, "Unable to connect to Backend API."

    except httpx.TimeoutException:
        logger.exception("Backend API timed out")
        return False, "Backend API request timed out."

    except Exception as ex:
        logger.exception("Unexpected backend error")
        return False, str(ex)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Agri-news system",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# Header
# ==========================================================

st.title(f"🌾 {APP_TITLE}")
st.caption(APP_SUBTITLE)

st.divider()

query = st.text_input(
    "Search Query",
    placeholder="e.g. banana market rates"
)

# ==========================================================
# Backend Status
# ==========================================================

backend_healthy, backend_error = check_backend_health()

status_col_1, status_col_2 = st.columns([1, 6])

with status_col_1:

    if backend_healthy:
        st.success("Connected")
    else:
        st.error("Offline")

with status_col_2:

    if backend_healthy:
        st.info(
            f"Backend API reachable: {BACKEND_URL}"
        )
    else:
        st.warning(
            f"Backend unavailable: {backend_error}"
        )

# ==========================================================
# Sidebar Filters
# ==========================================================

with st.sidebar:

    st.header("Filters")

    crop = st.selectbox(
        "Crop",
        options=[
            "Select Crop",
            "कापूस",
            "सोयाबीन",
            "ऊस",
            "तूर",
            "हरभरा",
            "गहू",
            "केळी",
            "द्राक्ष",
            "कांदा",
            "मका",
        ],
        index=0,
    )

    category = st.selectbox(
        "Category",
        options=[
            "Select Category",
            "Weather",
            "Market Intelligence",
            "Policy",
            "Technology",
            "General",
        ],
        index=0,
    )

    source = st.selectbox(
        "Source",
        options=[
            "Select Source",
            "Agrowon",
        ],
        index=0,
    )

    published_date = st.date_input(
        "Published Date",
        value=date.today(),
    )

    language = st.selectbox(
        "Language",
        options=[
            "English",
            "Hindi",
            "Marathi"
        ],
        index=0,
    )

    channel = st.selectbox(
        "Channel",
        options=[
            "WhatsApp",
            "Push Notification",
            "Newsletter"
        ],
        index=0,
    )

    content_length = st.selectbox(
        "Content Length",
        options=[
            "Short",
            "Medium",
            "Long"
        ],
        index=0,
    )

    notification_count = st.slider(
        "Number of Notifications",
        min_value=1,
        max_value=3,
        value=1,
    )

    st.divider()

    search_button = st.button(
        "Search Articles",
        use_container_width=True,
        disabled=not backend_healthy
    )

# ==========================================================
# Session State
# ==========================================================

if "filters" not in st.session_state:
    st.session_state.filters = {}

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "generated_response" not in st.session_state:
    st.session_state.generated_response = None

if "generation_type" not in st.session_state:
    st.session_state.generation_type = None

if "language" not in st.session_state:
    st.session_state.language = None    

if search_button:

    crop_value = (
        None
        if crop == "Select Crop"
        else crop
    )

    category_value = (
        None
        if category == "Select Category"
        else category
    )

    source_value = (
        None
        if source == "Select Source"
        else source
    )

    channel_mapping = {
        "Push Notification": "push",
        "WhatsApp": "whatsapp",
        "Newsletter": "newsletter",
    }

    generation_type = (
        channel_mapping[channel]
    )

    st.session_state.generation_type = (
        generation_type
    )

    st.session_state.language = (
        language
    )

    st.session_state.filters = {
        "crop": crop_value,
        "category": category_value,
        "source": source_value,
        "published_date": str(published_date),
        "language": language,
        "channel": channel,
        "content_length": content_length,
        "notification_count": notification_count,
    }

    try:

        with st.spinner(
            "Searching articles..."
        ):

            results = search(
                query=query,
                crop=crop_value,
                category=category_value,
                source=source_value,
            )

            st.session_state.search_results = (
                results
            )

            generation_response = (
                generate_content(
                    query=query,
                    crop=crop_value,
                    category=category_value,
                    source=source_value,
                    language=language,
                    generation_type=(
                        generation_type
                    ),
                )
            )


            print("\n===== GENERATION RESPONSE =====")
            print(generation_response)
            print("===============================\n")

            st.session_state.generated_response = (
                generation_response
            )

    except Exception as ex:

        st.error(
            f"Error: {str(ex)}"
        )
# ==========================================================
# Main Layout
# ==========================================================

left_col, right_col = st.columns([3, 2])

# ----------------------------------------------------------
# Article Selection Area
# ----------------------------------------------------------

with left_col:

    article_container = st.container(
        border=True
    )

    with article_container:

        results = st.session_state.get(
            "search_results",
            []
        )

        if not results:

            st.warning(
                "No articles found matching the "
                "selected filters."
            )

        else:

            for result in results:

                st.markdown(
                    f"### {result['title']}"
                )

                st.write(
                    f"Similarity Score: "
                    f"{result['score']:.4f}"
                )

                if result.get("category"):

                    st.write(
                        f"Category: "
                        f"{result['category']}"
                    )

                if result.get("source"):

                    st.write(
                        f"Source: "
                        f"{result['source']}"
                    )

                st.write(
                    result["content"][:400]
                    + "..."
                )

                st.divider()
# ----------------------------------------------------------
# Generated Content Area
# ----------------------------------------------------------

with right_col:

    st.subheader("Generated Communication")

    output_container = st.container(
        border=True
    )

    with output_container:

        generated_response = (
            st.session_state.get(
                "generated_response"
            )
        )

        if generated_response:

            if (
                generated_response["article_count"]
                == 0
            ):

                st.warning(
                    "No articles matched the selected filters."
                )

                st.info(
                    "Try changing crop, category, source, or search query."
                )

            else:

                st.markdown(
                    f"### {generated_response['title']}"
                )

                st.text_area(
                    "Generated Communication",
                    generated_response["content"],
                    height=400,
                )

                st.caption(
                    f"Articles Used: "
                    f"{generated_response['article_count']}"
                )

                with st.expander(
                    "📚 Source Articles"
                ):

                    for article in (
                        generated_response[
                            "source_articles"
                        ]
                    ):

                        st.write(
                            article["title"]
                        )

                        st.caption(
                            f"""
                        Crop: {article['crop']}
                        |
                        Source: {article['source']}
                        |
                        Similarity: {article['score']}
                        """
                        )

                    st.divider()                

                if st.button(
                    "✅ Mark as Published",
                    use_container_width=True,
                ):

                    try:

                        publish_content(
                            article_ids=(
                                generated_response[
                                    "article_ids"
                                ]
                            ),
                            generation_type=(
                                st.session_state[
                                    "generation_type"
                                ]
                            ),
                            language=(
                                st.session_state[
                                    "language"
                                ]
                            ),
                        )

                        st.success(
                            "Content marked as published."
                        )

                    except Exception as ex:

                        st.error(
                            f"Publishing failed: {str(ex)}"
                        )

        else:

            st.info(
                "Generated content will appear here."
            )

st.markdown(
    "## ✅ Evaluation"
)

retrieval_relevance = st.slider(
    "Retrieval Relevance",
    1,
    5,
    3,
)

crop_focus = st.slider(
    "Crop Focus",
    1,
    5,
    3,
)

faithfulness = st.slider(
    "Faithfulness",
    1,
    5,
    3,
)

communication_quality = st.slider(
    "Communication Quality",
    1,
    5,
    3,
)

language_compliance = st.checkbox(
    "Output follows requested language"
)

comments = st.text_area(
    "Comments"
)

if st.button(
    "Save Evaluation"
):

    payload = {
        "query": query,
        "crop": crop,
        "category": category,
        "language": language,
        "generation_type": generation_type,
        "retrieval_relevance": retrieval_relevance,
        "crop_focus": crop_focus,
        "faithfulness": faithfulness,
        "communication_quality": communication_quality,
        "language_compliance": language_compliance,
        "comments": comments,
    }

    submit_evaluation(
        payload
    )

    st.success(
        "Evaluation saved successfully."
    )
# ==========================================================
# Footer
# ==========================================================

st.divider()

st.subheader(
    "📋 Published Notifications"
)

import pandas as pd

history = get_notification_history()

if history:

    df = pd.DataFrame(history)

    st.dataframe(
        df[
            [
                "published_at",
                "title",
                "crop",
                "source",
                "generation_type",
                "language",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    f"Environment: Connected to {BACKEND_URL}"
    if backend_healthy
    else "Backend unavailable"
)


# =====================================================

st.subheader(
    "📊 ANS Analytics"
)

analytics = (
    get_analytics_summary()
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Articles",
    analytics[
        "total_articles"
    ],
)

col2.metric(
    "Chunks",
    analytics[
        "total_chunks"
    ],
)

col3.metric(
    "Published",
    analytics[
        "published_notifications"
    ],
)

generation_map = {
    item["generation_type"]:
    item["count"]
        for item in analytics["generation_counts"]
}

col1,col2, col3 = st.columns(3)

col1.metric(
    "Push",
    generation_map.get(
        "push",
        0,
   ),
)

col2.metric(
    "WhatsApp",
    generation_map.get(
       "whatsapp",
        0,
    ),
)

col3.metric(
    "Newsletter",
    generation_map.get(
        "newsletter",
        0,
    ),
)

st.markdown(
    "### 📢 Generation Breakdown"
)

st.markdown(
    "### 🌐 Language Usage"
)

st.dataframe(
    analytics["language_counts"],    
    use_container_width=True,
)

st.dataframe(
    analytics[
        "generation_counts"
    ],
    use_container_width=True,
)

st.markdown(
    "### 🌾 Top Published Crops"
)

st.dataframe(
    analytics[
        "top_crops"
    ],
    use_container_width=True,
)

st.markdown(
    "### 📰 Top Sources"
)

st.dataframe(
    analytics[
        "top_sources"
    ],
    use_container_width=True,
)

st.markdown(
    "### 📈 Publication Trend"
)

trend_df = pd.DataFrame(
    analytics["publication_trend"]
)

if not trend_df.empty:

    trend_df = trend_df.rename(
       columns={
            "publish_date": "Date",
            "count": "Published"
        }
    )
    st.line_chart(
        trend_df.set_index("Date")
    )