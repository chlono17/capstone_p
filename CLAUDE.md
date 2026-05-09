# CLAUDE.md

> Claude Code 核心設定檔。定義本專題的背景、架構、工作規範與工具整合方式。
> 每次啟動 Claude Code session 時自動載入。

---

## 專題基本資訊

- **專題名稱**：Autonomous Knowledge Synthesizer（自主知識合成器）
- **技術核心**：LLM + RAG + Agent + MCP，以本地部署為主
- **定位**：輸出驅動的學習社群平台，AI 降低輸出門檻，不替代輸出
- **目標範圍**：學校用戶（長庚大學），可申請國科會大專生研究計畫
- **GitHub Repo**：`chlono17/capstone_p`
- **Tech Lead**：chuYi（angelo95chen117）
- **團隊規模**：3–4 人，正式開始：2026/9

---

## 系統架構（Path A，細節待組員確認後可能調整）

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

### n8n 沙盒（練習用，非最終系統）
目前 `sandbox/n8n-prototype/` 是學習沙盒，讓團隊熟悉本地部署流程、Obsidian workflow、
理解本地模型限制，為正式開發做準備。已完成：
- `docker-compose.yml`：n8n + LM Studio（port 5678 / 1234）
- workflow：`知識萃取對話系統`、`notes-to-podcast`
- Obsidian vault：`sandbox/n8n-prototype/vault/`，Git 同步中

---

## Linear 任務分類（Label 系統）

每個 issue 必須貼上來源 label，代表這個任務是怎麼來的：

| Label | 說明 | 範例 |
|-------|------|------|
| `source:roadmap` | 來自 LLM Engineer / Scientist Roadmap 的學習節點 | CAP-6 到 CAP-21 |
| `source:architecture` | 對應系統架構圖某一層的功能開發任務 | Vector DB 建立、Feed 卡片設計 |
| `source:tooling` | 工具鏈、工作流程、開發環境相關 | Claude Code 設定、n8n workflow |
| `source:external` | 外部資源（論文、YT、工具）看到後衍生的任務 | Nemotron 多模態參考、RAGAS 評估 |
| `source:ops` | 專題管理、組員協調、文件維護 | 週會議程、分工確認 |

### 任務性質 Label（與來源 label 並用）

| Label | 說明 |
|-------|------|
| `type:learn` | 需要先學才能做，輸出是筆記或 demo |
| `type:build` | 直接實作，輸出是程式碼或系統 |
| `type:research` | 比較方案或評估可行性，輸出是決策文件 |

### 現有 Projects 對應架構層

| Linear Project | 對應架構層 | 主要 Issues |
|----------------|-----------|-------------|
| RAG 知識庫子系統 | STORE + AGENT（RAG） | CAP-7, CAP-8, CAP-9 |
| Agent & MCP 子系統 | AGENT（知識萃取、格式化、輔助寫作） | CAP-10 |
| 本地部署 & 推論優化子系統 | INPUT + AGENT（LLM 底層） | CAP-6, CAP-11, CAP-12 |
| ⚠️ 待新增：Feed 社群子系統 | FEED | 尚未建立 |

> Project 分類待整理，目前反映的是 Roadmap 結構而非系統架構，需對齊。

### Issue 命名規範
- Roadmap 學習：`[Engineer-N]` / `[Scientist-N]` 前綴
- 架構功能：`[系統層-功能名]` 前綴，例如 `[AGENT] RAG pipeline 整合`
- 管理任務：無前綴

---

## 工具鏈整合

### Claude Code + Linear MCP
- Linear 透過 MCP 整合，可直接在對話中建立/更新/查詢 issue
- 工作流：對話釐清需求 → 建 issue（貼 label）→ 開 branch → 實作 → PR

### GitHub
- Repo：`chlono17/capstone_p`
- Branch 命名：從 Linear issue 自動生成（`angelo95chen117/cap-N-...`）
- PR 合併後自動推進 Linear issue 狀態

### Obsidian Vault
- 路徑：`sandbox/n8n-prototype/vault/`
- 結構：`vault/notes/YYYY-MM/`，每 10 分鐘 auto-commit

---

## 工作規範

1. **先確認 Linear issue 再動工**：每個功能都要有 issue + label
2. **小步提交**：每個 commit 對應一個明確功能點
3. **AI 是加速器，不是替代品**：每行程式碼必須自己理解，不能盲目複製
4. **本地優先**：AI 功能以本地部署為主，外部 API 標注清楚（有經費支援）
5. **文件隨實作更新**：`progress.md` / `SETUP.md` 不能落後於程式碼

### Claude Code 互動方式
- 技術問題先釐清邏輯，再給方案
- 聚焦「現在最優先做什麼」
- 若討論開始蔓延會主動拉回

### 分工構想（待組員確認）
| 角色 | 子系統 | Roadmap 對應 |
|------|--------|-------------|
| 組員 A | Vector Storage + RAG | Engineer 2–3 |
| 組員 B | Agent 框架 + MCP | Engineer 5 |
| 組員 C | 本地部署 + 推論優化 | Engineer 6–7 |
| chuYi | 整體架構 + Feed 設計 + 管理 | 全段 |

---

## 環境快速參考

```bash
docker compose up -d                           # 啟動
docker compose down                            # 停止
docker compose logs -f n8n                     # 看 log
docker compose --profile import up n8n-import  # 匯入 workflow
```

- n8n UI：`http://localhost:5678`
- LM Studio API：`http://localhost:1234`
- Obsidian Vault：`./sandbox/n8n-prototype/vault/`

---

*最後更新：2026-05-10 | 架構版本：Path A v0.1（待組員確認）*