
import os
import json
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from groq import Groq, RateLimitError, AuthenticationError, APIError

st.set_page_config(
    page_title="Lingua Translator",
    page_icon="🌐",
    layout="wide"
)

load_dotenv()
MODEL_NAME = "qwen/qwen3.8-27b"

LANGUAGES = {
    "Auto Detect": "automatically detect the source language",
    "English": "English",
    "Hindi": "Hindi",
    "Spanish": "Spanish",
    "French": "French",
    "German": "German",
    "Japanese": "Japanese",
    "Korean": "Korean",
    "Chinese": "Chinese (Simplified)",
    "Telugu": "Telugu",
    "Tamil": "Tamil",
    "Bengali": "Bengali",
    "Arabic": "Arabic",
    "Portuguese": "Portuguese",
    "Russian": "Russian",
    "Italian": "Italian",
    "Malayalam": "Malayalam",
    "Marathi": "Marathi",
    "Urdu": "Urdu",
}

# -------------------- SESSION STATE --------------------
defaults = {
    "source_choice": "English",
    "target_choice": "Hindi",
    "input_text": "",
    "translated_text": "",
    "translation_error": "",
    "translation_output": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------- STYLING --------------------
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at top left, #312e81 0%, transparent 45%),
        linear-gradient(135deg, #0f172a 0%, #17152f 55%, #241447 100%);
    color: #f8fafc;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.main-title {
    text-align: center;
    font-size: 44px;
    font-weight: 850;
    letter-spacing: -1px;
    color: #c4b5fd !important;
    margin-bottom: 4px;
}

.subtitle {
    text-align: center;
    color: #cbd5e1 !important;
    font-size: 17px;
    margin-bottom: 28px;
}

.info-card {
    background: linear-gradient(120deg, #1e1b4b, #252044);
    color: #e2e8f0 !important;
    padding: 21px 24px;
    border-radius: 18px;
    border: 1px solid #494080;
    margin-bottom: 24px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18);
}

.stSubheader,
.stTextArea label,
.stSelectbox label {
    color: #e0e7ff !important;
    font-weight: 700 !important;
}

.stTextArea textarea {
    background: #171b30 !important;
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
    border: 1px solid #4b4777 !important;
    border-radius: 16px !important;
    padding: 18px !important;
    font-size: 18px !important;
    line-height: 1.7 !important;
    caret-color: #c4b5fd !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
}

.stTextArea textarea::placeholder {
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
}

.stTextArea textarea:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 2px rgba(167, 139, 250, 0.2);
}

.stCaption {
    color: #a5b4fc !important;
}

.stSelectbox [data-baseweb="select"] > div {
    background: #171b30;
    color: #f8fafc;
    border-color: #4b4777;
    border-radius: 11px;
}

div.stButton > button {
    border-radius: 12px;
    min-height: 46px;
    font-weight: 700;
    background: linear-gradient(100deg, #6366f1, #7c3aed);
    color: #ffffff;
    border: 1px solid #818cf8;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background: linear-gradient(100deg, #4f46e5, #6d28d9);
    border-color: #c4b5fd;
    color: white;
    transform: translateY(-1px);
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

.footer {
    text-align: center;
    color: #94a3b8 !important;
    margin-top: 36px;
    padding: 18px;
    font-size: 13px;
    border-top: 1px solid #37345c;
}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown(
    '<div class="main-title">🌐 Lingua Translator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Translate naturally. Communicate without boundaries.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="info-card">
    <b>✨ Welcome to Lingua Translator</b><br><br>
    Choose your source and target languages, enter your text, and let
    Groq AI translate while preserving the original meaning and tone.
</div>
""", unsafe_allow_html=True)

# -------------------- LANGUAGE SELECTORS --------------------
source_col, swap_col, target_col = st.columns([5, 1, 5])

with source_col:
    source_language = st.selectbox(
        "🌍 Translate from",
        list(LANGUAGES.keys()),
        key="source_choice"
    )

with swap_col:
    st.write("")
    st.write("")
    swap_clicked = st.button("⇄ Swap", use_container_width=True)

with target_col:
    target_language = st.selectbox(
        "🌎 Translate to",
        list(LANGUAGES.keys())[1:],
        key="target_choice"
    )

if swap_clicked:
    if source_language == "Auto Detect":
        st.warning("Choose a specific source language before swapping.")
    else:
        st.session_state.source_choice = target_language
        st.session_state.target_choice = source_language
        st.rerun()

# -------------------- TRANSLATION FUNCTION --------------------
def translate_text(text, source_language, target_language):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY was not found in your .env file."
        )

    client = Groq(api_key=api_key)

    prompt = f"""
Translate the following text into {LANGUAGES[target_language]}.
Source language: {LANGUAGES[source_language]}.

IMPORTANT TRANSLATION INSTRUCTIONS:

1. Translate the actual meaning and intention of the text, not merely
   its pronunciation, spelling, or individual words.

2. The source may contain Telugu written using English letters.
   This is called Roman Telugu or transliterated Telugu.
   For example, Telugu speakers commonly type Telugu words and sentences
   using the Latin alphabet instead of Telugu script.

3. If the selected source language is Telugu, treat the input as Telugu
   even when every word is written using English letters.
   Do not assume that Latin-script text is English.

4. If the source language is Auto Detect, check whether the input could
   be Roman Telugu. Consider Telugu vocabulary, common transliteration
   patterns, sentence structure, conversational context, and spelling
   variations before deciding that the text is English.

5. Understand informal Telugu, everyday spoken Telugu, regional wording,
   slang, abbreviations, spelling mistakes, and colloquial expressions.
   Telugu speakers may spell the same word in different ways when typing
   it using English letters. Interpret the intended word from context.

6. Translate Telugu swear words, insults, rude expressions, and profanity
   according to their actual meaning and intensity. Do not automatically
   censor them, replace them with polite language, or soften their meaning.
   Use the closest natural equivalent in the target language.

7. Preserve the original tone, including humour, anger, sarcasm, affection,
   informality, and vulgarity when present. Do not make an offensive
   expression more offensive than the original.

8. Use the surrounding sentence to understand ambiguous words. Do not
   translate Roman Telugu word by word as if it were English phonetics.
   If a short expression is ambiguous, choose the most likely meaning
   supported by the language and context.

9. When translating into Telugu, provide the translation in Telugu script.
   When translating into another language, produce natural, fluent text
   in that target language rather than transliterating the source.

10. Preserve names, numbers, and formatting where appropriate.
    Do not add explanations, definitions, transliterations, or labels.

Return ONLY the translated text.

Text to translate:
{text}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful multilingual translation engine "
                    "specializing in accurate, natural, context-aware "
                    "translations. You understand Telugu written in "
                    "English letters, also called Roman Telugu. When "
                    "translating, recognize colloquial language, slang, "
                    "transliterated words, spelling variations, insults, "
                    "and profanity. Preserve the intended meaning and "
                    "original tone. Do not confuse Roman Telugu with "
                    "English merely because it uses Latin letters. "
                    "Use context to interpret ambiguous expressions and "
                    "return only the translation."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_completion_tokens=2048
    )

    if not response.choices:
        raise ValueError("Groq returned no response choices.")

    result = response.choices[0].message.content

    if not result or not result.strip():
        raise ValueError("Groq returned an empty translation.")

    return result.strip()

# -------------------- TRANSLATION CALLBACK --------------------
def perform_translation():
    text = st.session_state.input_text.strip()
    source = st.session_state.source_choice
    target = st.session_state.target_choice

    st.session_state.translated_text = ""
    st.session_state.translation_output = ""
    st.session_state.translation_error = ""

    if not text:
        st.session_state.translation_error = (
            "Please enter some text first."
        )
        return

    if source == target:
        st.session_state.translation_error = (
            "Select two different languages."
        )
        return

    try:
        with st.spinner("Translating with Groq AI..."):
            result = translate_text(text, source, target)

        st.session_state.translated_text = result
        st.session_state.translation_output = result

    except AuthenticationError:
        st.session_state.translation_error = (
            "Groq rejected the API key. Check your .env file."
        )
    except RateLimitError as error:
        st.session_state.translation_error = f"Rate limit: {error}"
    except APIError as error:
        st.session_state.translation_error = f"Groq API error: {error}"
    except Exception as error:
        st.session_state.translation_error = (
            f"{type(error).__name__}: {error}"
        )

# -------------------- INPUT AND OUTPUT PANELS --------------------
input_col, output_col = st.columns(2, gap="medium")

with input_col:
    st.subheader("📝 Your Text")

    input_text = st.text_area(
        "Enter text to translate",
        height=280,
        max_chars=5000,
        placeholder="Type or paste your text here...",
        label_visibility="collapsed",
        key="input_text"
    )

    st.caption(f"{len(input_text)} / 5000 characters")

with output_col:
    st.subheader("📄 Translation")

    st.text_area(
        "Translated result",
        height=280,
        placeholder="Your translation will appear here...",
        disabled=True,
        label_visibility="collapsed",
        key="translation_output"
    )

# -------------------- TRANSLATE BUTTON --------------------
st.button(
    "🌐 Translate Text",
    type="primary",
    use_container_width=True,
    on_click=perform_translation
)

# -------------------- STATUS AND COPY --------------------
if st.session_state.translation_error:
    st.error(st.session_state.translation_error)

elif st.session_state.translated_text:
    st.success("Translation completed successfully!")

    # Copy button inside a small HTML component.
    # The translated text is safely encoded as a JavaScript string.
    translation_json = json.dumps(st.session_state.translated_text)

    components.html(
        f"""
        <div style="
            font-family: Arial, sans-serif;
            background: transparent;
            padding: 4px 0;
        ">
            <button id="copy-translation" style="
                background: linear-gradient(100deg, #6366f1, #7c3aed);
                color: white;
                border: 1px solid #818cf8;
                border-radius: 10px;
                padding: 12px 18px;
                font-size: 14px;
                font-weight: 700;
                cursor: pointer;
            ">📋 Copy Translation</button>
            <span id="copy-status" style="
                color: #c4b5fd;
                margin-left: 12px;
                font-size: 13px;
            "></span>
        </div>
        <script>
        const translatedText = {translation_json};
        const copyButton = document.getElementById("copy-translation");
        const copyStatus = document.getElementById("copy-status");

        copyButton.addEventListener("click", async () => {{
            try {{
                await navigator.clipboard.writeText(translatedText);
                copyStatus.textContent = "Copied!";
            }} catch (error) {{
                copyStatus.textContent =
                    "Clipboard unavailable. Select the text in the box and press Ctrl+C.";
            }}
        }});
        </script>
        """,
        height=55
    )

# -------------------- CLEAR BUTTON --------------------
def clear_text():
    st.session_state.input_text = ""
    st.session_state.translated_text = ""
    st.session_state.translation_output = ""
    st.session_state.translation_error = ""

st.button("🗑️ Clear Text", on_click=clear_text)

# -------------------- FOOTER --------------------
st.markdown("""
<div class="footer">
    Lingua Translator · Powered by Groq AI
</div>
""", unsafe_allow_html=True)
