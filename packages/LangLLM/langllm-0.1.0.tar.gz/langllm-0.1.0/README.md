# LLM Client Integration for LangChain with Chain-of-Thought Support

This package provides a seamless integration between custom LLM clients (e.g., DeepSeek, GLM, Qwen) and LangChain’s `BaseChatModel`, with built-in support for **chain-of-thought (CoT) reasoning**, structured output parsing, and both synchronous/asynchronous streaming.

Designed for developers who want fine-grained control over LLM interactions while leveraging LangChain’s ecosystem (e.g., callbacks, `astream_events`, tools, agents), this implementation wraps any OpenAI-compatible API into a fully compliant LangChain chat model.

---

## 📦 Features

- ✅ **LangChain-Compatible Chat Model**: Implements `BaseChatModel` with full support for sync/async, streaming/non-streaming.
- 🔗 **Chain-of-Thought (Thinking) Mode**: Enable or disable CoT reasoning per model (GLM, Qwen, DeepSeek).
- 🧠 **Custom Message Types**: `ChatMessage` and `ChatMessageChunk` preserve raw LLM responses (`ChatCompletion` / `ChatCompletionChunk`).
- 📐 **Structured Output Parsing**: `SchemaParser` generates schema-aware prompts and robustly parses LLM responses into Pydantic models.
- ⚙️ **Flexible LLM Client**: Configurable base URL, API key fallbacks, and dynamic reconfiguration.
- 🌐 **Streaming Support**: Full compatibility with LangChain’s event streaming (`astream_events`, callbacks).

---

## 🗂️ Project Structure

```text
lingua-agent/
├── pyproject.toml                 # ← MUST contain project metadata & deps
├── README.md
├── LICENSE
└── src/
    └── lingua_agent/              # ← top-level package name
        ├── __init__.py
        ├── llm_api/               # ← core LLM integration
        │   ├── __init__.py
        │   ├── llm_client.py
        │   ├── llm_client_chat_model.py
        │   ├── message_chunk.py
        │   └── thinking_config.py
        └── utils/                 # ← helpers
            ├── __init__.py
            └── schema_parse.py
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install langchain-core openai pydantic
```

### 2. Initialize the LLM Client

```python
from llm_client import LLMClient

llm_client = LLMClient(
    model="deepseek-chat",
    api_key="your-api-key",
    enable_thinking=True  # Enable chain-of-thought if supported
)
```

### 3. Wrap as LangChain Chat Model

```python
from llm_client_chat_model import LLMClientChatModel

chat_model = LLMClientChatModel(llm_client=llm_client)
```

### 4. Use with LangChain

```python
from langchain_core.messages import HumanMessage

# Non-streaming
response = chat_model.invoke([HumanMessage(content="Explain quantum computing.")])
print(response.content)

# Streaming
for chunk in chat_model.stream([HumanMessage(content="Write a haiku.")]):
    print(chunk.content, end="", flush=True)
```

### 5. Parse Structured Output

```python
from pydantic import BaseModel
from schema_parser import SchemaParser

class Answer(BaseModel):
    summary: str
    keywords: list[str]

parser = SchemaParser(Answer)
prompt = parser.schema_generation_prompt + "\n\nUser: Summarize climate change."

response = chat_model.invoke([HumanMessage(content=prompt)])
answer: Answer = parser.parse_response_to_base_model(response.content)
```

---

## 🔧 Configuration

### Supported Models & CoT Parameters

| Model Prefix | Enable Thinking                | Disable Thinking               |
|--------------|--------------------------------|--------------------------------|
| `glm`        | `{"thinking": {"type": "enabled"}}`  | `{"thinking": {"type": "disabled"}}` |
| `qwen`       | `{"enable_thinking": True}`    | `{"enable_thinking": False}`   |
| `deepseek`   | `{}` (no extra params)         | `{}`                           |

> The `LLMClient` auto-detects model type and injects parameters via `extra_body`.

### API Key Resolution

The client checks environment variables in order:
- `DEEPSEEK_API_KEY`
- `OPENAI_API_KEY`
- `ZHIPU_API_KEY`
- `API_KEY`

---

## 📝 Notes

- **Streaming Merge**: `merge_chunks_to_completion()` reconstructs full `ChatCompletion` from chunks, including usage stats and custom fields like `reasoning_content`.
- **Error Resilience**: `SchemaParser` uses fallback strategies to extract JSON from LLM responses (code blocks, raw JSON).
- **Callbacks**: Fully supports LangChain’s callback system (`on_llm_new_token`, `astream_events`, etc.).

---

## 📜 License

MIT License — feel free to use, modify, and distribute.

---

> Built for researchers and developers who need **reliable, structured, and introspectable** LLM interactions within the LangChain framework.