from __future__ import annotations

import streamlit as st

from src.chat_state import ContextConfig, approximate_tokens, build_context_with_summary
from src.database import (
    add_message,
    auto_title_from_text,
    create_conversation,
    delete_conversation,
    get_messages,
    init_db,
    list_conversations,
    rename_conversation,
)
from src.gemini_client import GeminiClient
from src.ui import inject_css, read_uploaded_files, render_chat_messages, render_welcome


st.set_page_config(
    page_title="Chat Gemini Pro",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
inject_css()


if "active_conversation_id" not in st.session_state:
    existing = list_conversations()
    st.session_state.active_conversation_id = (
        existing[0]["id"] if existing else create_conversation()
    )


with st.sidebar:
    st.title("💬 Seus chats")

    if st.button("+ Novo chat", use_container_width=True):
        st.session_state.active_conversation_id = create_conversation()
        st.rerun()

    conversations = list_conversations()
    if not conversations:
        st.info("Nenhuma conversa ainda.")
    else:
        for conv in conversations:
            cols = st.columns([4, 1])
            active = conv["id"] == st.session_state.active_conversation_id
            label = ("🟢 " if active else "") + conv["title"]
            if cols[0].button(label, key=f"select_{conv['id']}", use_container_width=True):
                st.session_state.active_conversation_id = conv["id"]
                st.rerun()
            if cols[1].button("🗑️", key=f"del_{conv['id']}"):
                delete_conversation(conv["id"])
                if st.session_state.active_conversation_id == conv["id"]:
                    remain = list_conversations()
                    st.session_state.active_conversation_id = (
                        remain[0]["id"] if remain else create_conversation()
                    )
                st.rerun()

    st.divider()
    st.subheader("⚙️ Configurações")
    model_name = st.selectbox("Modelo", ["gemini-2.5-flash", "gemini-2.5-pro"])
    temperature = st.slider("Temperatura", 0.0, 1.5, 0.7, 0.1)
    max_output_tokens = st.slider("Max output tokens", 128, 4096, 1024, 128)
    use_streaming = st.toggle("Streaming", value=True)
    system_prompt = st.text_area(
        "System prompt",
        value="Você é um assistente útil, objetivo e didático.",
        height=120,
    )

    st.divider()
    uploaded_files = st.file_uploader(
        "Upload de arquivos",
        type=["pdf", "txt", "docx", "csv"],
        accept_multiple_files=True,
        help="Envie documentos para adicionar contexto na próxima mensagem.",
    )


active_id = st.session_state.active_conversation_id
messages = get_messages(active_id)

if not messages:
    suggested = render_welcome()
else:
    suggested = None

render_chat_messages(messages)

prompt = st.chat_input("Digite sua mensagem...")
if not prompt and suggested:
    prompt = suggested

if prompt:
    file_context = read_uploaded_files(uploaded_files or [])
    user_content = prompt
    if file_context:
        user_content += (
            "\n\nContexto extraído de arquivos enviados (use se relevante):\n" + file_context
        )

    add_message(active_id, "user", user_content)
    st.chat_message("user").markdown(prompt)

    try:
        client = GeminiClient(model_name=model_name)

        history = get_messages(active_id)
        recent, summary = build_context_with_summary(history, ContextConfig())

        effective_messages = recent
        if summary:
            effective_messages = [{"role": "user", "content": summary}] + recent

        full_answer = client.generate(
            messages=effective_messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        with st.chat_message("assistant"):
            if use_streaming:
                def chunks(text: str):
                    for word in text.split(" "):
                        yield word + " "
                st.write_stream(chunks(full_answer))
            else:
                st.markdown(full_answer)

            with st.expander("Ver markdown bruto / copiar"):
                st.code(full_answer, language="markdown")

        add_message(active_id, "assistant", full_answer)

        if len(history) <= 1:
            rename_conversation(active_id, auto_title_from_text(prompt))

        token_estimate = approximate_tokens(prompt + full_answer)
        st.caption(f"Tokens aproximados nesta interação: {token_estimate}")

    except RuntimeError as err:
        st.error(
            "Não encontrei a chave da API. Configure GEMINI_API_KEY no arquivo .env para continuar."
        )
        st.exception(err)
    except Exception as err:
        st.error(
            "Não consegui falar com o Gemini agora. Tente novamente em alguns segundos."
        )
        st.exception(err)
