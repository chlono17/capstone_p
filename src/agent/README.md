# AGENT 層

系統的智慧處理核心，負責知識萃取、格式化、輔助寫作、RAG 檢索與 Podcast 生成。

## 功能模組（待實作）

| 模組 | 說明 | Linear |
|------|------|--------|
| `extractor/` | 知識萃取：Q&A 對話形式提煉重點 | CAP-10 |
| `formatter/` | 格式化：手寫 / 語音 → 結構化 Markdown | - |
| `writer_assist/` | 輔助寫作：架構提示，協助使用者完成輸出 | - |
| `rag/` | RAG 檢索：從 Vector DB 找出相關知識片段 | CAP-7, CAP-8 |
| `podcast/` | Podcast 生成：TTS 將知識卡片轉為音訊 | - |
| `llm/` | 本地 LLM 介接（Ollama） | CAP-6, CAP-11, CAP-12 |

## 技術選型（參考）

- 推論後端：Ollama
- MCP 整合：用於 Agent 工具呼叫
- TTS：待評估（Coqui / edge-tts）
