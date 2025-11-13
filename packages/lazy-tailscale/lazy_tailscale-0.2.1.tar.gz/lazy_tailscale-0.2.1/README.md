> [!IMPORTANT]
> **Active Development ❗**
> 
> This app is under active development and considered alpha software. Expect bugs and incomplete features.
> The list of features is more a wishlist/roadmap and most of them are not implemented yet.

# lazytailscale
A terminal UI for managing Tailscale, inspired by [lazydocker](https://github.com/jesseduffield/lazydocker) and [lazygit](https://github.com/jesseduffield/lazygit).

## Features
### Local Tailscale Management
- View connection status and node information
- Connect/disconnect from your tailnet
- Switch between exit nodes
- SSH into external devices
- Ping external devices
- Update Tailscale version

### Account-Wide Management (via API)
- View all devices across your tailnet
- Manage device authorizations and approvals
- Configure ACLs and DNS settings
- Monitor device activity and last seen status
- Manage device tags and attributes
- View and manage shared nodes

## Installation
### Prerequisites
- Python 3.10+
- `tailscale` CLI installed and `tailscaled` running on your machine
- Currently only supports macOS

### Install via pipx
lazytailscale can be installed from PyPI using pipx:
```bash
pipx install lazytailscale
```

## Environment Variables
```
LAZY_TAILSCALE_API_KEY: API key for Tailscale. You can generate one from the Tailscale admin console.
```

## Development
### Run Locally
```bash
source .env && uv run textual run --dev -c lazytailscale --port 7342
```
```bash
uv run textual console --port 7342 -x SYSTEM -x DEBUG -x INFO
```

### Publish New Version
```bash
uv build
uv run twine upload dist/*
```
