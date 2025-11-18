# KaiCTL - Kubernetes Natural Language Agent

Translate natural language requests into kubectl commands using Claude or Ollama.

## Installation
```bash
pip install -e .
```

Or for development:
```bash
pip install -e ".[dev]"
```

## Usage
```bash
kaictl
```

## First-Time Setup

When you run `kaictl` for the first time, it will:
1. Create `~/.kaictl/` configuration directory
2. Ask you to choose between Claude (Anthropic) or Ollama
3. Set up your API key or Ollama connection

## Requirements

- Python 3.8+
- kubectl installed and configured
- Either:
  - Anthropic API key (for Claude)
  - Ollama running locally (for local LLM)

## Features

- 🤖 Natural language to kubectl translation
- 🔧 Interactive troubleshooting mode
- 📊 Resource analysis and comparison
- 💾 Session history and learning
- ✅ Safety checks for destructive commands
