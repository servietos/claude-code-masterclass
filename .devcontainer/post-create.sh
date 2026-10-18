#!/usr/bin/env bash

set -euo pipefail

echo "Post-creation setup starting..."

TARGET_USER="${SUDO_USER:-${DEVCONTAINER_USER:-${USERNAME:-${USER:-}}}}"
if [[ -z "${TARGET_USER}" ]] || ! id -u "${TARGET_USER}" >/dev/null 2>&1; then
  TARGET_USER="$(awk -F: '$3>=1000 && $1!="nobody" {print $1; exit}' /etc/passwd)"
fi
TARGET_GROUP="$(id -gn "${TARGET_USER}" 2>/dev/null || true)"
if [[ -z "${TARGET_GROUP}" ]]; then
  TARGET_GROUP="${TARGET_USER}"
fi
echo "Ensuring /workspace is owned by ${TARGET_USER}:${TARGET_GROUP}"
sudo chown -R "${TARGET_USER}:${TARGET_GROUP}" /workspace
sudo chmod -R u+rwX,go+rX /workspace

echo "Cleaning .NET build artifacts under demos, labs and src..."
find /workspace/demos /workspace/labs /workspace/src -type d \( -name node_modules -o -name .venv \) -prune -o \
  -type d \( -name obj -o -name bin \) -exec rm -rf {} + 2>/dev/null || true

cd /workspace

GLOBAL_NPM_PREFIX="$(npm prefix -g 2>/dev/null || true)"
if [[ -n "${GLOBAL_NPM_PREFIX}" ]]; then
  GLOBAL_NPM_BIN="${GLOBAL_NPM_PREFIX}/bin"
  if [[ -d "${GLOBAL_NPM_BIN}" ]]; then
    if ! echo ":${PATH}:" | grep -q ":${GLOBAL_NPM_BIN}:"; then
      export PATH="${GLOBAL_NPM_BIN}:${PATH}"
    fi
    if [[ ! -f /etc/profile.d/npm-global-path.sh ]] || ! grep -q "${GLOBAL_NPM_BIN}" /etc/profile.d/npm-global-path.sh 2>/dev/null; then
      echo "export PATH=\"${GLOBAL_NPM_BIN}:\\$PATH\"" | sudo tee /etc/profile.d/npm-global-path.sh >/dev/null
    fi
  fi
fi

export PATH="$HOME/.dotnet/tools:$HOME/.local/bin:$PATH"
if ! grep -q ".dotnet/tools" ~/.bashrc 2>/dev/null; then
  echo 'export PATH="$PATH:$HOME/.dotnet/tools:$HOME/.local/bin"' >> ~/.bashrc
fi

echo "Installing Claude Code CLI..."
npm install -g @anthropic-ai/claude-code

echo "Installing uv (Python MCP servers in demos/04-mcp, demos/10-sdk-managed-agents, src)..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "Installing Hugo Extended (labs/09-agentic-devops)..."
HUGO_VERSION=0.128.0
curl -sSL -o /tmp/hugo.deb "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.deb"
sudo dpkg -i /tmp/hugo.deb
rm -f /tmp/hugo.deb

echo "Installing Bicep CLI (demos/09-agentic-devops)..."
az bicep install

echo "Installing a browser for the Playwright and Chrome DevTools MCP servers..."
npx --yes playwright install --with-deps chrome || npx --yes playwright install --with-deps chromium

echo ""
echo "Post-creation setup completed successfully!"
echo ""
echo "Available tools:"
echo "  - .NET SDK: $(dotnet --version)"
echo "  - Node.js: $(node --version)"
echo "  - Python: $(python3 --version)"
echo "  - uv: $($HOME/.local/bin/uv --version)"
echo "  - Java: $(java --version | head -1)"
echo "  - Maven: $(mvn --version | head -1)"
echo "  - Hugo: $(hugo version)"
echo "  - Terraform: $(terraform version | head -1)"
echo "  - PowerShell: $(pwsh --version | head -1)"
echo "  - Azure CLI: $(az --version | head -1)"
echo "  - Claude Code: $(claude --version)"
echo ""
echo "Run 'claude' to sign in, then open any project under demos/, labs/ or src/."
