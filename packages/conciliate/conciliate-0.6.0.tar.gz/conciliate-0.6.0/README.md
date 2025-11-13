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

## Quick Start

### Python Package

```bash
pip install conciliate
```

### VS Code Extension

**Install from VSIX**:
1. Download `conciliate-mcp-0.1.0.vsix` from releases
2. VS Code → Extensions → `...` → Install from VSIX
3. Open your project folder
4. Run `Conciliate: Initialize` from Command Palette
5. Edit `.conciliate.yaml` to set `backend_path`
6. Run `Conciliate: Start` to begin monitoring

**install globally**: `pip install conciliate` (required for extension)

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

### Multi-Source Configuration (v0.5.0+)

Track multiple API sources simultaneously - perfect for microservices, remote APIs, or monitoring production:

```yaml
# Multiple sources (local + remote)
sources:
  - name: "Main API"
    type: local
    path: ./backend
    framework: fastapi
    
  - name: "Auth Service"
    type: local
    path: ../auth-service
    framework: flask
    
  - name: "Staging API"
    type: url
    url: https://staging.example.com/openapi.json
    poll_interval: 300  # seconds
    headers:
      Authorization: "Bearer ${STAGING_TOKEN}"
      
  - name: "Production API"
    type: url
    url: https://api.example.com/openapi.json
    poll_interval: 600

# Server configuration
server:
  port: 5678
```

**Source Types**:
- **`local`**: File system watching (like traditional single backend)
- **`url`**: HTTP polling for remote OpenAPI specs

**Use Cases**:
- 🏗️ Microservices in different repositories
- 🔄 Frontend/Backend split repos
- 📊 Monitor staging/production APIs
- 🔍 Track third-party API changes (Stripe, GitHub, etc.)
- 📚 Aggregate multiple services into one unified spec

**Environment Variables**: Use `${VAR}` syntax for secrets (e.g., `${API_TOKEN}`)

**VS Code**: Sources appear in "API Sources" view with refresh buttons and status indicators

See `example/.conciliate.multi-source.yaml` for complete configuration example.

## 🔗 MCP Integration (AI Assistants)

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

## 🎨 VS Code Extension

### Features
- **Status Bar**: Server status with one-click start/stop
- **API Explorer**: Browse all endpoints with method badges (GET, POST, PUT, DELETE)
- **Search & Filter**: Find endpoints by path, method, or description
- **Changes View**: Real-time diff tracking (added/removed/modified endpoints)
- **Commands**: Initialize, start, stop, reload, view diff, view spec
- **Auto-refresh**: Detects backend changes every 3 seconds

### Usage
1. Open workspace with backend code
2. Command Palette → `Conciliate: Initialize`
3. Edit `.conciliate.yaml`: set `backend_path` to your backend folder
4. Command Palette → `Conciliate: Start`
5. API Explorer sidebar shows all endpoints
6. Use search icon to filter endpoints
7. Changes view updates when you modify endpoints

**Settings**:
- `conciliate.autoStart`: Auto-start server on workspace open (default: true)
- `conciliate.port`: Server port (default: 5678)
- `conciliate.pythonPath`: Python executable path (default: "python")
- `conciliate.autoRefresh`: Auto-refresh changes view (default: true)
- `conciliate.refreshInterval`: Refresh interval in ms (default: 3000)

**Package extension**: `cd conciliate-mcp && vsce package`

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

## Roadmap

### Free Tier ✨
- ✅ Core engine (watcher, spec gen, diff, REST API)
- ✅ MCP integration with live updates
- ✅ Flask & Express framework support
- ✅ VS Code extension (status bar, API explorer, changes view, auto-refresh)
- ✅ Mock server mode (fake API generation)
- ✅ Multi-Workspace Support

### Pro Tier 💎 ($9-15/month)
- Multi-backend support (microservices, aggregated specs)
- Enhanced AI diff narration (GPT-powered change descriptions)

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