# JVS CLI

A terminal-based AI chat interface with streaming support and beautiful terminal formatting.

## Features

- Interactive REPL mode with conversation history
- Streaming responses with real-time display
- AI thinking step visualization
- Markdown rendering
- Multiple color themes
- Support for multiple AI providers:
  - Jarvis backend
  - OpenAI (GPT-4 and other models)
  - Anthropic Claude (Haiku 4.5 by default)

## Installation

```bash
pip install jvs-cli
```

## Quick Start

### Using Jarvis Backend

#### Predefined Environments

For quick access to Jarvis environments, use the predefined options:

**Local Development:**
```bash
# First time (will prompt for login code)
jvs-cli -local

# Subsequent uses
jvs-cli -local
```

**Beta Environment:**
```bash
jvs-cli -beta
```

**Production Environment:**
```bash
jvs-cli -prod
```

#### Custom Configuration

Initialize custom configuration:

```bash
jvs-cli config init
```

You'll be prompted for:
- API URL (OpenAI-compatible endpoint)
- Login Code
- Theme (color scheme)

Start chatting:

```bash
jvs-cli
```

### Using OpenAI

First time (with API key):

```bash
jvs-cli -openai -k sk-your-openai-api-key
```

Subsequent uses (key is saved):

```bash
jvs-cli -openai
```

Debug mode to see API responses:

```bash
jvs-cli -openai -d
```

### Using Claude

First time (with API key):

```bash
jvs-cli -claude -k your-anthropic-api-key
```

Subsequent uses (key is saved):

```bash
jvs-cli -claude
```

### One-shot Queries

With Jarvis:

```bash
jvs-cli ask "What is machine learning?"
```

With OpenAI:

```bash
jvs-cli ask "What is machine learning?" -openai
```

With Claude:

```bash
jvs-cli ask "What is machine learning?" -claude
```

## Commands

Interactive mode commands:
- `/new` - Start new conversation
- `/history` - Show conversation history
- `/config` - Show configuration
- `/help` - Show help
- `/exit` - Exit

CLI commands:
- `jvs-cli` - Interactive mode with default provider
- `jvs-cli -local` - Use local Jarvis environment
- `jvs-cli -beta` - Use beta Jarvis environment
- `jvs-cli -prod` - Use production Jarvis environment
- `jvs-cli -openai` - Use OpenAI API
- `jvs-cli -claude` - Use Claude API
- `jvs-cli ask "query"` - One-shot query
- `jvs-cli chat <conv_id>` - Continue conversation
- `jvs-cli config init` - Setup wizard
- `jvs-cli config show` - Show configuration
- `jvs-cli history` - List conversations

Environment options work with all commands:
```bash
jvs-cli ask "hello" -local
jvs-cli ask "hello" -beta
jvs-cli ask "hello" -prod
jvs-cli ask "hello" -openai
jvs-cli ask "hello" -claude
```

## Configuration

### Predefined Jarvis Environments

The following environments are built-in and don't require configuration:

- `-local`: `http://localhost:7961/api/v1` (Local development)
- `-beta`: `https://jvs-api.atomecorp.net/api/v1` (Beta environment)
- `-prod`: `https://jarvis-api.atomecorp.net/api/v1` (Production environment)

Config file: `~/.jvs-cli/config.json`

```json
{
  "api_provider": "jarvis",
  "api_base_url": "https://api.example.com/v1",
  "login_code": "your_login_code",
  "api_keys": {
    "openai_api_key": "sk-...",
    "claude_api_key": "sk-ant-..."
  },
  "display": {
    "theme": "claude_dark",
    "live_mode": true
  }
}
```

API keys are stored locally and used automatically after first use.

## Requirements

- Python 3.10+
- OpenAI-compatible API endpoint

## License

Apache License 2.0
