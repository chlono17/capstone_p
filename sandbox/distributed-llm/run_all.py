#!/usr/bin/env python3
"""
全自動跑兩個模型的完整測試並生成對比報告
模型：Qwen3-30B-A3B-4bit vs Qwen3.5-9B-8bit
測試：數學/程式/時間規劃 + Agent/MCP/LangChain
"""

import json
import time
import datetime
import requests
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "test_results"
RESULTS_DIR.mkdir(exist_ok=True)

MODELS = {
    "9B":  "mlx-community/Qwen3.5-9B-8bit",
}
API_URL = "http://localhost:52415/v1/chat/completions"
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M")

# ── 所有測試題 ───────────────────────────────────────────────────────────────

GENERAL_TESTS = [
    # 數學
    {"domain":"math","id":"math_1","label":"二次方程式",
     "prompt":"解方程式 x² - 5x + 6 = 0，列出完整步驟。",
     "expect_keywords":["x = 2","x = 3","因式"]},
    {"domain":"math","id":"math_2","label":"微分",
     "prompt":"求 f(x) = x³ + 2x² - 5x + 1 的導函數 f'(x)，並求 x=1 時的切線斜率。",
     "expect_keywords":["3x²","4x","-5","2"]},
    {"domain":"math","id":"math_3","label":"機率",
     "prompt":"同時擲兩顆標準骰子，點數和恰好為 7 的機率是多少？列出所有組合。",
     "expect_keywords":["1/6","6","36"]},
    {"domain":"math","id":"math_4","label":"質數篩法",
     "prompt":"用篩法找出 1 到 30 以內的所有質數，列出清單並說明步驟。",
     "expect_keywords":["2","3","5","7","11","13","23","29"]},
    {"domain":"math","id":"math_5","label":"數列求和",
     "prompt":"等差數列首項為 3，公差為 4，求前 20 項的總和。用公式求解並驗證。",
     "expect_keywords":["820","公式","79"]},
    # 程式
    {"domain":"programming","id":"prog_1","label":"二分搜尋",
     "prompt":"用 Python 實作二分搜尋法，回傳 index 或 -1，附時間複雜度分析。",
     "expect_keywords":["def","mid","left","right","O(log n)"]},
    {"domain":"programming","id":"prog_2","label":"Debug",
     "prompt":"以下 Python 程式有 bug，請找出並修正：\ndef fibonacci(n):\n    if n==0: return 0\n    elif n==1: return 1\n    else: return fibonacci(n-1)+fibonacci(n-3)\nprint(fibonacci(10))  # 期望輸出 55",
     "expect_keywords":["n-2","fibonacci(n-2)","55"]},
    {"domain":"programming","id":"prog_3","label":"資料結構選擇",
     "prompt":"設計瀏覽器「上一頁/下一頁」功能，應選用哪種資料結構？為什麼？給出 Python 實作草稿。",
     "expect_keywords":["stack","Stack","堆疊","push","pop"]},
    {"domain":"programming","id":"prog_4","label":"排序複雜度",
     "prompt":"比較 Bubble Sort、Merge Sort、Quick Sort 的最佳/平均/最差時間複雜度，說明各自使用場景。",
     "expect_keywords":["O(n²)","O(n log n)","Merge Sort","Quick Sort"]},
    {"domain":"programming","id":"prog_5","label":"RAG 解釋",
     "prompt":"解釋 RAG 的工作原理，說明它如何解決 LLM 知識截止問題，給出一個具體應用場景。",
     "expect_keywords":["檢索","向量","LLM","context","知識庫"]},
    # 時間規劃
    {"domain":"time_planning","id":"time_1","label":"每週學習計畫",
     "prompt":"我是大學三年級資工系學生，要準備3門期末考（作業系統、演算法、資料庫）還要維持每週3次健身。規劃7天作息表，具體到每天時段。",
     "expect_keywords":["週一","週二","小時","休息","複習"]},
    {"domain":"time_planning","id":"time_2","label":"番茄工作法",
     "prompt":"我想用番茄工作法提高學習效率，但常常分心。給我5個實際可執行的技巧，說明如何融入大學生日常。",
     "expect_keywords":["25分鐘","番茄","休息","專注"]},
    {"domain":"time_planning","id":"time_3","label":"SMART 目標",
     "prompt":"我想在3個月內完成一個 LLM side project 並放上 GitHub。用 SMART 原則拆解成里程碑，附每週具體任務。",
     "expect_keywords":["SMART","里程碑","週","具體"]},
    {"domain":"time_planning","id":"time_4","label":"考前衝刺",
     "prompt":"期末考剩兩週，演算法還差30%、機器學習差50%。設計兩週衝刺計畫，列清每天可讀書時數。",
     "expect_keywords":["週","小時","演算法","機器學習","重點"]},
    {"domain":"time_planning","id":"time_5","label":"深度工作",
     "prompt":"Cal Newport 的「深度工作」理論如何應用在學生身上？給3個立刻能實行的方法，說明如何抵抗社群媒體干擾。",
     "expect_keywords":["深度","專注","社群","排程"]},
]

AGENT_TESTS = [
    # LLM Agent
    {"domain":"llm_agent","id":"agent_1","label":"Agent 基本概念",
     "prompt":"什麼是 LLM Agent？它與普通 LLM 對話的本質差異？說明 Agent 核心組成（感知、推理、行動、記憶），給具體例子。",
     "expect_keywords":["工具","tool","推理","行動","記憶","感知","ReAct"]},
    {"domain":"llm_agent","id":"agent_2","label":"ReAct 框架",
     "prompt":"解釋 ReAct 框架的運作方式。用「查詢今天天氣並發送提醒」的任務，畫出完整的 Thought → Action → Observation 循環。",
     "expect_keywords":["Thought","Action","Observation","循環","工具"]},
    {"domain":"llm_agent","id":"agent_3","label":"Tool Use 設計",
     "prompt":"設計一個能搜尋網路、讀寫檔案、執行 Python 的 LLM Agent。說明如何定義三個 Tool 的 schema（name, description, parameters），以及 LLM 如何決定呼叫哪個工具。",
     "expect_keywords":["schema","name","description","parameters","function calling","JSON"]},
    {"domain":"llm_agent","id":"agent_4","label":"Multi-Agent",
     "prompt":"什麼是 Multi-Agent 系統？比較 Orchestrator-Worker 和 Peer-to-Peer 兩種架構，說明各自適合場景。舉例說明研究任務如何拆解給多個 Agent 執行。",
     "expect_keywords":["Orchestrator","Worker","協調","分工","並行","子任務"]},
    # MCP
    {"domain":"mcp","id":"mcp_1","label":"MCP 是什麼",
     "prompt":"解釋 Model Context Protocol（MCP）是什麼，它解決了什麼問題？說明架構中 Host、Client、Server 三個角色各自的職責。",
     "expect_keywords":["Host","Client","Server","工具","資源","協議","Anthropic"]},
    {"domain":"mcp","id":"mcp_2","label":"MCP vs Function Calling",
     "prompt":"比較 MCP 與傳統 Function Calling / Tool Use 的差異。什麼情況應選 MCP？什麼情況直接用 Function Calling 就夠了？",
     "expect_keywords":["標準化","跨模型","ecosystem","Function Calling","動態","連接"]},
    {"domain":"mcp","id":"mcp_3","label":"MCP Server 設計",
     "prompt":"幫 Obsidian 知識庫設計一個 MCP Server，讓 AI 能讀寫筆記。說明需要暴露哪些 Resources 和 Tools（各 3 個），並解釋 Resources vs Tools 的選擇邏輯。",
     "expect_keywords":["Resources","Tools","讀取","寫入","筆記","URI"]},
    # LangChain
    {"domain":"langchain","id":"lc_1","label":"LangChain 核心模組",
     "prompt":"解釋 LangChain 的核心模組：Chain、Agent、Memory、Retriever。用「會記住對話歷史並能查詢文件的聊天機器人」說明各模組角色。",
     "expect_keywords":["Chain","Agent","Memory","Retriever","互動","文件"]},
    {"domain":"langchain","id":"lc_2","label":"LCEL 語法",
     "prompt":"什麼是 LangChain Expression Language（LCEL）？用 | 管道語法寫出 prompt template → LLM → output parser 的 chain，並解釋為什麼 LCEL 比舊版 LLMChain 更好。",
     "expect_keywords":["LCEL","|","prompt","llm","parser","pipe","stream"]},
    {"domain":"langchain","id":"lc_3","label":"LangGraph vs LangChain",
     "prompt":"LangGraph 和 LangChain 的關係是什麼？LangGraph 解決了哪些痛點？說明 Node、Edge、State 概念，舉例什麼場景應選 LangGraph 而不是 LangChain。",
     "expect_keywords":["Node","Edge","State","循環","有向圖","狀態機","graph"]},
    # 整合比較
    {"domain":"integration","id":"int_1","label":"技術選型",
     "prompt":"從零建「自動整理 Obsidian 筆記並生成摘要」的 AI 系統，比較三個方案並選出最適合的：A. 純 LangChain + Function Calling  B. LangGraph + MCP Server  C. 自己用 Python 寫 Agent loop + OpenAI API",
     "expect_keywords":["LangGraph","MCP","優缺點","選擇","Obsidian","理由"]},
    {"domain":"integration","id":"int_2","label":"RAG vs Fine-tuning vs Agent",
     "prompt":"對於「讓 AI 回答公司內部文件問題」，比較 RAG、Fine-tuning、Agent+工具搜尋 三種方案。從成本、維護難度、回答品質、知識更新速度四個維度比較，給出選型建議。",
     "expect_keywords":["RAG","Fine-tuning","Agent","成本","維護","更新","比較"]},
]

ALL_TESTS = GENERAL_TESTS + AGENT_TESTS

DOMAIN_NAMES = {
    "math":"數學", "programming":"程式", "time_planning":"個人時間規劃",
    "llm_agent":"LLM Agent", "mcp":"MCP", "langchain":"LangChain/LangGraph",
    "integration":"整合比較",
}

# ── API ───────────────────────────────────────────────────────────────────────

def chat(model: str, prompt: str, max_tokens: int = 1200) -> tuple[str, float]:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt + " /no_think"}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "enable_thinking": False,   # 直接關掉 thinking mode（/no_think 對 9B 無效）
    }
    for attempt in range(4):
        try:
            t0 = time.time()
            r = requests.post(API_URL, json=payload, timeout=300)
            elapsed = time.time() - t0
            if r.status_code == 404:
                wait = 20 * (attempt + 1)
                print(f"         404，等 {wait}s 重試 ({attempt+1}/3)...", flush=True)
                time.sleep(wait)
                continue
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            return content, elapsed
        except requests.exceptions.Timeout:
            if attempt < 3:
                print(f"         timeout，重試 ({attempt+1}/3)...", flush=True)
                time.sleep(10)
                continue
            raise
    raise RuntimeError("API 連續失敗")


def score(response: str, keywords: list) -> dict:
    hits = [kw for kw in keywords if kw.lower() in response.lower()]
    kw = len(hits) / len(keywords) if keywords else 0
    ln = min(len(response) / 500, 1.0)
    return {"hits": hits, "overall": round((kw * 0.65 + ln * 0.35) * 10, 1), "length": len(response)}


def warmup(model: str) -> bool:
    print(f"  暖機 {model.split('/')[-1]}...", flush=True)
    for i in range(8):
        try:
            r = requests.post(API_URL, json={
                "model": model,
                "messages": [{"role":"user","content":"hi /no_think"}],
                "max_tokens": 10,
            }, timeout=60)
            if r.status_code == 200:
                print(f"  ✓ 就緒\n", flush=True)
                return True
        except Exception:
            pass
        print(f"  暖機 {i+1}/8，等 15s...", flush=True)
        time.sleep(15)
    return False


# ── Run one model ─────────────────────────────────────────────────────────────

def run_model(model_key: str, model_id: str) -> dict:
    result_file = RESULTS_DIR / f"eval_{model_key}_{TIMESTAMP}.json"
    results = []

    if not warmup(model_id):
        print(f"  ✗ 無法連線 {model_id}，跳過")
        return {}

    for test in ALL_TESTS:
        q_preview = test['prompt'][:100].replace('\n',' ')
        print(f"  [{test['id']}] {test['label']}", flush=True)
        print(f"  Q: {q_preview}{'...' if len(test['prompt'])>100 else ''}", flush=True)
        try:
            response, elapsed = chat(model_id, test["prompt"])
            s = score(response, test["expect_keywords"])
            r = {**test, "response": response, "elapsed_sec": round(elapsed,2),
                 "scores": s, "status": "ok"}
            print(f"         → {elapsed:.1f}s | score {s['overall']}/10 | {s['length']} chars")
        except Exception as e:
            r = {**test, "response": "", "elapsed_sec": 0,
                 "scores": {"overall": 0, "hits": [], "length": 0}, "status": f"error: {e}"}
            print(f"         → ERROR: {e}")

        results.append(r)
        result_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(3)

    return {r["id"]: r for r in results}


# ── Compare Report ────────────────────────────────────────────────────────────

def build_compare_report(results_30b: dict, results_9b: dict) -> str:
    lines = [
        "# 模型對比報告：Qwen3-30B-A3B-4bit vs Qwen3.5-9B-8bit",
        "",
        f"**日期**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**測試總數**: {len(ALL_TESTS)} 題",
        "",
        "---",
        "",
        "## 一、分域對比",
        "",
        "| 域 | 30B-4bit | 9B-8bit | 差距 |",
        "|---|---|---|---|",
    ]

    domain_order = ["math","programming","time_planning","llm_agent","mcp","langchain","integration"]
    domain_avgs = {"30B": {}, "9B": {}}

    for domain in domain_order:
        tests = [t for t in ALL_TESTS if t["domain"] == domain]
        for key, results in [("30B", results_30b), ("9B", results_9b)]:
            scores = [results[t["id"]]["scores"]["overall"]
                      for t in tests if t["id"] in results and results[t["id"]]["status"]=="ok"]
            domain_avgs[key][domain] = round(sum(scores)/len(scores), 1) if scores else None

        a = domain_avgs["30B"][domain]
        b = domain_avgs["9B"][domain]
        a_str = f"{a}" if a is not None else "—"
        b_str = f"{b}" if b is not None else "—"
        if a is not None and b is not None:
            diff = round(a - b, 1)
            diff_str = f"+{diff} (30B 較好)" if diff > 0.5 else (f"{diff} (9B 較好)" if diff < -0.5 else "相近")
        else:
            diff_str = "—"
        lines.append(f"| {DOMAIN_NAMES[domain]} | {a_str} | {b_str} | {diff_str} |")

    # overall
    def overall(results):
        s = [v["scores"]["overall"] for v in results.values() if v["status"]=="ok"]
        return round(sum(s)/len(s), 1) if s else 0

    o30 = overall(results_30b)
    o9  = overall(results_9b)
    lines += [
        "",
        f"**整體平均** | **{o30}** | **{o9}** | **{round(o30-o9,1):+}**",
        "",
        "---",
        "",
        "## 二、逐題對比",
        "",
        "| 題目 | 域 | 30B | 9B | 建議用哪個 |",
        "|---|---|---|---|---|",
    ]

    for test in ALL_TESTS:
        tid = test["id"]
        s30 = results_30b.get(tid, {}).get("scores", {}).get("overall", "—")
        s9  = results_9b.get(tid, {}).get("scores", {}).get("overall", "—")
        if isinstance(s30, float) and isinstance(s9, float):
            if s30 > s9 + 1:    rec = "30B"
            elif s9 > s30 + 1:  rec = "9B"
            else:                rec = "相近，用 9B（快）"
        else:
            rec = "—"
        lines.append(f"| {test['label']} | {DOMAIN_NAMES[test['domain']]} | {s30} | {s9} | {rec} |")

    lines += [
        "",
        "---",
        "",
        "## 三、使用建議",
        "",
        "| 情境 | 建議模型 | 理由 |",
        "|---|---|---|",
        "| 快問快答 / 即時對話 | 9B-8bit | TTFT 快 3-4 倍 |",
        "| 複雜推理 / 架構分析 | 30B-4bit | 參數量和知識廣度勝出 |",
        "| MCP / 新技術概念 | 30B + RAG | 補充 2024 後知識 |",
        "| Capstone pipeline 後台 | 30B-4bit | 品質優先，不趕時間 |",
        "| M4 Mini 離線時 | 9B-8bit | 30B 單機塞滿記憶體不穩 |",
        "",
        "---",
        "",
        f"*由 run_all.py 自動生成 | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ]
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"  全模型測試開始 | {TIMESTAMP}")
    print(f"  題數：{len(ALL_TESTS)} 題 × 2 個模型 = {len(ALL_TESTS)*2} 次推理")
    print(f"{'='*60}\n")

    all_results = {}
    for key, model_id in MODELS.items():
        print(f"\n{'─'*60}")
        print(f"  模型：{key} → {model_id}")
        print(f"{'─'*60}\n")
        all_results[key] = run_model(key, model_id)

    print(f"\n{'='*60}")
    print(f"  生成對比報告...")
    report = build_compare_report(all_results.get("30B", {}), all_results.get("9B", {}))
    report_file = RESULTS_DIR / f"compare_{TIMESTAMP}.md"
    report_file.write_text(report, encoding="utf-8")
    print(f"  報告 → {report_file}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
