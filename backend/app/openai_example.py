"""Example of using the modern OpenAI Python SDK to create a chat completion."""

from __future__ import annotations

from openai import OpenAI


def ask_openai(prompt: str) -> str:
    """Send ``prompt`` to the OpenAI Chat Completions API and return the text.

    The OpenAI SDK from version ``1.x`` uses a client object.  This function
    demonstrates the minimal required parameters and returns the assistant's
    reply text.
    """

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


__all__ = ["ask_openai"]

