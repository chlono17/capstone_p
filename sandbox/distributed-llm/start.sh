#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$SCRIPT_DIR/exo-src" ]; then
    echo "錯誤：還沒安裝，請先執行 ./setup.sh"
    exit 1
fi

cd "$SCRIPT_DIR/exo-src"

export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
source "$HOME/.local/bin/env" 2>/dev/null || true

TS_IP=$(tailscale ip -4 2>/dev/null || echo "localhost")

echo "=== 啟動 Exo ==="
echo ""
echo "本機 Tailscale IP：$TS_IP"
echo "API endpoint    ：http://${TS_IP}:52415/v1"
echo ""
echo "把上面的 endpoint 填入 n8n 的 LLM_BASE_URL"
echo "使用 Ctrl+C 停止"
echo "────────────────────────────────────────────"

uv run exo
