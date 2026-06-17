#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Exo 分散式 LLM 安裝 ==="
echo ""

# ── 1. 修正 shell profile 權限（部分 Mac 是 root 擁有）─────────────────
for f in ~/.bash_profile ~/.tcshrc ~/.zshenv ~/.profile; do
    if [ -f "$f" ] && [ "$(stat -f '%Su' "$f")" != "$(whoami)" ]; then
        echo "修正 $f 擁有者..."
        sudo chown "$(whoami)" "$f"
    fi
done

# ── 2. 安裝 Rust（exo-rs 需要）────────────────────────────────────────
if ! command -v rustc &>/dev/null && [ ! -f "$HOME/.cargo/bin/rustc" ]; then
    echo "安裝 Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
fi
export PATH="$HOME/.cargo/bin:$PATH"
echo "Rust: $(rustc --version)"

# ── 3. 安裝 uv（exo 的套件管理器，pip 無法處理 exo-rs）──────────────
if ! command -v uv &>/dev/null && [ ! -f "$HOME/.local/bin/uv" ]; then
    echo "安裝 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
source "$HOME/.local/bin/env" 2>/dev/null || true
export PATH="$HOME/.local/bin:$PATH"
echo "uv: $(uv --version)"

# ── 4. Clone exo ───────────────────────────────────────────────────────
if [ ! -d "exo-src" ]; then
    echo "Clone exo from GitHub..."
    git clone https://github.com/exo-explore/exo.git exo-src
else
    echo "exo-src 已存在，跳過 clone"
fi

# ── 5. 安裝依賴 ────────────────────────────────────────────────────────
cd exo-src

# 檢查是否有完整 Xcode（有才能編 MLX Metal）
if xcrun --find metal &>/dev/null 2>&1; then
    echo "偵測到完整 Xcode，啟用 MLX Metal 模式..."
    uv sync
else
    echo "未偵測到完整 Xcode，使用 CPU 模式（--extra mlx-none）"
    echo "提示：安裝 App Store 的 Xcode 後重跑此腳本可啟用更快的 MLX 推論"
    uv sync --extra mlx-none
fi

# ── 6. Build dashboard（前端 UI）──────────────────────────────────────
if [ -d "dashboard" ]; then
    echo "Build dashboard..."
    cd dashboard
    npm install --silent
    npm run build
    cd ..
fi

cd "$SCRIPT_DIR"

echo ""
echo "=== 安裝完成 ==="
echo ""
echo "下一步："
echo "  1. 確認兩台都已從 menubar 開啟 Tailscale app 並登入同一帳號"
echo "  2. 兩台都執行 ./start.sh"
echo "  3. 看到 'Peer discovered' 代表連線成功"
