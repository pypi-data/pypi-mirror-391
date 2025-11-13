<p align="center">
    <img src="https://i.ibb.co/d9HMQPc/conciliate-brand.png" alt="Conciliate - Unified context for smarter AI decisions" />
</p>

<p align="center">
    <!-- <a href="https://github.com/iv4n-ga6l/conciliate/releases" target="_blank" rel="noopener"><img src="https://img.shields.io/github/release/iv4n-ga6l/conciliate.svg" alt="Latest releases" /></a> -->
    <a href="https://github.com/iv4n-ga6l/conciliate/blob/main/LICENSE" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License" /></a>
    <a href="https://pypi.org/project/conciliate/" target="_blank" rel="noopener"><img src="https://img.shields.io/pypi/v/conciliate.svg" alt="PyPI version" /></a>
</p>

**Unified context for smarter AI decisions.**

Conciliate automatically extracts API specifications from your backend, detects changes, and streams context to AI coding assistants in real-time. Keep your AI in sync across separate IDE sessions—no more manual copy-pasting.

## Features

- **Auto-extraction**: Monitors backend files, generates OpenAPI specs automatically
- **Live updates**: Real-time synchronization via MCP protocol  
- **Three access modes**: MCP server, REST API, CLI, VS Code extension
- **Framework support**: FastAPI, Flask, Express (auto-detected)
- **AI-native**: Built for Claude Desktop, Cursor, VS Code Copilot
- **Local-first**: No cloud dependencies, runs entirely on your machine
- VS Code extension (status bar, API explorer, changes view, auto-refresh)
- Mock server mode (fake API generation)
- Multi-Workspace Support

## Quick Start

### Python Package

```bash
pip install conciliate
```

### Setup

```bash
cd /path/to/your/project
conciliate init
# Edit .conciliate.yaml to set backend_path
```

### Run

```bash
conciliate mcp      # For AI assistants (recommended)
conciliate watch    # REST API + file watching
conciliate serve    # REST API only
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `conciliate init` | Create config file |
| `conciliate watch` | Watch backend + serve REST API |
| `conciliate mcp` | Run MCP server for AI assistants |
| `conciliate summary` | Display API summary |
| `conciliate diff` | Show recent changes |
| `conciliate status` | Show configuration |

## Configuration

Create `.conciliate.yaml` in your project root:

```yaml
backend_path: ../backend    # Path to your backend
framework: auto             # Backend framework (auto, fastapi, flask, express)
port: 5678                  # Server port
output_dir: .conciliate     # Output directory
```

Copy from `.conciliate.yaml.template` for all available options.

## � MCP Integration (AI Assistants)

### Claude Desktop

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "conciliate": {
      "command": "conciliate",
      "args": ["mcp"],
      "cwd": "C:\\path\\to\\your\\project"
    }
  }
}
```

### VS Code

Create `.vscode/mcp.json`:

```json
{
  "servers": {
    "conciliate": {
      "command": "conciliate",
      "args": ["mcp"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**Then**: Restart your AI assistant → Ask: "What API endpoints are available?"

### Features

- 📚 **Resources**: Full spec, summaries, diffs
- 🛠️ **Tools**: Reload, search, get endpoint details
- ⚡ **Live Updates**: Auto-detects backend changes, no manual reload
- 🎯 **Cross-session**: Keep frontend/backend AI assistants synchronized

**Full guide**: [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md)


## 📡 REST API

When running `conciliate watch` or `conciliate serve`:

| Endpoint | Description |
|----------|-------------|
| `GET /spec` | Full OpenAPI specification |
| `GET /summary` | Human-readable summary |
| `GET /diff` | Latest changes |
| `POST /reload` | Trigger spec regeneration |

## 🧪 Example

```bash
# Start example backend
cd example/backend && python main.py

# In another terminal
cd ../.. && conciliate init
# Edit .conciliate.yaml: backend_path: ./example/backend

conciliate watch
# Visit http://localhost:5678/summary
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Failed to generate spec" | Check `backend_path` in config, verify app file exists |
| "No .conciliate.yaml found" | Run `conciliate init` in your project directory |
| MCP not connecting | Restart AI assistant, verify `cwd` path in config |
| Framework not detected | Set `framework` explicitly in .conciliate.yaml |
| Extension not starting | Install Python package: `pip install conciliate` |
| Changes view empty | Wait 3 seconds for auto-refresh, or modify an endpoint |

See full troubleshooting guide in [docs/](docs/).