# Autonomous Knowledge Synthesizer

輸出驅動的學習社群平台。AI 降低輸出門檻，不替代輸出。

- **技術核心**：本地 LLM（Ollama）+ RAG + Agent + MCP
- **目標用戶**：長庚大學學生
- **正式開發**：2026/9 啟動

---

## 系統架構

```
┌─────────────────────────── INPUT ───────────────────────────┐
│  手寫/相機(OCR)  │  語音(STT)  │  文字/Markdown  │  網頁/PDF  │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌─────────────────── AGENT 處理核心（本地 LLM + MCP）──────────┐
│  知識萃取(Q&A對話)  │  格式化(手寫→MD)  │  輔助寫作(架構提示)  │
│  本地 LLM(Ollama)  │  RAG 檢索         │  Podcast 生成(TTS)  │
└──────────────┬──────────────────────────────────────────────┘
               ↓
┌──────────────────────────── STORE ──────────────────────────┐
│  Vector DB(ChromaDB/FAISS)  │  結構化DB(用戶/貼文/標籤)  │  媒體儲存  │
└──────────────┬──────────────────────────────────────────────┘
               ↓
┌──────────────────────── FEED（學校用戶）────────────────────┐
│  知識卡片(標籤/摘要/問題)  │  Podcast 播放  │  互動(問題/留言)  │
│  發文介面(使用者寫 + Agent 旁輔)  │  個人動態(學習狀況)         │
└─────────────────────────────────────────────────────────────┘
```

詳細說明見 [`docs/architecture.md`](docs/architecture.md)。

---

## 目錄結構

```
capstone_project/
├── docs/                  # 架構文件與決策記錄
│   ├── architecture.md    # 系統架構說明
│   └── decisions/         # ADR（架構決策記錄）
├── src/                   # 正式系統程式碼
│   ├── agent/             # AGENT 層：知識萃取、RAG、Podcast 生成
│   ├── store/             # STORE 層：Vector DB、結構化 DB、媒體儲存
│   ├── feed/              # FEED 層：知識卡片、互動、發文介面
│   └── input/             # INPUT 層：OCR、STT、Markdown、PDF
├── sandbox/               # 學習沙盒（n8n prototype，非正式系統）
│   └── n8n-prototype/     # n8n workflow + Obsidian vault
├── notes/                 # 工具學習筆記（Docker、Git）
├── scripts/               # 工具腳本
└── tests/                 # 測試
```

---

## 快速開始

### 啟動沙盒（n8n + LM Studio）

```bash
cd sandbox/n8n-prototype
docker compose up -d
```

- n8n UI：`http://localhost:5678`
- LM Studio API：`http://localhost:1234`

環境變數設定請參考 `sandbox/n8n-prototype/SETUP.md`。

---

## 團隊

| 角色 | 子系統 |
|------|--------|
| 組員 A | Vector Storage + RAG |
| 組員 B | Agent 框架 + MCP |
| 組員 C | 本地部署 + 推論優化 |
| chuYi | 整體架構 + Feed 設計 + 管理 |
