# 分散式 LLM 設定指南

M4 Mac Mini + M1 MacBook Air 合力跑 Qwen2.5 32B。
不需要 LM Studio，不需要手動裝 MLX，Exo 全包。

---

## 角色分工

| 機器 | 角色 | 負責 |
|------|------|------|
| M4 Mac Mini | Primary | 跑 Exo + n8n + Open WebUI，對外提供 API |
| M1 MacBook Air | Worker | 只跑 Exo，貢獻 12GB 記憶體給模型 |

兩台都要跑 Exo，少了任何一台只能跑 14B 以下。

---

## 記憶體估算

| 模型 | 需要 | 單台 16GB 夠嗎 | 兩台合計夠嗎 |
|------|------|----------------|--------------|
| Qwen2.5 14B Q4_K_M | ~9 GB | ✅ 單台即可 | ✅ |
| Qwen2.5 32B Q4_K_M | ~20 GB | ❌ | ✅（兩台合 ~24GB 可用） |

---

## Phase 1：Tailscale（兩台都做）

### 安裝 Tailscale

```bash
# 如果沒裝（會自動開 browser 讓你登入）
brew install tailscale
sudo tailscale up
```

### 確認 Tailscale IP

```bash
tailscale ip -4
# 應該是 100.x.x.x
```

### 確認兩台互通

```bash
# 在 M1 Air 上 ping M4 Mini 的 Tailscale IP
ping -c 3 <M4-Mini-的-100.x.x.x>
```

> **暫停點**：兩台都確認 Tailscale IP 後再繼續。

---

## Phase 2：Exo 安裝（兩台都做）

```bash
# 在 capstone_project 根目錄
git pull

cd sandbox/distributed-llm
chmod +x setup.sh start.sh
./setup.sh
```

安裝完成後確認：
```bash
source .venv/bin/activate
exo --version
```

---

## Phase 3：啟動分散式推論

### 步驟 1：M1 MacBook Air 先跑

```bash
cd sandbox/distributed-llm
./start.sh
```

看到以下代表在等待配對：
```
Exo node started. Waiting for peers...
```

### 步驟 2：M4 Mac Mini 跑

```bash
cd sandbox/distributed-llm
./start.sh
```

兩台出現 `Peer discovered` 代表連線成功，模型層級分配自動完成。

### 確認 API 有回應

在 M4 Mac Mini 上執行：
```bash
curl http://localhost:52415/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-exo" \
  -d '{
    "model": "mlx-community/Qwen2.5-14B-Instruct-4bit",
    "messages": [{"role": "user", "content": "你好，請用繁體中文回答"}],
    "stream": false
  }'
```

> 首次呼叫會先下載模型（14B 約 9GB，32B 約 20GB），需要等待。

---

## Phase 4：更新 n8n 設定

複製並編輯 n8n 的環境變數：

```bash
cd sandbox/n8n-prototype
# 編輯 .env，把 LLM_BASE_URL 和 LLM_MODEL 改成：
```

```dotenv
# Exo endpoint（用 M4 Mini 的 Tailscale IP，或同台用 localhost）
LLM_BASE_URL=http://<M4-Mini-Tailscale-IP>:52415/v1

# 兩台都在線時用 32B
LLM_MODEL=mlx-community/Qwen2.5-32B-Instruct-4bit

# 只有單台時改成 14B
# LLM_MODEL=mlx-community/Qwen2.5-14B-Instruct-4bit
```

```bash
# 重啟 n8n 讓環境變數生效
docker compose down && docker compose up -d
```

n8n workflow **不需要改動**，直接吃新的 endpoint。

---

## Phase 5：Open WebUI（在 M4 Mac Mini 上執行）

```bash
cd sandbox/distributed-llm

# 複製 .env
cp .env.example .env
# 把 LLM_BASE_URL 改成你的值（同台可以用 localhost）

cd open-webui
docker compose up -d
```

打開 http://localhost:3000，第一次進去需要建立帳號（本地，不需要外部服務）。

在 Open WebUI 的 Admin Panel > Settings > Connections 確認 OpenAI API 那欄顯示你填的 endpoint。

---

## Phase 6：測試 32B vs 14B

### 測 14B（單台或雙台都行）

```bash
curl http://localhost:52415/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-exo" \
  -d '{"model":"mlx-community/Qwen2.5-14B-Instruct-4bit","messages":[{"role":"user","content":"用繁體中文解釋 RAG 是什麼"}],"stream":false}'
```

### 測 32B（需要兩台同時在線）

```bash
curl http://localhost:52415/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-exo" \
  -d '{"model":"mlx-community/Qwen2.5-32B-Instruct-4bit","messages":[{"role":"user","content":"用繁體中文解釋 RAG 是什麼"}],"stream":false}'
```

---

## 未來擴充點

### 接 LangChain

`LLM_BASE_URL` + `LLM_API_KEY` 直接傳給 `ChatOpenAI`：

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://<tailscale-ip>:52415/v1",
    api_key="sk-exo",
    model="mlx-community/Qwen2.5-32B-Instruct-4bit"
)
```

### 接 MCP

Open WebUI 支援 MCP Tool Server，在 Admin Panel > Tools 裡加入即可。
n8n 那邊則是在 workflow 加一個 HTTP Request 節點呼叫 MCP server。

---

## 常見問題

**Q：兩台 ping 得到但 Exo 沒有 `Peer discovered`**
確認兩台的防火牆沒有擋 UDP。Tailscale 預設應該沒問題，如果有問題試試：
```bash
# macOS 防火牆通常不擋，但確認一下
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

**Q：只有一台在線想跑 32B**
不行，32B 需要兩台合計記憶體。改用 14B：
```bash
# 改 .env 的 LLM_MODEL，重啟 n8n
```

**Q：模型下載到哪裡**
`~/.cache/exo/`，不進 git，兩台分別下載各自需要的 layers。
