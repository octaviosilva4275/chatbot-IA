from __future__ import annotations

import hashlib
import html
from io import BytesIO

import streamlit as st


MAX_FILE_CONTEXT_CHARS = 12000
SUGGESTED_PROMPTS = [
    {
        "tag": "Codigo",
        "title": "Explique um trecho de codigo",
        "body": "Entenda rapidamente o que um trecho faz, os riscos e como melhorar.",
        "cta": "Explicar codigo",
        "prompt": "Explique este codigo passo a passo, diga o que cada parte faz e sugira melhorias.",
    },
    {
        "tag": "Resumo",
        "title": "Resuma um texto ou documento",
        "body": "Transforme um material longo em pontos claros e acionaveis.",
        "cta": "Resumir material",
        "prompt": "Resuma este material em topicos objetivos, destaque o principal e termine com proximos passos.",
    },
    {
        "tag": "Plano",
        "title": "Monte um plano de estudo",
        "body": "Estruture uma rotina realista com metas semanais e pratica.",
        "cta": "Criar plano",
        "prompt": "Monte um plano de estudos de 4 semanas com metas, exercicios e revisoes.",
    },
    {
        "tag": "Texto",
        "title": "Melhore uma escrita",
        "body": "Refine um texto com mais clareza, ritmo e impacto.",
        "cta": "Melhorar texto",
        "prompt": "Reescreva este texto com mais clareza, fluidez e impacto, mantendo um tom natural.",
    },
]


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Source+Serif+4:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

            :root {
                --bg: #f4f7fb;
                --bg-soft: #fbfdff;
                --panel: #ffffff;
                --panel-soft: #f7f9fc;
                --panel-muted: #edf2fa;
                --border: #dce5f1;
                --border-strong: #c8d6ea;
                --text: #172033;
                --muted: #5a667e;
                --accent: #2f6fff;
                --accent-soft: #e9f0ff;
                --success-soft: #e6f4ec;
                --shadow: 0 14px 34px rgba(23, 32, 51, 0.08);
                --shadow-soft: 0 8px 18px rgba(23, 32, 51, 0.05);
                --radius-xl: 26px;
                --radius-lg: 20px;
                --radius-md: 16px;
            }

            html, body, [class*="css"] {
                font-family: "Instrument Sans", sans-serif;
                color-scheme: light;
            }

            .stApp {
                color: var(--text);
                background:
                    radial-gradient(circle at top left, rgba(47, 111, 255, 0.14), transparent 30%),
                    radial-gradient(circle at 90% -10%, rgba(10, 196, 255, 0.1), transparent 35%),
                    linear-gradient(180deg, #f8fbff 0%, #f2f6fc 100%);
            }

            header[data-testid="stHeader"] {
                background: rgba(248, 251, 255, 0.82) !important;
                border-bottom: 1px solid var(--border);
                backdrop-filter: blur(8px);
            }

            [data-testid="stDecoration"] {
                background: transparent !important;
            }

            [data-testid="stToolbar"] {
                right: 1rem;
            }

            .block-container {
                max-width: 1120px;
                padding-top: 1.1rem;
                padding-bottom: 6.5rem;
            }

            section[data-testid="stSidebar"] > div {
                background: #f5f8fd;
                border-right: 1px solid var(--border);
            }

            section[data-testid="stSidebar"] .block-container {
                padding-top: 1rem;
            }

            h1, h2, h3 {
                font-family: "Source Serif 4", serif;
                color: var(--text);
                letter-spacing: -0.03em;
            }

            p, label, .stCaption {
                color: var(--muted);
            }

            .stButton > button,
            .stDownloadButton > button {
                width: 100%;
                min-height: 46px;
                border-radius: 14px;
                border: 1px solid var(--border);
                background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
                color: var(--text);
                box-shadow: none;
                transition: background 180ms ease, border-color 180ms ease, transform 180ms ease, box-shadow 180ms ease;
                cursor: pointer;
                font-weight: 600;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover {
                background: #ffffff;
                border-color: #b8c9e4;
                transform: translateY(-1px);
                box-shadow: var(--shadow-soft);
            }

            .stButton > button[kind="primary"] {
                background: linear-gradient(180deg, #3f7dff 0%, #2f6fff 100%);
                color: white;
                border-color: #2f6fff;
            }

            .stButton > button[kind="primary"]:hover {
                background: linear-gradient(180deg, #4a86ff 0%, #3b79ff 100%);
                border-color: #3b79ff;
            }

            .stButton > button:focus-visible,
            .stDownloadButton > button:focus-visible,
            textarea:focus-visible,
            input:focus-visible,
            [data-baseweb="select"] input:focus-visible {
                outline: 3px solid rgba(47, 111, 255, 0.24);
                outline-offset: 2px;
            }

            div[data-baseweb="select"] > div,
            div[data-baseweb="input"] > div,
            textarea,
            div[data-testid="stFileUploaderDropzone"] {
                background: var(--panel) !important;
                border: 1px solid var(--border) !important;
                border-radius: 16px !important;
                color: var(--text) !important;
                box-shadow: none !important;
            }

            textarea {
                font-family: "Instrument Sans", sans-serif !important;
            }

            div[data-testid="stFileUploaderDropzone"] {
                background: var(--panel-soft) !important;
                border-style: dashed !important;
                padding: 1rem;
            }

            div[data-testid="stBottomBlockContainer"] {
                background: linear-gradient(180deg, rgba(242,246,252,0.35) 0%, rgba(242,246,252,0.95) 36%, rgba(242,246,252,1) 100%) !important;
                border-top: 1px solid rgba(220, 229, 241, 0.85);
                padding-top: 0.45rem;
            }

            [data-testid="stChatInput"] {
                background: transparent !important;
                border-top: none !important;
                padding-top: 0.2rem;
            }

            [data-testid="stChatInput"] textarea {
                background: var(--panel) !important;
                color: var(--text) !important;
                border-radius: 18px !important;
                padding-top: 0.95rem !important;
            }

            [data-testid="stChatInput"] > div {
                background: transparent !important;
            }

            div[data-testid="stChatMessage"] {
                border: 1px solid var(--border);
                border-radius: 22px;
                padding: 0.5rem 0.75rem;
                margin-bottom: 0.95rem;
                box-shadow: var(--shadow);
            }

            div[data-testid="stChatMessage"][aria-label="assistant message"] {
                background: var(--panel);
                margin-right: 9%;
            }

            div[data-testid="stChatMessage"][aria-label="user message"] {
                background: var(--accent-soft);
                border-color: #c8d9ff;
                margin-left: 9%;
            }

            div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
            div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
                color: var(--text);
                line-height: 1.75;
                font-size: 0.99rem;
            }

            div[data-testid="stChatMessage"] code,
            .stCode code {
                font-family: "IBM Plex Mono", monospace !important;
            }

            [data-testid="stExpander"] {
                border: 1px solid var(--border);
                border-radius: 16px;
                background: var(--panel);
            }

            .sidebar-shell,
            .top-shell,
            .suggestion-card,
            .sidebar-note {
                background: var(--panel);
                border: 1px solid var(--border);
                box-shadow: var(--shadow);
            }

            .sidebar-shell {
                padding: 1rem;
                border-radius: 20px;
                margin-bottom: 1rem;
            }

            .sidebar-shell h2 {
                margin: 0;
                font-size: 1.35rem;
            }

            .sidebar-shell p,
            .sidebar-note p {
                margin: 0.45rem 0 0 0;
                line-height: 1.65;
            }

            .sidebar-note {
                margin-top: 1rem;
                padding: 0.95rem;
                border-radius: 16px;
            }

            .sidebar-note span,
            .metric-card span,
            .eyebrow,
            .message-label,
            .section-label,
            .suggestion-tag {
                font-size: 0.72rem;
                text-transform: uppercase;
                letter-spacing: 0.14em;
                color: var(--muted);
                font-weight: 700;
            }

            .top-shell {
                display: grid;
                grid-template-columns: minmax(0, 1.6fr) minmax(260px, 0.9fr);
                gap: 1rem;
                padding: 1.35rem;
                border-radius: var(--radius-xl);
                margin-bottom: 1.2rem;
                position: relative;
                overflow: hidden;
            }

            .top-shell::before {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(120deg, rgba(47,111,255,0.08), rgba(10,196,255,0.03) 42%, transparent 70%);
                pointer-events: none;
            }

            .top-shell h1 {
                margin: 0.2rem 0 0 0;
                font-size: clamp(2.2rem, 4vw, 3.5rem);
                line-height: 0.95;
                max-width: 11ch;
            }

            .top-shell p {
                margin: 0.9rem 0 0 0;
                line-height: 1.78;
                max-width: 58ch;
            }

            .meta-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.6rem;
                margin-top: 1rem;
            }

            .meta-pill {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.62rem 0.82rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.78);
                border: 1px solid var(--border);
                color: var(--text);
                font-size: 0.9rem;
                backdrop-filter: blur(2px);
            }

            .meta-pill strong {
                color: var(--text);
            }

            .stats-shell {
                display: grid;
                gap: 0.8rem;
                align-content: start;
            }

            .metric-card {
                padding: 0.95rem;
                border-radius: 18px;
                background: linear-gradient(180deg, #ffffff 0%, #f7f9fd 100%);
                border: 1px solid var(--border);
            }

            .metric-card strong {
                display: block;
                margin-top: 0.3rem;
                color: var(--text);
                font-size: 1.05rem;
            }

            .section-label {
                display: block;
                margin: 0.2rem 0 0.8rem 0;
            }

            .suggestion-card {
                min-height: 168px;
                padding: 1rem;
                border-radius: var(--radius-lg);
                margin-bottom: 0.75rem;
                background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
            }

            .suggestion-card h3 {
                margin: 0.7rem 0 0.45rem 0;
                font-size: 1.35rem;
                line-height: 1.05;
            }

            .suggestion-card p {
                margin: 0;
                line-height: 1.72;
            }

            .message-label {
                display: block;
                margin-bottom: 0.35rem;
            }

            .helper-note {
                padding: 0.95rem 1rem;
                margin-top: 0.2rem;
                border-radius: 16px;
                background: var(--panel-soft);
                border: 1px solid var(--border);
                color: var(--muted);
            }

            @media (max-width: 900px) {
                .top-shell {
                    grid-template-columns: 1fr;
                }

                .top-shell h1 {
                    max-width: none;
                    font-size: 2.7rem;
                }

                div[data-testid="stChatMessage"][aria-label="assistant message"],
                div[data-testid="stChatMessage"][aria-label="user message"] {
                    margin-left: 0;
                    margin-right: 0;
                }
            }

            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation: none !important;
                    transition: none !important;
                    scroll-behavior: auto !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(database, active_chat_id: int, settings: dict):
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-shell">
                <h2>Workspace</h2>
                <p>Historico salvo, contexto por arquivo e ajustes do modelo em um layout mais limpo.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("+ Novo chat", use_container_width=True, type="primary"):
            return "new_chat"

        st.caption("Conversas")
        chats = database.list_chats()
        for chat in chats:
            label = chat["title"]
            if st.button(
                label,
                key=f"chat_{chat['id']}",
                use_container_width=True,
                type="primary" if chat["id"] == active_chat_id else "secondary",
            ):
                return chat["id"]

        st.divider()
        st.subheader("Configuracoes")
        settings["model"] = st.selectbox(
            "Modelo",
            options=["gemini-2.5-flash", "gemini-2.5-pro"],
            index=0 if settings["model"] == "gemini-2.5-flash" else 1,
        )
        settings["temperature"] = st.slider(
            "Temperatura",
            min_value=0.0,
            max_value=1.5,
            value=float(settings["temperature"]),
            step=0.1,
        )
        settings["max_output_tokens"] = st.slider(
            "Max output tokens",
            min_value=256,
            max_value=4096,
            value=int(settings["max_output_tokens"]),
            step=256,
        )
        settings["stream"] = st.toggle("Streaming", value=bool(settings["stream"]))
        settings["system_prompt"] = st.text_area(
            "System prompt",
            value=settings.get("system_prompt", ""),
            height=140,
            placeholder="Instrucoes extras para o modelo...",
        )

        st.markdown(
            f"""
            <div class="sidebar-note">
                <span>Sessao atual</span>
                <strong>{html.escape(settings["model"])}</strong>
                <p>Temperatura {settings["temperature"]:.1f} | Streaming {"ligado" if settings["stream"] else "desligado"}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        if st.button("Excluir chat atual", use_container_width=True):
            return "delete_chat"

    return None


def render_chat_header(
    chat_title: str,
    settings: dict,
    chat_count: int,
    message_count: int,
) -> None:
    safe_title = html.escape(chat_title)
    st.markdown(
        f"""
        <div class="top-shell">
            <div>
                <span class="eyebrow">Chat com contexto</span>
                <h1>Um chat mais limpo, util e apresentavel.</h1>
                <p>
                    Sem exagero visual, sem cara de demo. So uma interface clara para conversar,
                    estudar, anexar arquivos e manter historico com boa hierarquia.
                </p>
                <div class="meta-row">
                    <span class="meta-pill"><strong>Conversa:</strong> {safe_title}</span>
                    <span class="meta-pill"><strong>Modelo:</strong> {html.escape(settings["model"])}</span>
                    <span class="meta-pill"><strong>Streaming:</strong> {"ON" if settings["stream"] else "OFF"}</span>
                </div>
            </div>
            <div class="stats-shell">
                <div class="metric-card">
                    <span>Chats salvos</span>
                    <strong>{chat_count}</strong>
                </div>
                <div class="metric-card">
                    <span>Mensagens desta conversa</span>
                    <strong>{message_count}</strong>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> str | None:
    st.markdown('<span class="section-label">Sugestoes para comecar</span>', unsafe_allow_html=True)
    selected_prompt = None
    columns = st.columns(2)

    for index, item in enumerate(SUGGESTED_PROMPTS):
        with columns[index % 2]:
            st.markdown(
                f"""
                <div class="suggestion-card">
                    <span class="suggestion-tag">{item["tag"]}</span>
                    <h3>{item["title"]}</h3>
                    <p>{item["body"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(item["cta"], key=f"suggestion_{index}", use_container_width=True):
                selected_prompt = item["prompt"]

    st.markdown(
        """
        <div class="helper-note">
            Anexe um PDF, DOCX, TXT ou CSV e faca a pergunta em seguida. O arquivo entra como contexto para a proxima resposta.
        </div>
        """,
        unsafe_allow_html=True,
    )
    return selected_prompt


def render_chat_messages(messages: list[dict]) -> None:
    for message in messages:
        label = "Voce" if message["role"] == "user" else "Assistente"
        with st.chat_message(message["role"]):
            st.markdown(f'<span class="message-label">{label}</span>', unsafe_allow_html=True)
            st.markdown(message["content"])


def render_response_tools(
    response_text: str,
    key_suffix: str,
    token_estimate: int | None = None,
) -> None:
    if token_estimate is not None:
        st.caption(f"Contexto enviado ao modelo: ~{token_estimate} tokens")
    with st.expander("Ver resposta em markdown"):
        st.code(response_text, language="markdown")
    st.download_button(
        "Baixar resposta .md",
        data=response_text,
        file_name=f"resposta_{key_suffix}.md",
        mime="text/markdown",
        key=f"download_{key_suffix}",
        use_container_width=False,
    )


def read_uploaded_file(uploaded_file) -> str:
    suffix = uploaded_file.name.lower().rsplit(".", maxsplit=1)[-1]

    if suffix == "txt":
        return uploaded_file.getvalue().decode("utf-8", errors="ignore")

    if suffix == "csv":
        return uploaded_file.getvalue().decode("utf-8", errors="ignore")

    if suffix == "pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Instale pypdf para ler arquivos PDF.") from exc

        reader = PdfReader(BytesIO(uploaded_file.getvalue()))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            cleaned = text.strip()
            if cleaned:
                pages.append(cleaned)
        if not pages:
            raise RuntimeError("Nao foi possivel extrair texto do PDF enviado.")
        return "\n\n".join(pages)

    if suffix == "docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError("Instale python-docx para ler arquivos DOCX.") from exc

        document = Document(uploaded_file)
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())

    raise RuntimeError("Formato de arquivo nao suportado.")


def render_file_uploader() -> None:
    uploaded_file = st.file_uploader(
        "Anexar contexto (txt, csv, docx, pdf)",
        type=["txt", "csv", "docx", "pdf"],
        accept_multiple_files=False,
    )
    if not uploaded_file:
        st.session_state.pending_file_context = None
        st.session_state.uploaded_file_signature = None
        st.session_state.uploaded_file_name = None
        st.session_state.file_context_consumed = False
        return

    file_bytes = uploaded_file.getvalue()
    file_signature = hashlib.sha256(file_bytes).hexdigest()

    if st.session_state.get("uploaded_file_signature") == file_signature:
        if st.session_state.get("pending_file_context"):
            st.success(f"Arquivo pronto para a proxima pergunta: {uploaded_file.name}")
        elif st.session_state.get("file_context_consumed"):
            st.caption(f"Arquivo ja usado na ultima pergunta: {uploaded_file.name}")
        return

    try:
        content = read_uploaded_file(uploaded_file)
        st.session_state.pending_file_context = content[:MAX_FILE_CONTEXT_CHARS]
        st.session_state.uploaded_file_signature = file_signature
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.file_context_consumed = False
        st.success(f"Arquivo carregado: {uploaded_file.name}")
    except Exception as exc:
        st.error(f"Nao foi possivel ler o arquivo: {exc}")


def render_error_message(exc: Exception) -> str:
    text = str(exc)
    lowered = text.lower()
    if "api key" in lowered or "chave" in lowered:
        return "Nao encontrei a chave da API. Confira o arquivo .env e tente novamente."
    if "quota" in lowered or "429" in lowered:
        return "O limite da API foi atingido no momento. Tente novamente em alguns segundos."
    return f"Nao consegui falar com o Gemini agora. Detalhe tecnico: {text}"
