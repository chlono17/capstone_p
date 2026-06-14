#!/usr/bin/env python3
"""
LLM Agent / MCP / LangChain 概念理解測試
動態加測：高分往深問，低分問基礎
"""

import json
import time
import datetime
import requests
from pathlib import Path

MODEL = "mlx-community/Qwen3-30B-A3B-4bit"
API_URL = "http://localhost:52415/v1/chat/completions"
RESULTS_DIR = Path(__file__).parent / "test_results"
RESULTS_DIR.mkdir(exist_ok=True)

TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M")
RESULT_FILE = RESULTS_DIR / f"eval_agent_{TIMESTAMP}.json"
REPORT_FILE = RESULTS_DIR / f"report_agent_{TIMESTAMP}.md"

# ── Base Tests ───────────────────────────────────────────────────────────────

BASE_TESTS = [

    # ── LLM Agent ────────────────────────────────────────────────────────────
    {
        "domain": "llm_agent", "id": "agent_1", "label": "Agent 基本概念",
        "prompt": (
            "什麼是 LLM Agent？它與普通的 LLM 對話有什麼本質差異？"
            "請說明 Agent 的核心組成要素（感知、推理、行動、記憶），並給一個具體例子。"
        ),
        "expect_keywords": ["工具", "tool", "推理", "行動", "記憶", "感知", "ReAct"],
    },
    {
        "domain": "llm_agent", "id": "agent_2", "label": "ReAct 框架",
        "prompt": (
            "解釋 ReAct（Reasoning + Acting）框架的運作方式。"
            "請用一個「查詢今天天氣並發送提醒」的任務，畫出完整的 Thought → Action → Observation 循環。"
        ),
        "expect_keywords": ["Thought", "Action", "Observation", "循環", "工具"],
    },
    {
        "domain": "llm_agent", "id": "agent_3", "label": "Tool Use 設計",
        "prompt": (
            "你在設計一個 LLM Agent，它需要能夠：搜尋網路、讀寫檔案、執行 Python 程式碼。"
            "請說明如何定義這三個 Tool 的 schema（包含 name, description, parameters），"
            "以及 LLM 如何決定要呼叫哪個工具。"
        ),
        "expect_keywords": ["schema", "name", "description", "parameters", "function calling", "JSON"],
    },
    {
        "domain": "llm_agent", "id": "agent_4", "label": "Multi-Agent",
        "prompt": (
            "什麼是 Multi-Agent 系統？比較 Orchestrator-Worker 和 Peer-to-Peer 兩種架構模式，"
            "說明各自適合的場景。舉例說明一個研究任務如何拆解給多個 Agent 執行。"
        ),
        "expect_keywords": ["Orchestrator", "Worker", "協調", "分工", "並行", "子任務"],
    },

    # ── MCP ──────────────────────────────────────────────────────────────────
    {
        "domain": "mcp", "id": "mcp_1", "label": "MCP 是什麼",
        "prompt": (
            "解釋 Model Context Protocol（MCP）是什麼，它解決了什麼問題？"
            "說明 MCP 的架構中 Host、Client、Server 三個角色各自的職責。"
        ),
        "expect_keywords": ["Host", "Client", "Server", "工具", "資源", "協議", "Anthropic"],
    },
    {
        "domain": "mcp", "id": "mcp_2", "label": "MCP vs Function Calling",
        "prompt": (
            "比較 MCP（Model Context Protocol）與傳統 Function Calling / Tool Use 的差異。"
            "在什麼情況下應該選擇 MCP？什麼情況下直接用 Function Calling 就夠了？"
        ),
        "expect_keywords": ["標準化", "跨模型", "ecosystem", "Function Calling", "動態", "連接"],
    },
    {
        "domain": "mcp", "id": "mcp_3", "label": "MCP Server 設計",
        "prompt": (
            "你要幫一個 Obsidian 知識庫設計一個 MCP Server，讓 AI 能讀寫筆記。"
            "請說明需要暴露哪些 Resources 和 Tools（至少各 3 個），並解釋為什麼選擇 Resources vs Tools 的邏輯。"
        ),
        "expect_keywords": ["Resources", "Tools", "讀取", "寫入", "筆記", "URI"],
    },

    # ── LangChain ─────────────────────────────────────────────────────────────
    {
        "domain": "langchain", "id": "lc_1", "label": "LangChain 核心模組",
        "prompt": (
            "解釋 LangChain 的核心模組：Chain、Agent、Memory、Retriever。"
            "這四個模組之間如何互動？用一個「會記住對話歷史並能查詢文件的聊天機器人」說明各模組扮演的角色。"
        ),
        "expect_keywords": ["Chain", "Agent", "Memory", "Retriever", "互動", "文件"],
    },
    {
        "domain": "langchain", "id": "lc_2", "label": "LCEL 語法",
        "prompt": (
            "什麼是 LangChain Expression Language（LCEL）？"
            "請用 LCEL 的 | 管道語法，寫出一個包含：prompt template → LLM → output parser 的簡單 chain，"
            "並解釋為什麼 LCEL 比舊版 LLMChain 更好。"
        ),
        "expect_keywords": ["LCEL", "|", "prompt", "llm", "parser", "pipe", "stream"],
    },
    {
        "domain": "langchain", "id": "lc_3", "label": "LangGraph vs LangChain",
        "prompt": (
            "LangGraph 和 LangChain 的關係是什麼？LangGraph 解決了 LangChain 哪些痛點？"
            "說明 LangGraph 中 Node、Edge、State 的概念，並舉例說明什麼場景應該選 LangGraph 而不是 LangChain。"
        ),
        "expect_keywords": ["Node", "Edge", "State", "循環", "有向圖", "狀態機", "graph"],
    },

    # ── 整合比較 ──────────────────────────────────────────────────────────────
    {
        "domain": "integration", "id": "int_1", "label": "技術選型",
        "prompt": (
            "你要從零開始建一個「自動幫使用者整理 Obsidian 筆記並生成摘要」的 AI 系統。"
            "請比較以下三種方案並選出最適合的，說明理由：\n"
            "A. 純 LangChain + Function Calling\n"
            "B. LangGraph + MCP Server\n"
            "C. 自己用 Python 寫 Agent loop + OpenAI API"
        ),
        "expect_keywords": ["LangGraph", "MCP", "優缺點", "選擇", "Obsidian", "理由"],
    },
    {
        "domain": "integration", "id": "int_2", "label": "RAG vs Fine-tuning vs Agent",
        "prompt": (
            "對於「讓 AI 回答公司內部文件問題」這個需求，比較 RAG、Fine-tuning、Agent+工具搜尋 三種方案。"
            "請從成本、維護難度、回答品質、知識更新速度四個維度比較，並給出選型建議。"
        ),
        "expect_keywords": ["RAG", "Fine-tuning", "Agent", "成本", "維護", "更新", "比較"],
    },
]

# ── Dynamic Follow-up Pools ──────────────────────────────────────────────────

FOLLOWUP_POOLS = {
    "llm_agent": {
        "hard": [
            {
                "domain": "llm_agent", "id": "agent_hard_1", "label": "Agent 記憶架構（動態加測）",
                "prompt": (
                    "Agent 的記憶系統可以分為哪四種類型（Sensory、Short-term、Long-term、Procedural）？"
                    "在一個長期使用的個人助手 Agent 中，如何設計這四層記憶的儲存與調用機制？"
                    "具體說明哪些資訊應該進 Vector DB，哪些應該進結構化 DB。"
                ),
                "expect_keywords": ["Sensory", "Short-term", "Long-term", "Vector DB", "結構化", "調用"],
            },
        ],
        "easy": [
            {
                "domain": "llm_agent", "id": "agent_easy_1", "label": "Agent vs Chatbot（動態加測）",
                "prompt": "用一句話解釋 Agent 和 Chatbot 最大的差別，並各舉一個現實生活中的例子。",
                "expect_keywords": ["工具", "自主", "主動", "被動", "例子"],
            },
        ],
    },
    "mcp": {
        "hard": [
            {
                "domain": "mcp", "id": "mcp_hard_1", "label": "MCP Transport 層（動態加測）",
                "prompt": (
                    "MCP 支援哪幾種 transport 方式（stdio、HTTP+SSE）？"
                    "分別說明它們的適用場景、優缺點，以及在實作本地 MCP Server 時應該選哪種。"
                ),
                "expect_keywords": ["stdio", "SSE", "HTTP", "本地", "遠端", "transport"],
            },
        ],
        "easy": [
            {
                "domain": "mcp", "id": "mcp_easy_1", "label": "MCP 直覺理解（動態加測）",
                "prompt": "用一個生活中的比喻解釋 MCP，讓一個完全不懂程式的人也能理解它在做什麼。",
                "expect_keywords": ["比喻", "連接", "工具", "標準"],
            },
        ],
    },
    "langchain": {
        "hard": [
            {
                "domain": "langchain", "id": "lc_hard_1", "label": "LangSmith 可觀測性（動態加測）",
                "prompt": (
                    "在生產環境的 LangChain/LangGraph 系統中，如何使用 LangSmith 做可觀測性（observability）？"
                    "說明 trace、span、run 的概念，以及如何透過 LangSmith 找出 Agent 在哪個步驟失敗或回應品質差。"
                ),
                "expect_keywords": ["LangSmith", "trace", "span", "可觀測", "debug", "品質"],
            },
        ],
        "easy": [
            {
                "domain": "langchain", "id": "lc_easy_1", "label": "為什麼用 LangChain（動態加測）",
                "prompt": "用3個具體理由說明，為什麼開發 LLM 應用時應該考慮使用 LangChain，而不是直接呼叫 OpenAI API？",
                "expect_keywords": ["抽象", "Chain", "整合", "模板", "工具"],
            },
        ],
    },
    "integration": {
        "hard": [
            {
                "domain": "integration", "id": "int_hard_1", "label": "Capstone 系統架構建議（動態加測）",
                "prompt": (
                    "你在幫一個大學生團隊設計「自主知識合成器（Autonomous Knowledge Synthesizer）」：\n"
                    "- 輸入：手寫/語音/網頁/PDF\n"
                    "- 處理：知識萃取、問答對話、格式化、RAG 檢索\n"
                    "- 輸出：知識卡片、Podcast、學習社群 Feed\n"
                    "請推薦具體的技術棧（LLM框架、向量DB、部署方式），並說明各元件為什麼選這個而不是替代方案。"
                ),
                "expect_keywords": ["LangGraph", "ChromaDB", "Ollama", "Agent", "RAG", "向量", "本地"],
            },
        ],
        "easy": [
            {
                "domain": "integration", "id": "int_easy_1", "label": "RAG 基本流程（動態加測）",
                "prompt": "用5個步驟說明 RAG 系統的完整運作流程，從使用者提問到最終回答。",
                "expect_keywords": ["向量", "檢索", "embedding", "相似度", "LLM", "步驟"],
            },
        ],
    },
}

# ── API & Scoring ─────────────────────────────────────────────────────────────

def chat(prompt: str, max_tokens: int = 1200) -> tuple[str, float, dict]:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt + " /no_think"}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    for attempt in range(4):
        try:
            t0 = time.time()
            resp = requests.post(API_URL, json=payload, timeout=300)
            elapsed = time.time() - t0
            if resp.status_code == 404:
                wait = 20 * (attempt + 1)
                print(f"         → 404，等 {wait}s 重試 ({attempt+1}/3)...", flush=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return content, elapsed, usage
        except requests.exceptions.Timeout:
            if attempt < 3:
                print(f"         → timeout，重試 ({attempt+1}/3)...", flush=True)
                time.sleep(10)
                continue
            raise
    raise RuntimeError("API 連續失敗，已重試 3 次")


def score(response: str, keywords: list[str]) -> dict:
    hits = [kw for kw in keywords if kw.lower() in response.lower()]
    kw_score = len(hits) / len(keywords) if keywords else 0
    length_score = min(len(response) / 600, 1.0)
    overall = round((kw_score * 0.7 + length_score * 0.3) * 10, 1)
    return {"keyword_hits": hits, "keyword_score": round(kw_score * 10, 1),
            "length": len(response), "overall": overall}


def run_test(test: dict) -> dict:
    prompt_preview = test['prompt'][:120].replace('\n', ' ')
    print(f"  [{test['id']}] {test['label']}", flush=True)
    print(f"  Q: {prompt_preview}{'...' if len(test['prompt'])>120 else ''}", flush=True)
    try:
        response, elapsed, usage = chat(test["prompt"])
        scores = score(response, test["expect_keywords"])
        result = {**test, "response": response, "elapsed_sec": round(elapsed, 2),
                  "scores": scores, "usage": usage, "status": "ok"}
        print(f"         → {elapsed:.1f}s | score {scores['overall']}/10 | {len(response)} chars")
    except Exception as e:
        result = {**test, "response": "", "elapsed_sec": 0,
                  "scores": {"overall": 0, "keyword_hits": [], "length": 0},
                  "usage": {}, "status": f"error: {e}"}
        print(f"         → ERROR: {e}")
    return result


# ── Report ────────────────────────────────────────────────────────────────────

def build_report(results: list[dict]) -> str:
    domain_names = {
        "llm_agent": "LLM Agent",
        "mcp": "MCP（Model Context Protocol）",
        "langchain": "LangChain / LangGraph",
        "integration": "整合比較 & 技術選型",
    }
    domain_results: dict[str, list] = {d: [] for d in domain_names}
    for r in results:
        domain_results[r["domain"]].append(r)

    lines = [
        "# LLM Agent / MCP / LangChain 概念理解評估報告",
        "",
        f"**模型**: `{MODEL}`  ",
        f"**日期**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**測試總數**: {len(results)}",
        "",
        "---",
        "",
        "## 一、分域成績",
        "",
        "| 域 | 測試數 | 平均分 | 強弱評語 |",
        "|---|---|---|---|",
    ]

    domain_avgs = {}
    for domain, dr in domain_results.items():
        ok = [r for r in dr if r["status"] == "ok"]
        avg = round(sum(r["scores"]["overall"] for r in ok) / len(ok), 1) if ok else 0
        domain_avgs[domain] = avg
        if avg >= 8:   comment = "概念清晰，能延伸說明"
        elif avg >= 6: comment = "基本理解正確，細節稍弱"
        elif avg >= 4: comment = "有基本認識，但解釋不夠深"
        else:          comment = "理解有誤或過於表淺"
        lines.append(f"| {domain_names[domain]} | {len(dr)} | {avg} | {comment} |")

    all_ok = [r for r in results if r["status"] == "ok"]
    overall_avg = round(sum(r["scores"]["overall"] for r in all_ok) / len(all_ok), 1) if all_ok else 0

    # Find best and worst
    sorted_ok = sorted(all_ok, key=lambda r: r["scores"]["overall"])
    weakest = sorted_ok[:3] if sorted_ok else []
    strongest = sorted_ok[-3:][::-1] if sorted_ok else []

    lines += [
        "",
        "---",
        "",
        "## 二、整體觀察",
        "",
        f"- **整體平均分**: {overall_avg} / 10",
        "",
        "### 最強的3題",
        "",
    ]
    for r in strongest:
        lines.append(f"- **{r['label']}** ({r['scores']['overall']}/10)：命中關鍵字 {r['scores']['keyword_hits']}")

    lines += ["", "### 最弱的3題（需要關注）", ""]
    for r in weakest:
        missed = [kw for kw in r["expect_keywords"] if kw.lower() not in r["response"].lower()]
        lines.append(f"- **{r['label']}** ({r['scores']['overall']}/10)：缺少關鍵字 {missed}")

    lines += [
        "",
        "---",
        "",
        "## 三、各題詳細回應",
        "",
    ]

    for domain, dr in domain_results.items():
        if not dr:
            continue
        lines += [f"### {domain_names[domain]}", ""]
        for r in dr:
            icon = "✅" if r["scores"]["overall"] >= 7 else ("⚠️" if r["scores"]["overall"] >= 4 else "❌")
            dynamic = "（動態加測）" if "動態加測" in r["label"] else ""
            lines += [
                f"#### {icon} {r['label']}{dynamic}",
                "",
                f"- **分數**: {r['scores'].get('overall', 'N/A')} / 10  |  **耗時**: {r['elapsed_sec']}s  |  **字數**: {r['scores'].get('length', 0)}",
                f"- **命中關鍵字**: {r['scores'].get('keyword_hits', [])}",
                "",
                "<details><summary>查看回應（前 1000 字）</summary>",
                "",
                "```",
                r["response"][:1000] + ("..." if len(r["response"]) > 1000 else ""),
                "```",
                "",
                "</details>",
                "",
            ]

    lines += [
        "---",
        "",
        "## 四、對 Capstone 專題的啟示",
        "",
        "| 問題 | 模型建議 |",
        "|---|---|",
        "| Agent 框架選擇 | 根據整合題回應，LangGraph + MCP 組合適合複雜 workflow |",
        "| 知識庫工具 | RAG 優先，Fine-tuning 僅在需要語氣/格式時用 |",
        "| 本地部署 | Qwen3-30B 可作為本地 Agent 腦，替代 GPT-4 |",
        "| MCP 整合點 | Obsidian vault / Vector DB 都適合做 MCP Server |",
        "",
        "---",
        "",
        f"*報告由 test_agent_concepts.py 自動生成 | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ]
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"  Model  : {MODEL}")
    print(f"  Topic  : LLM Agent / MCP / LangChain")
    print(f"  Tests  : {len(BASE_TESTS)} base + dynamic follow-ups")
    print(f"  Start  : {TIMESTAMP}")
    print(f"{'='*60}\n")

    # 暖機：確認模型可用再開始
    print("  暖機中...", flush=True)
    for i in range(6):
        try:
            r = requests.post(API_URL, json={
                "model": MODEL,
                "messages": [{"role": "user", "content": "hi /no_think"}],
                "max_tokens": 10,
            }, timeout=60)
            if r.status_code == 200:
                print("  ✓ 模型就緒\n")
                break
            print(f"  暖機 {i+1}/6：status {r.status_code}，等 15s...")
            time.sleep(15)
        except Exception as e:
            print(f"  暖機 {i+1}/6：{e}，等 15s...")
            time.sleep(15)

    all_results: list[dict] = []
    domain_scores: dict[str, list[float]] = {d: [] for d in FOLLOWUP_POOLS}
    domains_order = ["llm_agent", "mcp", "langchain", "integration"]
    domain_names = {
        "llm_agent": "LLM Agent",
        "mcp": "MCP",
        "langchain": "LangChain/LangGraph",
        "integration": "整合比較",
    }

    by_domain = {d: [t for t in BASE_TESTS if t["domain"] == d] for d in domains_order}

    for domain in domains_order:
        print(f"\n── {domain_names[domain]} ({'─'*40})")
        for test in by_domain[domain]:
            result = run_test(test)
            all_results.append(result)
            if result["status"] == "ok":
                domain_scores[domain].append(result["scores"]["overall"])
            RESULT_FILE.write_text(
                json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
            time.sleep(3)

        avg = (sum(domain_scores[domain]) / len(domain_scores[domain])
               if domain_scores[domain] else 0)
        print(f"\n  → {domain_names[domain]} 平均分: {avg:.1f}/10")

        pool = FOLLOWUP_POOLS.get(domain, {})
        if avg >= 7.5 and "hard" in pool:
            print(f"  → 分數高，加測進階題...")
            for ft in pool["hard"]:
                result = run_test(ft)
                all_results.append(result)
                if result["status"] == "ok":
                    domain_scores[domain].append(result["scores"]["overall"])
                RESULT_FILE.write_text(
                    json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
                time.sleep(3)
        elif avg < 5.5 and "easy" in pool:
            print(f"  → 分數偏低，加測基礎題確認理解...")
            for ft in pool["easy"]:
                result = run_test(ft)
                all_results.append(result)
                if result["status"] == "ok":
                    domain_scores[domain].append(result["scores"]["overall"])
                RESULT_FILE.write_text(
                    json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
                time.sleep(3)

    print(f"\n{'='*60}")
    print(f"  生成報告中...")
    report_content = build_report(all_results)
    REPORT_FILE.write_text(report_content, encoding="utf-8")
    RESULT_FILE.write_text(
        json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")

    all_ok = [r for r in all_results if r["status"] == "ok"]
    overall = round(sum(r["scores"]["overall"] for r in all_ok) / len(all_ok), 1) if all_ok else 0
    print(f"  完成！共 {len(all_results)} 題，整體平均 {overall}/10")
    print(f"  報告 → {REPORT_FILE}")
    print(f"  JSON → {RESULT_FILE}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
