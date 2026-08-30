# CLAUDE.md

> Claude Code 核心設定檔。定義本專題的背景、架構、工作規範與工具整合方式。
> 每次啟動 Claude Code session 時自動載入。

---

## 專題基本資訊

- **專題名稱**：IT 事件助理
- **技術核心**：LangGraph + RAG + MCP，以本地部署為主
- **定位**：協助 IT 維運事件處理的智慧助理，涵蓋智慧洞察、人員調度、總結追蹤、知識沉澱四大功能
- **驗證策略**：主場景用團隊自身開發歷程（GitHub Issues/PR/CI log）當真實資料，公開資料集（LogHub、Kaggle ticket dataset schema、HuggingFace IT ticket 分類）補強核心模型能力驗證
- **GitHub Repo**：本 repo
- **Tech Lead**：（待定）
- **團隊規模**：（待定）

> Repo 為 public：本文件與其他文件已避免寫出學校名稱、真實姓名/GitHub handle、確切人數與時程。但 git remote 本身已包含 GitHub 使用者代稱，文件層級無法做到完全匿名，若需要徹底匿名須另外處理 org/repo 名稱本身。

---

## 系統架構（v0.1，細節待組員確認後可能調整）

```
┌───────────────────────── 共用基礎層 ─────────────────────────┐
│      LangGraph Agent 框架  │  RAG 檢索  │  MCP 工具整合       │
│                      本地部署（推論後端）                     │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌──────────┬──────────────┬──────────────┬─────────────────────┐
│ 智慧洞察  │  人員調度     │  總結追蹤     │  知識沉澱            │
│ log/SOP  │  行事曆/排班   │  事件報告生成  │  回寫知識庫          │
│ 比對      │  API 整合     │              │                     │
└──────────┴──────────────┴──────────────┴─────────────────────┘
```

### 資料來源策略

| 功能 | 主資料來源 | 補強資料來源 |
|------|-----------|-------------|
| 智慧洞察 | 團隊自身 GitHub Issues、PR 討論、CI log | LogHub（HDFS/BGL/Thunderbird，公開、有異常標籤，學界標準 benchmark） |
| 人員調度 | 團隊自身行事曆/排班 | 不需要外部資料集，屬通用 API 整合能力 |
| 總結追蹤 | 團隊真實踩過的 bug/issue 討論串 | Kaggle customer-support-ticket-dataset（只借欄位 schema：type/subject/description/resolution/priority，不用其消費性支援內容） |
| 知識沉澱 | GitHub Issues 本身、知識庫（見下方） | HuggingFace IT ticket 分類資料集，用來校準知識庫標籤體系 |

> 核心邏輯：只有「智慧洞察」真正需要一批已知結論的歷史 case 才能驗證比對準不準，所以用公開、有 ground truth 標籤的 log 資料集驗證；其餘三個功能本質上是團隊自身協作資料就是最好的訓練/demo 素材，不需要模擬企業情境。

### n8n 沙盒（舊題目時期練習，非最終系統）
`sandbox/n8n-prototype/` 是舊題目（Autonomous Knowledge Synthesizer）時期的學習沙盒，讓團隊熟悉本地部署流程、n8n workflow，概念上不再直接對應現在的四大功能。其 Obsidian vault 內容已搬遷至 Linear Document，資料夾已從 repo 移除（備份於本機）。sandbox 本身（docker-compose、workflow）是否保留待後續決定。

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
| ⚠️ 待新增：智慧洞察子系統 | 智慧洞察（log/SOP 比對） | 尚未建立 |
| ⚠️ 待新增：人員調度子系統 | 人員調度（行事曆/排班） | 尚未建立 |
| ⚠️ 待新增：總結追蹤子系統 | 總結追蹤（事件報告生成） | 尚未建立 |
| ⚠️ 待新增：知識沉澱子系統 | 知識沉澱（回寫知識庫） | 尚未建立 |

> Project 分類待整理，題目已轉向 IT 事件助理，舊題目（RAG 知識庫/Agent & MCP/本地部署/Feed 社群）的 Project 分類已不適用。

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
- Repo：本 repo
- Branch 命名：從 Linear issue 自動生成（`<github-handle>/cap-N-...`）
- PR 合併後自動推進 Linear issue 狀態

### 共筆 / 知識庫
- 共筆改用 Linear Document（原本規劃的 Obsidian vault 已淘汰，內容搬遷至 Linear）
- 任務與進度一律以 Linear issue 追蹤，不再依賴 vault 裡的 `progress.md`

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
| 角色 | 子系統 |
|------|--------|
| 組員 A | 智慧洞察（log/SOP 比對） |
| 組員 B | 人員調度（行事曆/排班） |
| 組員 C | 總結追蹤（事件報告生成） |
| 組員 D | 知識沉澱 + 整體架構 + 管理 |

---

## 環境快速參考

`sandbox/n8n-prototype/` 的 docker/n8n 指令仍可用於該學習沙盒（見該目錄下 SETUP.md），與正式系統無關，故不在此重複列出。

---

*最後更新：2026-08-31 | 架構版本：v0.1（待組員確認）*