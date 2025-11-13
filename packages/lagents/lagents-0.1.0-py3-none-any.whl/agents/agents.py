"""
Agent role abstractions for the unified Ollama framework.

This module defines classes representing different kinds of agents that use
an underlying BaseOllamaClient to perform specific tasks. The goal is to
provide reusable behaviors without forcing application developers to
repeatedly set up prompts or handle streaming responses.

Classes
-------
* BaseAgent – Abstract base class for all agents
* ChatAgent – Simple conversational agent
* CodingAgent – Specialized agent for code generation
* EmbeddingAgent – Agent for generating text embeddings
"""

from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator, Dict, Iterable, List, Optional, Union

from .ollama_framework import (
    BaseOllamaClient,
    ChatMessage,
    ChatResponse,
)


class BaseAgent:
    """Base class for agents that communicate via a BaseOllamaClient.

    Subclasses should implement `run` to perform their task. Agents can
    optionally define a `system_prompt` attribute to prime the model's behavior.

    Parameters
    ----------
    client : BaseOllamaClient
        The client to use for model interactions
    system_prompt : str, optional
        System prompt to prepend to all conversations
    """

    system_prompt: Optional[str] = None

    def __init__(self, client: BaseOllamaClient, system_prompt: Optional[str] = None) -> None:
        self.client = client
        if system_prompt is not None:
            self.system_prompt = system_prompt

    async def run(
        self,
        messages: Iterable[Union[ChatMessage, Dict[str, Any]]],
        **options: Any,
    ) -> AsyncGenerator[ChatResponse, None]:
        """Execute the agent with the given messages.

        Subclasses can override this to implement specific behaviors. The
        default implementation sends messages via client.chat.

        Parameters
        ----------
        messages : iterable of ChatMessage or dict
            The messages to send
        options : any
            Additional options passed to client.chat

        Yields
        ------
        ChatResponse
            Streaming response chunks
        """
        # Convert to list for manipulation
        message_list = list(messages)

        # Prepend system prompt if defined
        if self.system_prompt:
            message_list.insert(0, {"role": "system", "content": self.system_prompt})

        async for chunk in self.client.chat(message_list, **options):
            yield chunk

    def run_sync(
        self,
        messages: Iterable[Union[ChatMessage, Dict[str, Any]]],
        **options: Any,
    ) -> List[ChatResponse]:
        """Synchronous wrapper around the asynchronous run method.

        Parameters
        ----------
        messages : iterable of ChatMessage or dict
            The messages to send
        options : any
            Additional options passed to run

        Returns
        -------
        list of ChatResponse
            All response chunks collected
        """
        async def _collect() -> List[ChatResponse]:
            results: List[ChatResponse] = []
            async for chunk in self.run(messages, **options):
                results.append(chunk)
            return results

        return asyncio.run(_collect())

    def get_full_response(
        self,
        messages: Iterable[Union[ChatMessage, Dict[str, Any]]],
        **options: Any,
    ) -> str:
        """Convenience method to get the complete response as a single string.

        Parameters
        ----------
        messages : iterable of ChatMessage or dict
            The messages to send
        options : any
            Additional options passed to run

        Returns
        -------
        str
            The complete response text
        """
        chunks = self.run_sync(messages, **options)
        return "".join(chunk.content for chunk in chunks)


class ChatAgent(BaseAgent):
    """A simple chat agent that echoes user messages to the underlying model.

    This is the most basic agent type - it simply forwards messages to the
    model without any special prompt engineering.

    Example
    -------
    ```python
    from ollama_framework import LocalOllamaClient
    from agents import ChatAgent

    client = LocalOllamaClient("llama3:latest", "http://localhost:11434")
    agent = ChatAgent(client)

    response = agent.get_full_response([
        {"role": "user", "content": "Hello!"}
    ])
    print(response)
    ```
    """
    system_prompt: Optional[str] = None


class CodingAgent(BaseAgent):
    """Agent specialized for code generation tasks.

    The system prompt instructs the model to produce clean, self-contained
    code snippets. Adjust the prompt or options to tailor the generated output.

    Example
    -------
    ```python
    agent = CodingAgent(client)
    code = agent.get_full_response([
        {"role": "user", "content": "Write a Python function to calculate fibonacci"}
    ])
    print(code)
    ```
    """
    system_prompt: str = (
        "You are an expert software engineer. Generate clean, efficient, and "
        "well-documented code based on the user's instructions. Respond with "
        "only the code without explanations, unless explicitly asked."
    )


class ReasoningAgent(BaseAgent):
    """Agent optimized for complex reasoning and analysis tasks.

    Uses chain-of-thought prompting to encourage step-by-step reasoning.

    Example
    -------
    ```python
    agent = ReasoningAgent(client)
    response = agent.get_full_response([
        {"role": "user", "content": "Explain the proof of Fermat's Last Theorem"}
    ])
    print(response)
    ```
    """
    system_prompt: str = (
        "You are an expert analyst with strong reasoning capabilities. "
        "When answering questions, break down complex problems into steps "
        "and explain your reasoning process clearly. Use logical thinking "
        "and cite relevant facts or principles."
    )


class ResearchAgent(BaseAgent):
    """Agent specialized for research and information synthesis.

    Designed to provide comprehensive, well-structured responses with
    citations when applicable.

    Example
    -------
    ```python
    agent = ResearchAgent(client)
    response = agent.get_full_response([
        {"role": "user", "content": "What are the latest developments in quantum computing?"}
    ])
    print(response)
    ```
    """
    system_prompt: str = (
        "You are an expert researcher. Provide comprehensive, well-researched "
        "responses to queries. Structure your answers clearly with sections, "
        "cite sources when available, and distinguish between established facts "
        "and current hypotheses."
    )


class SummarizationAgent(BaseAgent):
    """Agent optimized for summarizing text and extracting key points.

    Example
    -------
    ```python
    agent = SummarizationAgent(client)
    summary = agent.get_full_response([
        {"role": "user", "content": f"Summarize this text: {long_text}"}
    ])
    print(summary)
    ```
    """
    system_prompt: str = (
        "You are an expert at summarizing text. Extract the key points and "
        "main ideas from the provided content. Present summaries in a clear, "
        "concise format. Preserve important details while removing redundancy."
    )


class EmbeddingAgent(BaseAgent):
    """Agent for generating text embeddings using the underlying client.

    Calling `run` on this agent will ignore chat options and simply return
    the embedding vector as a single ChatResponse with the embedding stored
    in the metadata field.

    Example
    -------
    ```python
    agent = EmbeddingAgent(client)
    responses = agent.run_sync([
        {"role": "user", "content": "Hello world"}
    ])
    embedding = responses[0].metadata["embedding"]
    print(f"Embedding dimension: {len(embedding)}")
    ```
    """

    async def run(
        self,
        messages: Iterable[Union[ChatMessage, Dict[str, Any]]],
        **options: Any,
    ) -> AsyncGenerator[ChatResponse, None]:
        """Generate embeddings for the concatenated message contents.

        Parameters
        ----------
        messages : iterable of ChatMessage or dict
            Messages to embed
        options : any
            Ignored for embedding generation

        Yields
        ------
        ChatResponse
            A single response with embedding in metadata
        """
        # Concatenate all message contents
        combined_text = "\n\n".join(
            msg.content if isinstance(msg, ChatMessage) else str(msg.get("content", ""))
            for msg in messages
        )

        vector = await self.client.generate_embedding(combined_text)

        yield ChatResponse(
            content="",  # No textual content
            role="embedding",
            done=True,
            metadata={"embedding": vector},
        )


__all__ = [
    "BaseAgent",
    "ChatAgent",
    "CodingAgent",
    "ReasoningAgent",
    "ResearchAgent",
    "SummarizationAgent",
    "EmbeddingAgent",
]
