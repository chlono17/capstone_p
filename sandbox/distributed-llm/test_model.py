#!/usr/bin/env python3
"""
Overnight model evaluation: Qwen3-30B-A3B-4bit
Domains: Math / Programming / Personal Time Planning
Dynamic: after each domain, adds follow-up tests based on scores.
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
RESULT_FILE = RESULTS_DIR / f"eval_{TIMESTAMP}.json"
REPORT_FILE = RESULTS_DIR / f"report_{TIMESTAMP}.md"

# ── Base Test Cases ──────────────────────────────────────────────────────────

BASE_TESTS = [
    # Math
    {
        "domain": "math", "id": "math_1", "label": "二次方程式",
        "prompt": "解方程式 x² - 5x + 6 = 0，列出完整步驟。",
        "expect_keywords": ["x = 2", "x = 3", "因式"],
    },
    {
        "domain": "math", "id": "math_2", "label": "微分",
        "prompt": "求 f(x) = x³ + 2x² - 5x + 1 的導函數 f'(x)，並求 x=1 時的切線斜率。",
        "expect_keywords": ["3x²", "4x", "-5", "2"],
    },
    {
        "domain": "math", "id": "math_3", "label": "機率",
        "prompt": "同時擲兩顆標準骰子，點數和恰好為 7 的機率是多少？請列出所有可能的組合。",
        "expect_keywords": ["1/6", "6", "36"],
    },
    {
        "domain": "math", "id": "math_4", "label": "質數篩法",
        "prompt": "用篩法（Sieve of Eratosthenes）找出 1 到 30 以內的所有質數，列出清單並說明步驟。",
        "expect_keywords": ["2", "3", "5", "7", "11", "13", "23", "29"],
    },
    {
        "domain": "math", "id": "math_5", "label": "數列求和",
        "prompt": "等差數列首項為 3，公差為 4，求前 20 項的總和。請用公式求解並驗證。",
        "expect_keywords": ["820", "公式", "79"],
    },
    # Programming
    {
        "domain": "programming", "id": "prog_1", "label": "二分搜尋",
        "prompt": "用 Python 實作二分搜尋法，要求：接受已排序的 list 和目標值，回傳 index 或 -1，附上時間複雜度分析。",
        "expect_keywords": ["def", "mid", "left", "right", "O(log n)"],
    },
    {
        "domain": "programming", "id": "prog_2", "label": "Debug",
        "prompt": "以下 Python 程式有 bug，請找出並修正：\n```python\ndef fibonacci(n):\n    if n == 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-3)\nprint(fibonacci(10))\n```\n期望輸出應為 55。",
        "expect_keywords": ["n-2", "fibonacci(n-2)", "55"],
    },
    {
        "domain": "programming", "id": "prog_3", "label": "資料結構選擇",
        "prompt": "你在設計一個瀏覽器的「上一頁/下一頁」功能，應該選用哪種資料結構？為什麼？請給出 Python 的實作草稿。",
        "expect_keywords": ["stack", "Stack", "堆疊", "push", "pop"],
    },
    {
        "domain": "programming", "id": "prog_4", "label": "排序複雜度",
        "prompt": "比較 Bubble Sort、Merge Sort、Quick Sort 的最佳、平均、最差時間複雜度，說明各自使用場景。",
        "expect_keywords": ["O(n²)", "O(n log n)", "Merge Sort", "Quick Sort"],
    },
    {
        "domain": "programming", "id": "prog_5", "label": "RAG 解釋",
        "prompt": "用簡單的語言解釋 RAG（Retrieval-Augmented Generation）的工作原理，說明它如何解決 LLM 的知識截止問題，給出一個具體應用場景。",
        "expect_keywords": ["檢索", "向量", "LLM", "context", "知識庫"],
    },
    # Time Planning
    {
        "domain": "time_planning", "id": "time_1", "label": "每週學習計畫",
        "prompt": "我是大學三年級資工系學生，要同時準備3門期末考（作業系統、演算法、資料庫），還要維持每週3次健身。請幫我規劃一份7天的作息表，具體到每天的時段安排。",
        "expect_keywords": ["週一", "週二", "小時", "休息", "複習"],
    },
    {
        "domain": "time_planning", "id": "time_2", "label": "番茄工作法",
        "prompt": "我想用番茄工作法提高學習效率，但常常分心。請給我5個實際可執行的技巧，並說明如何把番茄工作法融入大學生日常學習。",
        "expect_keywords": ["25分鐘", "番茄", "休息", "專注"],
    },
    {
        "domain": "time_planning", "id": "time_3", "label": "SMART 目標拆解",
        "prompt": "我想在3個月內完成一個 LLM 相關的 side project 並放上 GitHub。請幫我用 SMART 原則拆解成可執行的里程碑，附上每週具體任務。",
        "expect_keywords": ["SMART", "里程碑", "週", "具體"],
    },
    {
        "domain": "time_planning", "id": "time_4", "label": "考前衝刺計畫",
        "prompt": "期末考剩兩週，我有演算法和機器學習兩門課要考，演算法還差30%沒複習，機器學習差50%。請設計一份兩週衝刺計畫，每天可讀書時數要列清楚。",
        "expect_keywords": ["週", "小時", "演算法", "機器學習", "重點"],
    },
    {
        "domain": "time_planning", "id": "time_5", "label": "深度工作",
        "prompt": "Cal Newport 的「深度工作」理論如何應用在學生身上？請給出3個可以立刻實行的方法，並說明如何抵抗社群媒體的干擾。",
        "expect_keywords": ["深度", "專注", "社群", "排程"],
    },
]

# ── Dynamic follow-up pools ───────────────────────────────────────────────────

FOLLOWUP_POOLS = {
    "math": {
        "hard": [
            {
                "domain": "math", "id": "math_hard_1", "label": "積分（動態加測）",
                "prompt": "計算不定積分 ∫(3x² + 2x - 1)dx，並求定積分 ∫₀²(3x² + 2x - 1)dx 的值。",
                "expect_keywords": ["x³", "x²", "x", "10", "+C"],
            },
            {
                "domain": "math", "id": "math_hard_2", "label": "矩陣運算（動態加測）",
                "prompt": "設 A = [[1,2],[3,4]]，B = [[5,6],[7,8]]，求 A×B 和 det(A)。",
                "expect_keywords": ["19", "22", "43", "50", "-2"],
            },
        ],
        "easy": [
            {
                "domain": "math", "id": "math_easy_1", "label": "基礎代數（動態加測）",
                "prompt": "解方程式：2x + 5 = 15，並說明每個步驟代表的意義。",
                "expect_keywords": ["x = 5", "5"],
            },
        ],
    },
    "programming": {
        "hard": [
            {
                "domain": "programming", "id": "prog_hard_1", "label": "動態規劃（動態加測）",
                "prompt": "用動態規劃解決「爬樓梯」問題：有 n 個台階，每次可以爬 1 或 2 個台階，有多少種不同的爬法？請用 Python 實作，並分析時間和空間複雜度。",
                "expect_keywords": ["dp", "def", "fibonacci", "O(n)"],
            },
            {
                "domain": "programming", "id": "prog_hard_2", "label": "裝飾器（動態加測）",
                "prompt": "解釋 Python decorator 的工作原理，並實作一個可以計算函數執行時間的裝飾器，再示範一個記憶化（memoization）裝飾器。",
                "expect_keywords": ["@", "def wrapper", "functools", "cache", "time"],
            },
        ],
        "easy": [
            {
                "domain": "programming", "id": "prog_easy_1", "label": "List Comprehension（動態加測）",
                "prompt": "用 Python list comprehension 寫出：1) 1到10的平方數 2) 從一個列表中過濾出偶數 3) 二維矩陣展平。",
                "expect_keywords": ["[", "for", "if", "**2"],
            },
        ],
    },
    "time_planning": {
        "hard": [
            {
                "domain": "time_planning", "id": "time_hard_1", "label": "OKR 框架（動態加測）",
                "prompt": "請用 OKR 框架（Objectives and Key Results）幫一個想在半年內從初學者成為具備求職能力的前端工程師的大學生設定目標，要有3個 Objective，每個配2-3個 KR。",
                "expect_keywords": ["Objective", "KR", "半年", "前端"],
            },
        ],
        "easy": [
            {
                "domain": "time_planning", "id": "time_easy_1", "label": "晨間例行（動態加測）",
                "prompt": "設計一個30分鐘的晨間例行程序（morning routine），適合需要專注讀書的大學生，說明每個環節的目的。",
                "expect_keywords": ["分鐘", "早上", "專注", "例行"],
            },
        ],
    },
}

# ── API ───────────────────────────────────────────────────────────────────────

def chat(prompt: str, max_tokens: int = 1000) -> tuple[str, float, dict]:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt + " /no_think"}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    t0 = time.time()
    resp = requests.post(API_URL, json=payload, timeout=300)
    elapsed = time.time() - t0
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return content, elapsed, usage


def score(response: str, keywords: list[str]) -> dict:
    hits = [kw for kw in keywords if kw.lower() in response.lower()]
    kw_score = len(hits) / len(keywords) if keywords else 0
    length_score = min(len(response) / 400, 1.0)
    overall = round((kw_score * 0.65 + length_score * 0.35) * 10, 1)
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
        result = {**test, "response": "", "elapsed_sec": 0, "scores": {"overall": 0},
                  "usage": {}, "status": f"error: {e}"}
        print(f"         → ERROR: {e}")
    return result


# ── Report ────────────────────────────────────────────────────────────────────

def build_report(results: list[dict]) -> str:
    domain_names = {"math": "數學", "programming": "程式", "time_planning": "個人時間規劃"}
    domain_results: dict[str, list] = {"math": [], "programming": [], "time_planning": []}
    for r in results:
        domain_results[r["domain"]].append(r)

    lines = [
        "# Exo 模型評估報告",
        "",
        f"**模型**: `{MODEL}`  ",
        f"**日期**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**測試總數**: {len(results)}",
        "",
        "---",
        "",
        "## 一、分域總結",
        "",
        "| 域 | 測試數 | 平均分 (滿分10) | 評語 |",
        "|---|---|---|---|",
    ]

    for domain, dr in domain_results.items():
        ok = [r for r in dr if r["status"] == "ok"]
        avg = round(sum(r["scores"]["overall"] for r in ok) / len(ok), 1) if ok else 0
        if avg >= 8:
            comment = "優秀，邏輯清晰正確"
        elif avg >= 6:
            comment = "良好，偶有細節缺失"
        elif avg >= 4:
            comment = "普通，部分問題表現弱"
        else:
            comment = "待改善"
        lines.append(f"| {domain_names[domain]} | {len(dr)} | {avg} | {comment} |")

    # overall observations
    all_scores = [r["scores"]["overall"] for r in results if r["status"] == "ok"]
    overall_avg = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
    slowest = max((r for r in results if r["status"] == "ok"),
                  key=lambda r: r["elapsed_sec"], default=None)
    fastest = min((r for r in results if r["status"] == "ok"),
                  key=lambda r: r["elapsed_sec"], default=None)

    lines += [
        "",
        "---",
        "",
        "## 二、整體觀察",
        "",
        f"- **整體平均分**：{overall_avg} / 10",
        f"- **最慢回應**：{slowest['label'] if slowest else 'N/A'} ({slowest['elapsed_sec'] if slowest else 0}s)",
        f"- **最快回應**：{fastest['label'] if fastest else 'N/A'} ({fastest['elapsed_sec'] if fastest else 0}s)",
        "",
        "### 關鍵發現",
        "",
        "1. **必須加 `/no_think`**：Qwen3-30B 預設啟用 reasoning mode，"
        "在 max_tokens=600 下幾乎全耗在內部推理，實際輸出只剩 1-2 字。"
        "加上 `/no_think` 後輸出正常，reasoning_tokens 降至 1。",
        "",
        "2. **格式能力強**：回應使用 LaTeX 數學公式、Markdown 表格、code block，"
        "結構清晰，中文表達自然。",
        "",
        "3. **token 截斷風險**：超過 700 tokens 的列舉型回應（如質數清單）"
        "容易在 token limit 前截斷。建議此類任務設 max_tokens=1200+。",
        "",
        "---",
        "",
        "## 三、各域細節",
        "",
    ]

    for domain, dr in domain_results.items():
        lines += [f"### {domain_names[domain]}", ""]
        for r in dr:
            status_icon = "✅" if r["status"] == "ok" else "❌"
            dynamic_tag = "（動態加測）" if "動態加測" in r["label"] else ""
            lines += [
                f"#### {status_icon} {r['label']}{dynamic_tag}",
                "",
                f"- **分數**: {r['scores'].get('overall', 'N/A')} / 10",
                f"- **耗時**: {r['elapsed_sec']}s",
                f"- **字數**: {r['scores'].get('length', 0)}",
                f"- **關鍵字命中**: {r['scores'].get('keyword_hits', [])}",
                "",
                "<details><summary>查看回應（前 800 字）</summary>",
                "",
                "```",
                r["response"][:800] + ("..." if len(r["response"]) > 800 else ""),
                "```",
                "",
                "</details>",
                "",
            ]

    lines += [
        "---",
        "",
        "## 四、建議",
        "",
        "| 場景 | 建議設定 |",
        "|---|---|",
        "| 一般問答 | `/no_think` + max_tokens=800 |",
        "| 程式碼生成 | `/no_think` + max_tokens=1200 + temperature=0.5 |",
        "| 列舉/清單類 | `/no_think` + max_tokens=1500 |",
        "| 需要深度推理（如數學證明） | 不加 `/no_think`，max_tokens=2000+ |",
        "",
        "---",
        "",
        f"*報告由 test_model.py 自動生成 | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ]
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"  Model : {MODEL}")
    print(f"  API   : {API_URL}")
    print(f"  Start : {TIMESTAMP}")
    print(f"  Tests : {len(BASE_TESTS)} base + dynamic follow-ups")
    print(f"{'='*60}\n")

    all_results: list[dict] = []
    domain_scores: dict[str, list[float]] = {"math": [], "programming": [], "time_planning": []}
    domains_order = ["math", "programming", "time_planning"]
    domain_names = {"math": "數學", "programming": "程式", "time_planning": "個人時間規劃"}

    # Group base tests by domain
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

        # Dynamic adjustment
        avg = (sum(domain_scores[domain]) / len(domain_scores[domain])
               if domain_scores[domain] else 0)
        print(f"\n  → {domain_names[domain]} 平均分: {avg:.1f}/10")

        pool = FOLLOWUP_POOLS.get(domain, {})
        if avg >= 7.5 and "hard" in pool:
            print(f"  → 分數高，加測難題...")
            for ft in pool["hard"][:1]:
                result = run_test(ft)
                all_results.append(result)
                if result["status"] == "ok":
                    domain_scores[domain].append(result["scores"]["overall"])
                RESULT_FILE.write_text(
                    json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
                time.sleep(3)
        elif avg < 5.5 and "easy" in pool:
            print(f"  → 分數偏低，加測基礎題...")
            for ft in pool["easy"][:1]:
                result = run_test(ft)
                all_results.append(result)
                if result["status"] == "ok":
                    domain_scores[domain].append(result["scores"]["overall"])
                RESULT_FILE.write_text(
                    json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
                time.sleep(3)

    # Final report
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
