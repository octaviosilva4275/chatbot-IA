from __future__ import annotations

import io
import csv

import streamlit as st


def inject_css() -> None:
    st.markdown(
        """
        <style>
            .main { padding-top: 0.6rem; }
            .block-container { max-width: 1050px; padding-top: 1rem; }
            .hero {
                text-align: center;
                margin: 2.4rem auto 1.8rem;
                max-width: 700px;
                animation: fadeIn .45s ease-out;
            }
            .hero h1 { font-size: 2rem; margin-bottom: 0.4rem; }
            .hero p { color: #9aa0a6; margin-bottom: 1rem; }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(6px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_welcome() -> str | None:
    st.markdown(
        """
        <div class="hero">
            <h1>Como posso ajudar hoje?</h1>
            <p>Faça perguntas, peça explicações de código ou analise arquivos.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    suggestions = [
        "Explique um código Python",
        "Resuma um texto",
        "Crie um plano de estudos",
        "Monte um checklist para deploy",
    ]
    cols = st.columns(2)
    for idx, suggestion in enumerate(suggestions):
        with cols[idx % 2]:
            if st.button(suggestion, use_container_width=True):
                return suggestion
    return None


def render_chat_messages(messages: list[dict[str, str]]) -> None:
    for i, msg in enumerate(messages):
        with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                with st.expander("Ver markdown bruto / copiar"):
                    st.code(msg["content"], language="markdown")
                st.download_button(
                    "Baixar resposta (.md)",
                    msg["content"],
                    file_name=f"resposta_{i}.md",
                    mime="text/markdown",
                    key=f"download_{i}",
                )


def read_uploaded_files(uploaded_files: list) -> str:
    all_chunks: list[str] = []

    for f in uploaded_files:
        suffix = f.name.lower().split(".")[-1]

        if suffix == "txt":
            all_chunks.append(f"\n### {f.name}\n" + f.getvalue().decode("utf-8", errors="ignore"))

        elif suffix == "csv":
            content = f.getvalue().decode("utf-8", errors="ignore")
            reader = csv.reader(io.StringIO(content))
            preview_rows = []
            for idx, row in enumerate(reader):
                if idx >= 30:
                    break
                preview_rows.append(", ".join(cell.strip() for cell in row))
            all_chunks.append(f"\n### {f.name} (prévia)\n" + "\n".join(preview_rows))

        elif suffix == "pdf":
            try:
                from pypdf import PdfReader

                reader = PdfReader(io.BytesIO(f.getvalue()))
                text = "\n".join((page.extract_text() or "") for page in reader.pages[:20])
                all_chunks.append(f"\n### {f.name}\n{text}")
            except Exception:
                all_chunks.append(
                    f"\n### {f.name}\nNão foi possível extrair PDF (verifique dependência pypdf)."
                )

        elif suffix == "docx":
            try:
                import docx

                document = docx.Document(io.BytesIO(f.getvalue()))
                text = "\n".join(p.text for p in document.paragraphs[:300])
                all_chunks.append(f"\n### {f.name}\n{text}")
            except Exception:
                all_chunks.append(
                    f"\n### {f.name}\nNão foi possível extrair DOCX (verifique dependência python-docx)."
                )

    return "\n".join(all_chunks).strip()
