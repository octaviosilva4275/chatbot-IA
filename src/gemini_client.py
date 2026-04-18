from __future__ import annotations

from dataclasses import dataclass

from google import genai
from google.genai import types


@dataclass
class GeminiClient:
    api_key: str | None

    def __post_init__(self) -> None:
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def ensure_ready(self) -> None:
        if not self.api_key or self.client is None:
            raise RuntimeError(
                "Chave da API nao encontrada. Defina GEMINI_API_KEY ou GOOGLE_API_KEY no arquivo .env."
            )

    def generate_response(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_output_tokens: int,
        stream: bool,
        placeholder,
    ) -> str:
        self.ensure_ready()

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        if stream:
            collected = ""
            response = self.client.models.generate_content_stream(
                model=model,
                contents=prompt,
                config=config,
            )
            for chunk in response:
                text = getattr(chunk, "text", None)
                if not text:
                    continue
                collected += text
                placeholder.markdown(collected + "\n\n`...`")
            placeholder.markdown(collected)
            return collected

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        text = getattr(response, "text", "") or "Nao houve conteudo retornado pelo modelo."
        placeholder.markdown(text)
        return text
