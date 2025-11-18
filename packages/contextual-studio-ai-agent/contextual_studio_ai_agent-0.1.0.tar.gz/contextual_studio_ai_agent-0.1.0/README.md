# 🧠 Contextual Studio AI Agent

> **Composable Agent Framework built on top of ADK.**  
> A modular Python library for creating, orchestrating, and managing autonomous AI agents with structured reasoning, prompt engineering, and LLM pipelines.

---

## 🚀 Overview

`contextual-studio-ai-agent` is a **high-level agent framework** built on top of the **Agent Development Kit (ADK)**.  
It provides a flexible architecture for building **stateful, composable, and reactive agents** capable of multi-step reasoning and coordination with large language models (LLMs).

This library powers the **Contextual Studio AI Stack**, offering a clean and extensible interface for integrating **LLMs**, **prompt systems**, and **multi-agent orchestration**.

---

## 🧩 Key Features

- 🧠 **Unified ADK Agent API** — Build and run autonomous agents directly on ADK.
- 🔁 **Composable Managers** — Coordinate multiple reasoning pipelines using `AdkManager` and `AdkSequentialManager`.
- 🧾 **Dynamic Prompt Layer** — Create reusable, testable prompt templates directly in Python or Markdown.
- ⚙️ **Factory Pattern for LLMs** — Centralized configuration of language models and connectors through `LLMFactory`.
- 🧱 **Extensible Modular Design** — Easily extend components, factories, and managers without altering the core code.
- 🧩 **Integration Ready** — Compatible with external RAG systems, retrievers, and custom LLM endpoints.

---

## 🏗️ Project Structure

```

contextual/
└── agent/
├── components/
│ ├── agents/ # Core agent implementations (ADK-based)
│ │ ├── base.py
│ │ ├── adk_agent.py
│ │ ├── adk_a_agent.py
│ │ ├── adk_b_agent.py
│ │ └── adk_sequential_agent.py
│ └── prompts/ # Prompt templates, base classes, and test prompts
│ ├── base.py
│ ├── test_a_prompt.py
│ ├── test_b_prompt.py
│ └── test_seq_prompt.py
│
├── factories/
│ └── llm_factory.py # Factory for building and configuring LLMs
│
├── managers/
│ ├── base.py # Base manager class
│ ├── adk_manager.py # ADK manager
│ └── adk_seq_manager.py # Sequential orchestration manager
│
├── models/
│ ├── content.py # Content and message models (Pydantic)
│ └── llm_model.py # LLM configuration and schema models
│
└── utils/ # Utilities and shared helpers

```

This modular structure allows each layer — **components**, **factories**, **managers**, and **models** — to evolve independently while remaining tightly integrated.

---

## ⚡ Installation

Install from **TestPyPI** future in **PyPI**:

```bash
pip install -i https://test.pypi.org/simple/ contextual-studio-ai-agent
```

Once available on PyPI:

```bash
pip install contextual-studio-ai-agent
```

### Requirements

- Python ≥ 3.12
- Compatible with `uv`, `pip`, or `poetry`

---

## 🧠 Quick Start

### ✳️ Basic Agent Execution

```python
from contextual.agent.managers import AdkManager
from contextual.agent.factories import LLMFactory
from contextual.agent.components.agents import AdkAgent

# 1. Create an LLM factory
llm = LLMFactory.create("openai", model="gpt-4-turbo")

# 2. Initialize an ADK agent
agent = AdkAgent(llm=llm, name="contextual-agent")

# 3. Manage agent lifecycle
manager = AdkManager(agent)

# 4. Run a reasoning task
response = manager.run("Summarize the legal implications of AI-driven contracts.")
print(response)
```

---

### 🔁 Sequential Orchestration

```python
from contextual.agent.managers import AdkSequentialManager
from contextual.agent.components.agents import AdkSequentialAgent

manager = AdkSequentialManager()
agent = AdkSequentialAgent()

result = manager.run(agent, "Draft and review a non-disclosure agreement.")
print(result)
```

---

### 🧱 Extending Prompts

```python
from contextual.agent.components.prompts import base

class LegalPrompt(base.BasePrompt):
    def render(self, case_facts: str) -> str:
        return f"Given the following case:\n{case_facts}\nExplain the key legal issues."

prompt = LegalPrompt()
print(prompt.render("An employee was terminated after an AI system error."))
```

---

## 🧩 Integration Example: RAG Pipelines

```python
from contextual.agent.factories import LLMFactory
from contextual.agent.managers import AdkManager

llm = LLMFactory.create("openai", model="gpt-4o")
manager = AdkManager.from_retriever("pinecone", llm)
```

---

## 🧪 Testing

Tests follow standard `pytest` conventions and are located under `tests/`.

Run all tests with:

```bash
uv run pytest -v
```

---

## 🧩 Development Setup

```bash
# Clone the repository
git clone https://github.com/contextual-studio/agent.git
cd agent

# Sync dependencies
uv sync --dev

# Run tests
uv run pytest
```

---

## 🧭 Roadmap

- [ ] Multi-agent orchestration with ADK sequential control
- [ ] Graph-based memory and state tracking
- [ ] RAG integration with contextual retrievers
- [ ] LangFuse analytics integration
- [ ] Async streaming for real-time reasoning

---

## 🤝 Contributing

We welcome contributions!
Please follow [PEP 8](https://peps.python.org/pep-0008/) and [Conventional Commits](https://www.conventionalcommits.org/) standards.

Submit issues or pull requests via the [GitHub repository](https://github.com/contextual-studio/agent).

---

## 🧾 License

Licensed under the **MIT License**.
See [`LICENSE`](./LICENSE) for more information.

---

## 🌐 Project Links

- 🏠 [Homepage](https://contextualstudio.com/)
- 📘 [Documentation](https://github.com/contextual-studio/agent)
- 🧩 [Repository](https://github.com/contextual-studio/agent)
- 🧪 [TestPyPI Package](https://test.pypi.org/project/contextual-studio-ai-agent/)
