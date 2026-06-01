#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Exo 分散式 LLM 安裝 ==="
echo ""

# ── 1. 確認 Python 3.11+ ──────────────────────────────────────────────
PYTHON=""
for cmd in python3.12 python3.11 python3; do
    if command -v "$cmd" &>/dev/null; then
        VER=$($cmd -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJOR=$(echo "$VER" | cut -d. -f1)
        MINOR=$(echo "$VER" | cut -d. -f2)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
            PYTHON=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "錯誤：需要 Python 3.11+，請先執行："
    echo "  brew install python@3.12"
    exit 1
fi

echo "Python: $PYTHON ($VER)"

# ── 2. 建立虛擬環境 ────────────────────────────────────────────────────
if [ ! -d ".venv" ]; then
    echo "建立虛擬環境 .venv ..."
    $PYTHON -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip --quiet

# ── 3. 安裝 Exo ────────────────────────────────────────────────────────
echo "安裝 exo-explore（首次需要幾分鐘）..."
pip install exo-explore --quiet

echo ""
echo "=== 安裝完成 ==="
echo ""
echo "下一步："
echo "  1. 確認兩台都已登入同一個 Tailscale 帳號"
echo "  2. 兩台都執行 ./start.sh"
echo "  3. 看到 'Peer discovered' 代表連線成功"
