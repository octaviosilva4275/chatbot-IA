import math

import streamlit as st


MAX_RECENT_MESSAGES = 10
SUMMARY_CHAR_LIMIT = 900


def default_generation_settings() -> dict:
    return {
        "model": "gemini-2.5-flash",
        "temperature": 0.7,
        "max_output_tokens": 2048,
        "stream": True,
        "system_prompt": "",
    }


def ensure_session_state() -> None:
    if "active_chat_id" not in st.session_state:
        st.session_state.active_chat_id = None
    if "pending_file_context" not in st.session_state:
        st.session_state.pending_file_context = None
    if "uploaded_file_signature" not in st.session_state:
        st.session_state.uploaded_file_signature = None
    if "uploaded_file_name" not in st.session_state:
        st.session_state.uploaded_file_name = None
    if "file_context_consumed" not in st.session_state:
        st.session_state.file_context_consumed = False


def generate_chat_title(user_message: str) -> str:
    cleaned = " ".join(user_message.split())
    if not cleaned:
        return "Novo chat"
    if len(cleaned) <= 45:
        return cleaned
    return f"{cleaned[:42].rstrip()}..."


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def summarize_older_messages(messages: list[dict]) -> str:
    if not messages:
        return ""

    parts = []
    for message in messages:
        role = "Usuario" if message["role"] == "user" else "Assistente"
        preview = " ".join(message["content"].split())
        parts.append(f"{role}: {preview[:180]}")

    summary = "\n".join(parts)
    if len(summary) > SUMMARY_CHAR_LIMIT:
        summary = f"{summary[:SUMMARY_CHAR_LIMIT].rstrip()}..."
    return summary


def get_effective_system_prompt(settings: dict) -> str:
    base_prompt = (
        "Voce e um assistente util, claro e confiavel. "
        "Responda em portugues do Brasil, usando markdown quando fizer sentido."
    )
    custom_prompt = settings.get("system_prompt", "").strip()
    if not custom_prompt:
        return base_prompt
    return f"{base_prompt}\n\nInstrucoes adicionais:\n{custom_prompt}"


def build_generation_prompt(
    messages: list[dict],
    system_prompt: str,
    transient_context: str | None = None,
) -> tuple[str, int]:
    recent_messages = messages[-MAX_RECENT_MESSAGES:]
    older_messages = messages[:-MAX_RECENT_MESSAGES]
    summary = summarize_older_messages(older_messages)

    prompt_parts = [f"Sistema:\n{system_prompt}"]

    if summary:
        prompt_parts.append(f"Resumo da conversa anterior:\n{summary}")

    if recent_messages:
        rendered_recent = []
        for message in recent_messages:
            role = "Usuario" if message["role"] == "user" else "Assistente"
            rendered_recent.append(f"{role}: {message['content']}")
        prompt_parts.append("Mensagens recentes:\n" + "\n\n".join(rendered_recent))

    if transient_context:
        prompt_parts.append(
            "Contexto adicional anexado nesta rodada:\n"
            f"{transient_context}"
        )

    prompt_parts.append(
        "Tarefa:\n"
        "Responda a ultima mensagem do usuario considerando o contexto acima. "
        "Foque no pedido atual e use o contexto adicional apenas se ele ajudar."
    )

    prompt = "\n\n".join(prompt_parts)
    token_estimate = estimate_tokens(prompt)
    return prompt, token_estimate
