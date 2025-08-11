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
    if not response.choices or len(response.choices) == 0:
        raise ValueError("No choices returned from OpenAI API.")
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content in OpenAI API response.")
    return content


__all__ = ["ask_openai"]

