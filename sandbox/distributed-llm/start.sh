#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "錯誤：還沒安裝，請先執行 ./setup.sh"
    exit 1
fi

source .venv/bin/activate

# 取得本機 Tailscale IP（沒裝就顯示 localhost）
TS_IP=$(tailscale ip -4 2>/dev/null || echo "localhost")

echo "=== 啟動 Exo ==="
echo ""
echo "本機 Tailscale IP：$TS_IP"
echo "API endpoint    ：http://${TS_IP}:52415/v1"
echo ""
echo "把上面的 endpoint 填入 n8n 的 LLM_BASE_URL"
echo "使用 Ctrl+C 停止"
echo "────────────────────────────────────────────"

exo
