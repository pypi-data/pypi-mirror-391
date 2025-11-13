# Symbol Machines Memory SDK (Python)

A lightweight SDK that adds structured long-term memory to any LLM.

Learn more at https://symbolmachines.com

---

## Installation

```bash
pip install symbolmachines
```

## Usage

```python
from symbolmachines import Symbol

symbol = Symbol(api_key="sk-...")

# Inject memory context before calling your LLM
context = symbol.memory.inject.create(input="What should i eat for lunch?")

# ... call your LLM with the contextual input ...

# Save memory after generation
symbol.memory.save.create(output="Eating sushi is a healthy meal.")
```

---

## API

`symbol.memory.inject.create(input=str)`
Injects memory context into user input.

`symbol.memory.save.create(output=str)`
Writes an output into the Symbol's memory.

---

## Configuration

```python
symbol = Symbol(
    api_key="sk-...",
    base_url="https://api.symbol.ai/v1" # optional override
)
```
