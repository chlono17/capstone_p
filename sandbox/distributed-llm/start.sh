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

# 兩台機器的 Tailscale IP
M4_MINI_TS="100.125.4.81"
M1_AIR_TS="100.103.131.88"

# 固定 libp2p port（這台用 52416，M4 Mini 若重啟需更新 M4_LIBP2P_PORT）
MY_LIBP2P_PORT=52416
M4_LIBP2P_PORT=52416  # M4 Mini 固定 libp2p port（與 M1 Air 同 port，不同主機無衝突）

# 自動判斷對方的 Tailscale IP 與 libp2p port
if [ "$TS_IP" = "$M4_MINI_TS" ]; then
    PEER_IP="$M1_AIR_TS"
    PEER_LIBP2P_PORT="$MY_LIBP2P_PORT"
    MACHINE="M4 Mac Mini"
elif [ "$TS_IP" = "$M1_AIR_TS" ]; then
    PEER_IP="$M4_MINI_TS"
    PEER_LIBP2P_PORT="$M4_LIBP2P_PORT"
    MACHINE="M1 MacBook Air"
else
    PEER_IP=""
    PEER_LIBP2P_PORT=""
    MACHINE="Unknown ($TS_IP)"
fi

echo "=== 啟動 Exo ==="
echo ""
echo "本機              ：$MACHINE ($TS_IP)"
echo "API endpoint      ：http://${TS_IP}:52415/v1"
echo "libp2p port       ：$MY_LIBP2P_PORT"
if [ -n "$PEER_IP" ]; then
    echo "Bootstrap peer    ：/ip4/${PEER_IP}/tcp/${PEER_LIBP2P_PORT}"
fi
echo ""
echo "使用 Ctrl+C 停止"
echo "────────────────────────────────────────────"

if [ -n "$PEER_IP" ]; then
    uv run exo --libp2p-port $MY_LIBP2P_PORT \
               --bootstrap-peers "/ip4/${PEER_IP}/tcp/${PEER_LIBP2P_PORT}"
else
    uv run exo --libp2p-port $MY_LIBP2P_PORT
fi
