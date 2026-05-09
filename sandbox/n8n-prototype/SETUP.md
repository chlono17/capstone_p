# 安裝指南

這份文件讓你從零開始，把整個系統跑起來。大約需要 20–30 分鐘。

---

## 你需要安裝的東西

| 工具 | 用途 | 下載 |
|------|------|------|
| Docker Desktop | 跑 n8n | https://www.docker.com/products/docker-desktop |
| LM Studio | 跑本地 AI 模型 | https://lmstudio.ai |
| Obsidian | 看和寫筆記 | https://obsidian.md |
| Git | 同步筆記 | https://git-scm.com（Mac 通常已內建） |

---

## 第一步：Clone repo

```bash
git clone https://github.com/你的org/para-ai-system.git
cd para-ai-system
```

---

## 第二步：設定 .env

```bash
cp .env.example .env
```

用任何文字編輯器打開 `.env`，至少填這兩個：

```
AUTHOR_NAME=你的名字
LLM_MODEL=你在 LM Studio 載入的模型名稱
```

其他欄位保持預設值即可，之後有需要再改。

---

## 第三步：安裝並設定 LM Studio

### Mac（M1/M2/M3/M4）
1. 下載並安裝 LM Studio
2. 打開 LM Studio → 左側選 **搜尋** → 搜尋 `mlx-community/Llama-3.2-3B-Instruct-4bit`
3. 下載模型（約 2 GB）
4. 左側選 **開發者（Developer）** → 選剛才下載的模型 → 點 **啟動伺服器（Start Server）**
5. 確認畫面顯示 `Running on port 1234`

### Windows
1. 下載並安裝 LM Studio
2. 打開 LM Studio → 搜尋 `llama-3.2-3b-instruct`（選 Q4 版本）
3. 下載模型
4. 左側選 **開發者（Developer）** → 載入模型 → 點 **啟動伺服器（Start Server）**
5. 確認畫面顯示 `Running on port 1234`

> **注意**：每次要使用系統前，都要先確認 LM Studio Server 是執行中的狀態。

---

## 第四步：啟動 n8n

```bash
# 首次啟動（同時匯入 workflow）
docker compose up -d
docker compose --profile import up n8n-import

# 之後每次啟動只需要
docker compose up -d
```

打開瀏覽器，進入 `http://localhost:5678`

- 帳號：你在 `.env` 填的 `N8N_USER`（預設 `admin`）
- 密碼：你在 `.env` 填的 `N8N_PASSWORD`（預設 `changeme`，請改掉）

進去之後應該可以看到 **知識萃取對話系統** 這個 workflow，把它啟用（右上角 toggle）。

---

## 第五步：設定 Obsidian

1. 安裝 Obsidian
2. 打開 Obsidian → **Open folder as vault**
3. 選擇 `para-ai-system/vault/` 這個資料夾
4. 安裝 Obsidian Git plugin：
   - 設定 → Community plugins → 關閉 Safe mode → Browse → 搜尋 `Obsidian Git` → 安裝並啟用
5. Obsidian Git plugin 設定：
   - Vault backup interval：`10`（每 10 分鐘自動 commit + push）
   - Pull updates on startup：開啟
   - Auto push：開啟

---

## 確認系統正常運作

1. LM Studio Server 是執行中的 ✓
2. `docker compose up -d` 執行完成 ✓
3. `http://localhost:5678` 可以打開，看到 workflow ✓
4. Obsidian 打開 vault 資料夾，看到 `notes/`、`progress.md` ✓
5. 測試對話：在 n8n 的 Chat UI 貼一段文字，輸入「完成」，確認 `vault/notes/` 出現新筆記 ✓

---

## 常用指令

```bash
# 啟動
docker compose up -d

# 停止
docker compose down

# 看 n8n log（除錯用）
docker compose logs -f n8n

# 更新 workflow（改了 JSON 後執行）
docker compose --profile import up n8n-import
```

---

## 遇到問題？

| 問題 | 可能原因 |
|------|----------|
| n8n 無法連到 LM Studio | LM Studio Server 沒啟動，或 port 不是 1234 |
| workflow 執行失敗 | 打開 n8n → 點進 workflow → 看紅色節點的錯誤訊息 |
| 筆記沒出現在 Obsidian | 確認 vault 資料夾路徑正確，Docker 有掛載到 `./vault` |
| Windows Docker 啟動失敗 | 確認 WSL2 已安裝，Docker Desktop 設定有啟用 WSL2 backend |
