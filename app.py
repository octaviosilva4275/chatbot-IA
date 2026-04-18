import os
from typing import List, Dict

import streamlit as st
from dotenv import load_dotenv
from google import genai


# -----------------------------------------------------
# Configuração inicial
# -----------------------------------------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

if not API_KEY:
    raise RuntimeError(
        "Chave da API não encontrada. Crie um arquivo .env com GEMINI_API_KEY=sua_chave"
    )

client = genai.Client(api_key=API_KEY)

st.set_page_config(
    page_title="Chat Gemini",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------
# Estilo visual
# -----------------------------------------------------
CUSTOM_CSS = """
<style>
    .main {
        padding-top: 1rem;
    }

    .block-container {
        max-width: 1000px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 0.4rem;
    }

    .chat-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .chat-subtitle {
        color: #777;
        margin-bottom: 1rem;
    }

    .small-muted {s
        color: #888;
        font-size: 0.9rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)