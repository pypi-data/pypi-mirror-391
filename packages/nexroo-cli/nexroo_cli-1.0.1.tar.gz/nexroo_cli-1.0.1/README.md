# Nexroo CLI

CLI wrapper for Nexroo workflow engine. See docs at https://docs.nexroo.ai

## Installation

### Quick Install (Recommended)

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/nexroo-ai/nexroo-cli/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/nexroo-ai/nexroo-cli/main/install.ps1 | iex
```

### Manual Install

```bash
pip install nexroo-cli
nexroo install
```

### Installing Nexroo addons

HERE DOC HOW TO ADD ROOMS-PKG

## Quick Start

After installation, authenticate and run your first workflow:

```bash
# Authenticate with Synvex
nexroo login

# Run a workflow
nexroo run workflow.json
```

## Usage

### Authentication Commands

#### Login
```bash
nexroo login
```

Opens browser for Zitadel authentication. Credentials stored encrypted for 30 days.

#### Logout
```bash
nexroo logout
```

Clears saved credentials.

#### Status
```bash
nexroo status
```

Shows authentication status and token expiration.

### Running Workflows

**With authentication** (SaaS features enabled):
```bash
nexroo run workflow.json [entrypoint]
```

**Without authentication** (local-only mode):
```bash
nexroo run workflow.json --no-auth
```

### Additional Options

All ai-rooms-script options are supported:

```bash
nexroo run workflow.json [entrypoint] [options]
```

Refer to [Nexroo Documentation](https://docs.nexroo.ai)

## Storage Locations

- Encrypted tokens: `~/.nexroo/auth_token.enc`
- Encryption key: `~/.nexroo/.key`

## Troubleshooting

### Authentication fails
```bash
nexroo logout
nexroo login
```

### Token expired
```bash
nexroo status
nexroo login   # Re-authenticate
```

## Documentation

See [Nexroo Documentation](https://docs.nexroo.ai) to know how to use Nexroo workflow engine.

## License

PolyForm Noncommercial License 1.0.0 - see [LICENSE](./LICENSE) file for details.
Or on <https://polyformproject.org/licenses/noncommercial/1.0.0>

## Support

- GitHub Issues: https://github.com/nexroo-ai/nexroo-cli/issues