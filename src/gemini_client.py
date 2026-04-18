from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai


class GeminiClient:
    def __init__(self, model_name: str) -> None:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Chave da API não encontrada. Defina GEMINI_API_KEY ou GOOGLE_API_KEY no .env"
            )
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_output_tokens: int = 1024,
    ) -> str:
        contents: list[dict[str, object]] = []
        if system_prompt.strip():
            contents.append(
                {
                    "role": "user",
                    "parts": [{"text": f"Instruções do sistema:\n{system_prompt.strip()}"}],
                }
            )

        for msg in messages:
            contents.append(
                {
                    "role": "model" if msg["role"] == "assistant" else "user",
                    "parts": [{"text": msg["content"]}],
                }
            )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config={
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            },
        )
        return response.text or "Não consegui gerar resposta no momento."
