# 共用基礎層

四個功能模組（智慧洞察、人員調度、總結追蹤、知識沉澱）共用的 Agent 框架、檢索與工具整合基礎設施。

## 模組

| 模組 | 說明 |
|------|------|
| `agent/` | LangGraph Agent 執行框架 |
| `rag/` | RAG 檢索：向量索引與查詢，供各功能模組使用 |
| `mcp/` | MCP 工具整合：Agent 呼叫外部工具（GitHub、Calendar 等）的統一介面 |
| `llm/` | 本地部署推論後端介接 |

## 技術選型（參考）

- Agent 框架：LangGraph
- 推論後端：本地優先，外部 API 用量另外標注
- MCP：用於 Agent 工具呼叫（GitHub、Calendar 等）
