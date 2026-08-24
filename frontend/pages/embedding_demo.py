import streamlit as st

from api_client import generate_embedding


st.title("Embedding Demo")

text = st.text_area(
    "Enter text:",
)

if st.button("Generate Embedding"):

    result = generate_embedding(text)

    st.success(
        f"Dimensions: {result['dimensions']}"
    )

    st.write(
        result["embedding"][:10]
    )