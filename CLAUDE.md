# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專題背景
大學畢業專題，主題「個人知識庫 + AI Agent」。三人組，全 AI major。
- 指導教授：邢正蓉（長庚大學通識中心），背景機器學習／平行計算／物理
- GitHub org：Dr-PenPen
- 組員：2 台 Mac M1、2 台 Windows

## 系統目標
降低組員寫共筆的門檻，透過對話自動生成結構化筆記存入知識庫。

核心理念：人掌管知識，AI 是輔助工具。
- INPUT：透過 NotebookLM 整理外部資料（信任的 RAG）
- OUTPUT：組員透過對話產出問題，沒想法時由本地模型引導提問
- 沉澱：收集 input/output 整理成 markdown，存入 Obsidian vault

## 技術棧
- **n8n**（本地 Docker，每人各自跑，不共用 server）
- **LM Studio**（本地模型執行環境，每人各自裝）
  - Mac M1：MLX backend（速度約 2x Ollama，記憶體少 50%）
  - Windows：llama.cpp / CUDA backend
  - API：OpenAI-compatible，port 1234
- **Obsidian**（知識庫，markdown 格式，vault 在 `para-ai-system/vault/`）
- **Obsidian Git plugin**（自動 push/pull，每 10 分鐘同步）
- **Git / GitHub**（共用 vault 同步 + 程式碼版控）
- **NotebookLM**（前置 input 整理，不在自動化流程內）

> Ollama 已棄用：喚醒時間慢，改用 LM Studio（常駐 Server 模式，無 coldstart）

## 系統架構
```
外部資料上傳
  → NotebookLM 整理（人工步驟）
  → 組員閱讀
  → n8n Chat UI 輸入（貼上 NotebookLM 摘要）
  → 本地模型對話索取問題
     - 有想法 → 使用者自己輸入
     - 沒想法 → 模型根據 input 主動提問
  → 輸入「完成」或「done」結束對話
  → n8n 整理成 markdown 寫入 vault/notes/
  → Obsidian Git 自動 push → 組員 pull 看到新筆記
```

## 專案結構

實作主體在 `../para-ai-system/`：
```
para-ai-system/
  docker-compose.yml          ← n8n 容器定義
  .env.example                ← 複製成 .env 並填值
  SETUP.md                    ← 組員安裝指南（中文）
  n8n/workflows/
    knowledge-chat.json       ← 核心：知識萃取對話系統
    notes-to-podcast.json     ← 選用：筆記轉 Podcast
  vault/                      ← Obsidian vault（git 同步）
    notes/YYYY-MM/            ← n8n 生成的筆記
    raw/YYYY-MM/              ← 原始對話 JSON（不進 git）
    templates/                ← 筆記模板
    progress.md               ← 進度追蹤（checkbox）
    .obsidian/                ← Obsidian 設定 + Git plugin 設定
  backlog/ideas.md
  .claude/commands/
    summary.md                ← /summary：快速摘要指定檔案
    todo.md                   ← /todo：掃描所有 action items
```

## 常用指令

### n8n 啟動 / 停止
```bash
cd ../para-ai-system

# 首次啟動
cp .env.example .env   # 填入真實值
docker compose up -d
docker compose --profile import up n8n-import   # 匯入 workflow

# 之後每次啟動
docker compose up -d

# 停止
docker compose down

# 更新 workflow（改了 JSON 後執行）
docker compose --profile import up n8n-import
```

n8n UI：http://localhost:5678

## 環境變數（`.env`，不進 repo）

| 變數 | 說明 | 範例 |
|------|------|------|
| `N8N_USER` | n8n 登入帳號 | `admin` |
| `N8N_PASSWORD` | n8n 登入密碼 | 自訂 |
| `N8N_ENCRYPTION_KEY` | 32 字元隨機字串 | `openssl rand -hex 16` |
| `LLM_BASE_URL` | LLM API endpoint | `http://host.docker.internal:1234/v1` |
| `LLM_MODEL` | 模型名稱 | Mac：`mlx-community/Llama-3.2-3B-Instruct-4bit` |
| `AUTHOR_NAME` | 每人填自己名字 | `chuyi` |
| `CLAUDE_API_KEY` | Anthropic API（podcast 用） | `sk-ant-...` |
| `TTS_API_KEY` / `TTS_API_URL` | ElevenLabs 或 OpenAI TTS | 選填 |

## 現有 Workflow

### `knowledge-chat.json`（核心）
觸發：n8n Chat UI
流程：貼入 NotebookLM 內容 → 本地模型對話萃取問題 → 輸入「完成」→ 整理成 markdown
輸出：`vault/notes/YYYY-MM/[title].md` + `vault/raw/YYYY-MM/[title].json`

### `notes-to-podcast.json`（選用）
觸發：`01_Projects/**/inbox/*.md` 有新檔案時自動執行
流程：讀取 markdown → Claude API 轉英文文章 → TTS 轉音頻
輸出：同目錄下 `-article.md` + `-podcast.mp3`

## Vault 資料夾結構
```
vault/
  notes/YYYY-MM/[title].md   ← 根據模板生成，可重新渲染
  raw/YYYY-MM/[title].json   ← 原始對話，永遠保留，不進 git
  templates/                 ← 換模板只改這裡
  progress.md                ← 進度追蹤，未來交 AI agent 管理
```

## 架構原則
- raw data 永遠保留原始 Q&A，不受模板影響
- markdown 這層模板可抽換，換模板後重新渲染所有舊資料
- 每人 n8n 各自獨立，不依賴共用 server
- 身份靠 `AUTHOR_NAME` 環境變數區分
- LLM backend 靠 `LLM_BASE_URL` + `LLM_MODEL` 切換，workflow 不寫死

## 筆記輸出格式
```
---
title: [主題標題]
date: [YYYY-MM-DD]
author: [AUTHOR_NAME]
source: [來源名稱]
tags: [3-5 個關鍵字]
---

## 摘要
[NotebookLM input 核心重點，3-5 句]

## 我的問題
[使用者提出的問題條列]

## 模型補充問題
[模型主動提問的條列，若有]
```

## Claude Code 使用原則
- 一次只做一件事，範圍要清楚
- 給 Claude 錯誤訊息時附上自己的猜測
- 重要決定馬上更新這份 CLAUDE.md

## 目前進度
- [x] 確定系統架構與技術棧
- [x] 確定資料夾結構與模板分離原則
- [x] `notes-to-podcast` workflow 完成
- [x] `knowledge-chat` workflow 完成（LM Studio env var 版）
- [x] vault 結構建立（Obsidian + Git plugin 設定）
- [x] SETUP.md 組員安裝指南完成
- [ ] 三人各自完成本機部署
- [ ] 知識萃取流程端對端測試通過
- [ ] 組員各自部署測試

## 下一階段（待討論）
- 加入 AI agent 自動更新 progress.md
- 更多 HuggingFace 模型測試
- 嵌入式裝置部署規劃（Linux native）
