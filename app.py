import streamlit as st

from src.config import LANGUAGE_OPTIONS, LENGTH_OPTIONS
from src.post_composer import PostComposer
from src.style_examples import StyleExampleLibrary

st.set_page_config(page_title="Post Composer", page_icon="✍️")


@st.cache_resource
def load_composer() -> PostComposer:
    return PostComposer(StyleExampleLibrary())


def main():
    st.subheader("✍️ AI Post Composer")
    st.caption("Draft a new LinkedIn post styled after your own past writing.")

    composer = load_composer()
    tags = composer.style_library.get_tags()

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_tag = st.selectbox("Topic", options=tags)
    with col2:
        selected_length = st.selectbox("Length", options=LENGTH_OPTIONS)
    with col3:
        selected_language = st.selectbox("Language", options=LANGUAGE_OPTIONS)

    if st.button("Generate", type="primary"):
        with st.spinner("Writing your post..."):
            try:
                post = composer.generate(selected_length, selected_language, selected_tag)
                st.write(post)
            except Exception as exc:
                st.error(f"Couldn't generate a post: {exc}")


if __name__ == "__main__":
    main()
