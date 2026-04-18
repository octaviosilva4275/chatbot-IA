import os

import streamlit as st
from dotenv import load_dotenv

from src.chat_state import (
    build_generation_prompt,
    default_generation_settings,
    ensure_session_state,
    generate_chat_title,
    get_effective_system_prompt,
)
from src.database import ChatDatabase
from src.gemini_client import GeminiClient
from src.ui import (
    apply_global_styles,
    render_chat_header,
    render_chat_messages,
    render_empty_state,
    render_error_message,
    render_file_uploader,
    render_response_tools,
    render_sidebar,
)


def _is_safe_mode_enabled() -> bool:
    env_value = os.getenv("SAFE_MODE", "").strip().lower()
    if env_value in {"1", "true", "yes", "on"}:
        return True

    query_value = str(st.query_params.get("safe_mode", "")).strip().lower()
    return query_value in {"1", "true", "yes", "on"}


def _resolve_api_key() -> str | None:
    # Prioriza st.secrets para deploy (ex.: Streamlit Cloud) e
    # mantém fallback para variáveis de ambiente em execução local.
    secrets_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    if secrets_key:
        return str(secrets_key)

    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def bootstrap() -> tuple[ChatDatabase, GeminiClient]:
    load_dotenv()

    st.set_page_config(
        page_title="Chat Workspace",
        page_icon="AI",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    ensure_session_state()
    if _is_safe_mode_enabled():
        st.info(
            "Modo seguro ativo: estilos customizados foram desativados. "
            "Use este modo para diagnosticar problemas de renderizacao."
        )
    else:
        apply_global_styles()

    api_key = _resolve_api_key()
    database = ChatDatabase()
    client = GeminiClient(api_key=api_key)
    return database, client


def ensure_active_chat(database: ChatDatabase) -> int:
    active_chat_id = st.session_state.get("active_chat_id")
    if active_chat_id is not None and database.chat_exists(active_chat_id):
        return active_chat_id

    chats = database.list_chats()
    if chats:
        active_chat_id = chats[0]["id"]
    else:
        active_chat_id = database.create_chat()

    st.session_state.active_chat_id = active_chat_id
    return active_chat_id


def create_new_chat(database: ChatDatabase) -> int:
    chat_id = database.create_chat()
    st.session_state.active_chat_id = chat_id
    st.session_state.pending_file_context = None
    st.session_state.file_context_consumed = True
    return chat_id


def delete_current_chat(database: ChatDatabase, chat_id: int) -> None:
    database.delete_chat(chat_id)
    chats = database.list_chats()
    st.session_state.active_chat_id = chats[0]["id"] if chats else database.create_chat()
    st.session_state.pending_file_context = None
    st.session_state.file_context_consumed = True


def maybe_store_auto_title(database: ChatDatabase, chat_id: int, user_message: str) -> None:
    chat = database.get_chat(chat_id)
    if not chat:
        return
    if chat["title"] != "Novo chat":
        return

    title = generate_chat_title(user_message)
    database.rename_chat(chat_id, title)


def handle_user_message(
    database: ChatDatabase,
    client: GeminiClient,
    chat_id: int,
    user_message: str,
) -> None:
    file_context = st.session_state.get("pending_file_context")

    database.add_message(chat_id, "user", user_message)
    maybe_store_auto_title(database, chat_id, user_message)

    with st.chat_message("user"):
        st.markdown('<div class="message-label">Voce</div>', unsafe_allow_html=True)
        st.markdown(user_message)

    messages = database.get_messages(chat_id)
    settings = st.session_state.generation_settings
    prompt, token_estimate = build_generation_prompt(
        messages=messages,
        system_prompt=get_effective_system_prompt(settings),
        transient_context=file_context,
    )

    with st.chat_message("assistant"):
        st.markdown('<div class="message-label">Assistente</div>', unsafe_allow_html=True)
        placeholder = st.empty()
        consumed_file_context = False
        try:
            response_text = client.generate_response(
                prompt=prompt,
                model=settings["model"],
                temperature=settings["temperature"],
                max_output_tokens=settings["max_output_tokens"],
                stream=settings["stream"],
                placeholder=placeholder,
            )
            render_response_tools(
                response_text,
                key_suffix=str(len(messages)),
                token_estimate=token_estimate,
            )
            consumed_file_context = True
        except Exception as exc:
            response_text = render_error_message(exc)
            placeholder.error(response_text)

    database.add_message(chat_id, "assistant", response_text)
    if consumed_file_context:
        st.session_state.pending_file_context = None
        st.session_state.file_context_consumed = bool(file_context)


def main() -> None:
    database, client = bootstrap()
    st.session_state.generation_settings = st.session_state.get(
        "generation_settings",
        default_generation_settings(),
    )

    active_chat_id = ensure_active_chat(database)
    sidebar_action = render_sidebar(
        database=database,
        active_chat_id=active_chat_id,
        settings=st.session_state.generation_settings,
    )

    if sidebar_action == "new_chat":
        create_new_chat(database)
        st.rerun()
    if sidebar_action == "delete_chat":
        delete_current_chat(database, active_chat_id)
        st.rerun()
    if isinstance(sidebar_action, int):
        st.session_state.active_chat_id = sidebar_action
        st.rerun()

    active_chat_id = ensure_active_chat(database)
    messages = database.get_messages(active_chat_id)
    chat = database.get_chat(active_chat_id)
    chat_count = len(database.list_chats())

    render_chat_header(
        chat_title=chat["title"] if chat else "Novo chat",
        settings=st.session_state.generation_settings,
        chat_count=chat_count,
        message_count=len(messages),
    )
    render_file_uploader()

    selected_prompt = None
    if messages:
        render_chat_messages(messages)
    else:
        selected_prompt = render_empty_state()

    prompt = st.chat_input("Digite sua mensagem...")
    prompt = prompt or selected_prompt
    if prompt:
        handle_user_message(database, client, active_chat_id, prompt)
        st.rerun()


if __name__ == "__main__":
    main()
