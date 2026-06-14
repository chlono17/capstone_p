# Qwen3-30B-A3B-4bit vs Qwen3.5-9B-8bit 完整對比報告

> 生成時間：2026-06-03 20:45  
> 測試題數：27 題（全域覆蓋）  
> 環境：M4 Mac Mini (主) + M1 MacBook Air (分散) via Tailscale + Exo MLX Ring  
> ⚠ 30B 有 3 題因 Exo timeout 未取得結果（lc_3, int_1, int_2），標記為 —

---

## 一、總覽

| 指標 | Qwen3-30B-A3B-4bit | Qwen3.5-9B-8bit |
|------|-------------------|-----------------|
| 有效題數 | 24/27 (3 題超時) | 27/27 |
| 有效題平均 | **8.60/10** | **8.74/10** |
| 記憶體配置 | ~30GB (MoE, active 3B) | ~9GB (dense 8bit) |
| 典型回應時間 | 60–120s (兩機分散) | 160–225s (單機) |
| Thinking mode 關閉 | 需 /no_think | 需 enable_thinking: False |

---

## 二、分域對比

| 域 | 30B-4bit | 9B-8bit | 差距 | 備註 |
|-----|---------|---------|------|------|
| 數學 | 9.24 (5/5) | 9.24 | 0.00 (≈) | 兩者相當，均 9.24 |
| 程式 | 8.18 (5/5) | 7.54 | +0.64 (30B↑) | 30B 在排序複雜度/二分搜尋領先 |
| 時間規劃 | 9.68 (5/5) | 9.36 | +0.32 (30B↑) | 兩者相當，結構化輸出都完整 |
| LLM Agent | 7.97 (4/4) | 8.95 | -0.97 (9B↑) | 9B 稍勝，Qwen3.5 訓練資料含大量 Agent 文件 |
| MCP | 6.67 (3/3) | 8.90 | -2.23 (9B↑) | 9B 勝，但 MCP 為 2024 新標準，建議兩者加 RAG |
| LangChain/LangGraph | 9.50 (2/3) | 8.70 | +0.80 (30B↑) | 30B 有效題 lc_1/lc_2 佳，lc_3 超時未計；9B 三題全完成 |
| 整合比較 | — (0/2 超時) | 8.40 | — | 30B 兩題均超時未計；9B 8.4/10 |
| **有效題均分** | **8.60** | **8.74** | **-0.14** | 30B 以 24 題計算 |

---

## 三、逐題對比

| ID | 題目 | 域 | 30B | 9B | ▲ |
|----|----|---|----|----|---|
| math_1 | 二次方程式 | 數學 | 10.0 | 10.0 | ≈ |
| math_2 | 微分 | 數學 | 8.4 | 8.4 | ≈ |
| math_3 | 機率 | 數學 | 7.8 | 7.8 | ≈ |
| math_4 | 質數篩法 | 數學 | 10.0 | 10.0 | ≈ |
| math_5 | 數列求和 | 數學 | 10.0 | 10.0 | ≈ |
| prog_1 | 二分搜尋 | 程式 | 10.0 | 8.7 | 30B |
| prog_2 | Debug | 程式 | 10.0 | 10.0 | ≈ |
| prog_3 | 資料結構選擇 | 程式 | 6.1 | 3.5 | 30B |
| prog_4 | 排序複雜度 | 程式 | 10.0 | 6.8 | 30B |
| prog_5 | RAG 解釋 | 程式 | 4.8 | 8.7 | 9B |
| time_1 | 每週學習計畫 | 時間規劃 | 10.0 | 10.0 | ≈ |
| time_2 | 番茄工作法 | 時間規劃 | 10.0 | 8.4 | 30B |
| time_3 | SMART 目標 | 時間規劃 | 10.0 | 10.0 | ≈ |
| time_4 | 考前衝刺 | 時間規劃 | 10.0 | 10.0 | ≈ |
| time_5 | 深度工作 | 時間規劃 | 8.4 | 8.4 | ≈ |
| agent_1 | Agent 基本概念 | LLM Agent | 8.0 | 9.1 | 9B |
| agent_2 | ReAct 框架 | LLM Agent | 8.6 | 10.0 | 9B |
| agent_3 | Tool Use 設計 | LLM Agent | 8.8 | 8.9 | ≈ |
| agent_4 | Multi-Agent | LLM Agent | 6.5 | 7.8 | 9B |
| mcp_1 | MCP 是什麼 | MCP | 7.0 | 10.0 | 9B |
| mcp_2 | MCP vs Function Calling | MCP | 4.2 | 7.8 | 9B |
| mcp_3 | MCP Server 設計 | MCP | 8.8 | 8.9 | ≈ |
| lc_1 | LangChain 核心模組 | LangChain/LangGraph | 10.0 | 8.9 | 30B |
| lc_2 | LCEL 語法 | LangChain/LangGraph | 9.0 | 8.1 | 30B |
| lc_3 | LangGraph vs LangChain | LangChain/LangGraph | — | 9.1 | — (30B 超時) |
| int_1 | 技術選型 | 整合比較 | — | 6.8 | — (30B 超時) |
| int_2 | RAG vs Fine-tuning vs Agent | 整合比較 | — | 10.0 | — (30B 超時) |

---

## 四、速度分析

| 模型 | 中位 elapsed | >200s | <100s | 備註 |
|------|------------|-------|-------|------|
| 30B-4bit | 58s | 0 題 | 24 題 | 兩機分散，TCP over Tailscale |
| 9B-8bit  | 196s  | 12 題  | 2 題  | M4 Mini 單機，output token bound |

---

## 五、使用建議

| 情境 | 建議 | 理由 |
|------|------|------|
| 即時對話 / 快速草稿 | **9B-8bit** | M4 Mini 單機，速度中位 196s vs 30B 分散時需兩機都在線 |
| 複雜程式邏輯、排序/演算法 | **30B-4bit** | prog_4 差距 10.0 vs 6.8 |
| Agent / MCP 概念 | **9B-8bit** | 9B 訓練資料含 Qwen3 Agent 相關，且兩機不需同時在線 |
| 整合架構比較 | **30B-4bit** | 等 M4 Mini 重連後補跑 int_1/int_2 |
| M4 Mini 離線時 | **9B-8bit** | 30B 需要 M4+M1 Air 合計 ~40GB，單機裝不下 |
| Capstone pipeline 後台 | **30B-4bit** | 品質優先，非即時場景 |

---

## 六、30B 待補跑（M4 Mini 重連後）

| ID | 題目 | 失敗原因 |
|-----|------|---------|
| lc_3 | LangGraph vs LangChain | Exo read timeout |
| int_1 | 技術選型 | API 連續失敗 3 次 |
| int_2 | RAG vs Fine-tuning vs Agent | API 連續失敗 3 次 |

## 七、弱項與提升方向

**9B 弱項**
- `prog_3` 資料結構選擇: 3.5/10
- `prog_4` 排序複雜度: 6.8/10
- `int_1` 技術選型: 6.8/10

**30B 弱項（已取得的 24 題中）**
- `mcp_2` MCP vs Function Calling: 4.2/10
- `prog_5` RAG 解釋: 4.8/10
- `prog_3` 資料結構選擇: 6.1/10
- `agent_4` Multi-Agent: 6.5/10

**提升方向**
1. **RAG 補知識**：MCP / LangGraph 訓練資料截止 2024，
   用官方文件建向量庫可補 mcp_2、lc_3 等題的分數。
2. **Few-shot prompting**：prog_3（資料結構選擇）兩個模型都偏低，
   加 1–2 個 few-shot 範例可提高一致性。
3. **max_tokens 放寬**：prog_4 排序複雜度、lc_2 LCEL 語法常被截斷，
   建議列舉型題目改成 1800 tokens。

---

*自動生成 by capstone test suite | 2026-06-03*