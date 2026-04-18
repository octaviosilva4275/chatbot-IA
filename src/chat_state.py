from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ContextConfig:
    max_recent_messages: int = 12
    max_chars_before_summary: int = 12000


def approximate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def build_context_with_summary(
    messages: list[dict[str, str]],
    config: ContextConfig,
) -> tuple[list[dict[str, str]], str | None]:
    """
    Retorna mensagens recentes e um resumo simples da parte antiga.
    """
    if not messages:
        return [], None

    history_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
    if len(history_text) <= config.max_chars_before_summary:
        return messages[-config.max_recent_messages :], None

    older = messages[: -config.max_recent_messages]
    recent = messages[-config.max_recent_messages :]

    snippets = []
    for msg in older[-8:]:
        snippets.append(f"- {msg['role']}: {msg['content'][:120]}")

    summary = "Resumo de contexto anterior:\n" + "\n".join(snippets)
    return recent, summary
