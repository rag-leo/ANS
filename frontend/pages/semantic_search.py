import streamlit as st

from api_client import search


st.set_page_config(
    page_title="ANIS - Semantic Search",
    layout="wide",
)

st.title("🔎 Semantic Search")

st.markdown(
    """
    Search agricultural news using
    semantic similarity powered by
    Azure OpenAI embeddings.
    """
)

st.sidebar.header(
    "Filters"
)

crop = st.sidebar.selectbox(
    "Crop",
    [
        None,
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
)

category = st.sidebar.selectbox(
    "Category",
    [
        None,
        "Weather",
        "Market Intelligence",
        "Policy",
        "Technology",
        "General",
    ],
)

source = st.sidebar.selectbox(
    "Source",
    [
        None,
        "Agrowon",
    ],
)

query = st.text_input(
    "Search Query",
    placeholder="e.g. banana market rates",
)

if st.button("Search"):

    if not query.strip():

        st.warning(
            "Please enter a search query."
        )

    else:

        with st.spinner(
            "Searching relevant articles..."
        ):

            try:

                results = search(
                    query=query,
                    crop=crop,
                    category=category,
                    source=source,
                )

                st.success(
                    f"{len(results)} results found"
                )

                st.subheader(
                    "Search Results"
                )

                for result in results:

                    st.markdown(
                        f"### {result['title']}"
                    )

                    st.write(
                        f"Similarity Score: "
                        f"{round(result['score'],4)}"
                    )

                    st.write(
                        f"Crop: "
                        f"{', '.join(result['crop']) if result['crop'] else 'N/A'}"
                    )

                    st.write(
                        f"Category: "
                        f"{result['category']}"
                    )

                    st.write(
                        f"Source: "
                        f"{result['source']}"
                    )

                    st.write(
                        result["content"]
                    )

                    st.markdown(
                        f"{result['url']}"
                    )

                    st.divider()

            except Exception as ex:

                st.error(
                    f"Search failed: {str(ex)}"
                )