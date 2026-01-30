import streamlit as st
from gtts import gTTS
import tempfile
import os
from langdetect import detect, lang_detect_exception
from deep_translator import GoogleTranslator
import pycountry
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Globalize",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Globalize – Universal Translator")

# -------------------- FUNCTIONS --------------------
def read_aloud_streamlit(text, language="en"):
    tts = gTTS(text=text, lang=language)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        st.audio(fp.name, format="audio/mp3")

def generate_wordcloud(text):
    clean_text = re.sub(r"[^a-zA-Z\s]", "", text)
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white"
    ).generate(clean_text)

    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    return fig

# -------------------- INPUT UI --------------------
col1, col2 = st.columns(2)

with col1:
    paragraph = st.text_area("Enter one paragraph:")

with col2:
    all_languages = sorted(
        [lang.name for lang in pycountry.languages if hasattr(lang, "alpha_2")]
    )
    target_languages_input = st.multiselect(
        "Select target languages:",
        all_languages
    )

# -------------------- READ ALOUD ORIGINAL --------------------
if st.button("Read Aloud (Original)"):
    if paragraph.strip():
        read_aloud_streamlit(paragraph)
    else:
        st.warning("Please enter text first.")

# -------------------- LANGUAGE DETECTION --------------------
paragraph_language = "en"

if paragraph.strip():
    try:
        paragraph_language = detect(paragraph)
        language_name = pycountry.languages.get(alpha_2=paragraph_language).name
        st.info(f"Detected language: {language_name}")
    except lang_detect_exception.LangDetectException:
        st.warning("Could not detect language. Defaulting to English.")
    except Exception:
        st.warning("Language detection issue.")

# -------------------- TRANSLATE TO ENGLISH --------------------
if paragraph_language != "en" and paragraph.strip():
    translated_english = GoogleTranslator(
        source="auto", target="en"
    ).translate(paragraph)

    st.subheader("Translated to Universal Language (English)")
    st.write(translated_english)
else:
    translated_english = paragraph

# -------------------- WORD CLOUD --------------------
if translated_english.strip():
    st.sidebar.subheader("Word Cloud")
    wc_fig = generate_wordcloud(translated_english)
    st.sidebar.pyplot(wc_fig)

# -------------------- TRANSLATE & READ ALOUD --------------------
if st.button("Translate and Read Aloud"):
    if not paragraph.strip():
        st.warning("Please enter text first.")
    elif not target_languages_input:
        st.warning("Please select at least one language.")
    else:
        for lang_name in target_languages_input:
            try:
                lang_code = pycountry.languages.lookup(lang_name).alpha_2

                translated_text = GoogleTranslator(
                    source="auto", target=lang_code
                ).translate(paragraph)

                st.subheader(f"Translated to {lang_name}")
                st.write(translated_text)

                read_aloud_streamlit(translated_text, lang_code)

            except Exception as e:
                st.error(f"Translation failed for {lang_name}: {e}")

# -------------------- FOOTER --------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit, NLP & Deep Translator")


