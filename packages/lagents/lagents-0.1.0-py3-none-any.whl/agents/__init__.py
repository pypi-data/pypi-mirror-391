"""
Agents - Minimal Experimental Local LLM Agent Framework
=======================================================

⚠️ EXPERIMENTAL MINIMAL FRAMEWORK ⚠️

A minimal, experimental framework for building agents with local LLM deployments.
**Zero bloat, maximum simplicity, direct API calls.**

Currently configured for Ollama, with stubs for other local LLM providers:
- Ollama (Fully Implemented ✓)
- llama.cpp (Stub)
- vLLM (Stub)
- Text Generation WebUI (Stub)
- LocalAI (Stub)
- LM Studio (Stub)

Minimal overhead design - supports both single-node and distributed deployments.

Basic Usage
-----------
```python
from Agents import LocalOllamaClient, ChatAgent

# Create a client
client = LocalOllamaClient(
    model_name="llama3:latest",
    api_base="http://localhost:11434"
)

# Create an agent
agent = ChatAgent(client)

# Get a response
response = agent.get_full_response([
    {"role": "user", "content": "Hello!"}
])
print(response)
```

For distributed deployments with SOLLOL:
```python
from Agents import DistributedOllamaClient, ChatAgent

# Create a distributed client
client = DistributedOllamaClient(
    model_name="llama3:latest",
    nodes=["http://192.168.1.100:11434", "http://192.168.1.101:11434"]
)

agent = ChatAgent(client)
```

Components
----------
* Clients: BaseOllamaClient, LocalOllamaClient, DistributedOllamaClient
* Agents: BaseAgent, ChatAgent, CodingAgent, ReasoningAgent, etc.
* Data Classes: ChatMessage, ChatResponse
* Providers: LlamaCppClient, VLLMClient, etc. (stubs for future development)
* Utils: Parsing, health checking, retry logic
"""

from .ollama_framework import (
    BaseOllamaClient,
    LocalOllamaClient,
    DistributedOllamaClient,
    ChatMessage,
    ChatResponse,
)

from .agents import (
    BaseAgent,
    ChatAgent,
    CodingAgent,
    ReasoningAgent,
    ResearchAgent,
    SummarizationAgent,
    EmbeddingAgent,
)

from .utils import (
    parse_json_response,
    check_node_health,
    retry_with_backoff,
    format_chat_history,
    estimate_tokens,
    truncate_to_token_limit,
    merge_response_chunks,
)

# Optional: Import provider stubs (will raise NotImplementedError if used)
from .providers import (
    LlamaCppClient,
    VLLMClient,
    TextGenWebUIClient,
    LocalAIClient,
    LMStudioClient,
)

__version__ = "0.1.0-experimental"

__all__ = [
    # Clients
    "BaseOllamaClient",
    "LocalOllamaClient",
    "DistributedOllamaClient",
    # Data classes
    "ChatMessage",
    "ChatResponse",
    # Agents
    "BaseAgent",
    "ChatAgent",
    "CodingAgent",
    "ReasoningAgent",
    "ResearchAgent",
    "SummarizationAgent",
    "EmbeddingAgent",
    # Providers (stubs)
    "LlamaCppClient",
    "VLLMClient",
    "TextGenWebUIClient",
    "LocalAIClient",
    "LMStudioClient",
    # Utils
    "parse_json_response",
    "check_node_health",
    "retry_with_backoff",
    "format_chat_history",
    "estimate_tokens",
    "truncate_to_token_limit",
    "merge_response_chunks",
]
