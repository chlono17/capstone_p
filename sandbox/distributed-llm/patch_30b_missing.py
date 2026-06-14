#!/usr/bin/env python3
"""
補跑 30B 的 3 題缺失結果：lc_3, int_1, int_2
執行前：在 Exo dashboard 切換到 Qwen3-30B-A3B-4bit
"""

import json, time, requests
from pathlib import Path

MODEL    = "mlx-community/Qwen3-30B-A3B-4bit"
API_URL  = "http://localhost:52415/v1/chat/completions"
RESULTS_DIR = Path(__file__).parent / "test_results"

MISSING_TESTS = [
    {"domain": "langchain", "id": "lc_3", "label": "LangGraph vs LangChain",
     "prompt": "LangGraph 和 LangChain 的關係是什麼？LangGraph 解決了哪些痛點？說明 Node、Edge、State 概念，舉例什麼場景應選 LangGraph 而不是 LangChain。",
     "expect_keywords": ["Node", "Edge", "State", "循環", "有向圖", "狀態機", "graph"]},

    {"domain": "integration", "id": "int_1", "label": "技術選型",
     "prompt": "從零建「自動整理 Obsidian 筆記並生成摘要」的 AI 系統，比較三個方案並選出最適合的：A. 純 LangChain + Function Calling  B. LangGraph + MCP Server  C. 自己用 Python 寫 Agent loop + OpenAI API",
     "expect_keywords": ["LangGraph", "MCP", "優缺點", "選擇", "Obsidian", "理由"]},

    {"domain": "integration", "id": "int_2", "label": "RAG vs Fine-tuning vs Agent",
     "prompt": "對於「讓 AI 回答公司內部文件問題」，比較 RAG、Fine-tuning、Agent+工具搜尋 三種方案。從成本、維護難度、回答品質、知識更新速度四個維度比較，給出選型建議。",
     "expect_keywords": ["RAG", "Fine-tuning", "Agent", "成本", "維護", "更新", "比較"]},
]


def chat(prompt: str, max_tokens: int = 1800) -> tuple[str, float]:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt + " /no_think"}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "enable_thinking": False,
    }
    for attempt in range(4):
        try:
            t0 = time.time()
            r = requests.post(API_URL, json=payload, timeout=300)
            elapsed = time.time() - t0
            if r.status_code == 404:
                wait = 30 * (attempt + 1)
                print(f"  404，等 {wait}s 重試 ({attempt+1}/3)...", flush=True)
                time.sleep(wait)
                continue
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            return content, elapsed
        except requests.exceptions.Timeout:
            if attempt < 3:
                print(f"  timeout，重試 ({attempt+1}/3)...", flush=True)
                time.sleep(10)
                continue
            raise
    raise RuntimeError("API 連續失敗，已重試 3 次")


def score(response: str, keywords: list) -> dict:
    hits = [kw for kw in keywords if kw.lower() in response.lower()]
    kw = len(hits) / len(keywords) if keywords else 0
    ln = min(len(response) / 500, 1.0)
    return {
        "keyword_hits": hits,
        "keyword_score": round(kw * 10, 1),
        "length": len(response),
        "overall": round((kw * 0.65 + ln * 0.35) * 10, 1),
    }


def warmup() -> bool:
    print(f"暖機 {MODEL.split('/')[-1]}...", flush=True)
    for i in range(10):
        try:
            r = requests.post(API_URL, json={
                "model": MODEL,
                "messages": [{"role": "user", "content": "hi /no_think"}],
                "max_tokens": 10,
                "enable_thinking": False,
            }, timeout=60)
            if r.status_code == 200:
                print("✓ 模型就緒\n", flush=True)
                return True
        except Exception:
            pass
        print(f"  暖機 {i+1}/10，等 15s...", flush=True)
        time.sleep(15)
    return False


def merge_and_update_report(new_results: dict):
    # Load existing 30B agent results
    agent_file = sorted(RESULTS_DIR.glob("eval_agent_20260603_1129.json"))
    if not agent_file:
        print("ERROR: 找不到 eval_agent_20260603_1129.json")
        return

    with open(agent_file[0]) as f:
        existing = json.load(f)

    # Replace/append new results
    existing_by_id = {r["id"]: r for r in existing}
    for id_, result in new_results.items():
        existing_by_id[id_] = result
    updated = list(existing_by_id.values())

    # Save merged file
    merged_path = RESULTS_DIR / "eval_agent_30B_complete.json"
    merged_path.write_text(json.dumps(updated, ensure_ascii=False, indent=2))
    print(f"\n合併結果已存至: {merged_path}")

    # Regenerate final comparison report
    regen_report(merged_path)


def regen_report(agent30_path: Path):
    from datetime import datetime

    with open(RESULTS_DIR / "eval_20260603_0419.json") as f:
        data30_g = json.load(f)
    with open(agent30_path) as f:
        data30_a = json.load(f)
    with open(sorted(RESULTS_DIR.glob("eval_9B_20260603_1758.json"))[0]) as f:
        data9_list = json.load(f)

    data30 = {r["id"]: r for r in data30_g + data30_a}
    data9  = {r["id"]: r for r in data9_list}

    def s30(id_):
        r = data30.get(id_)
        if not r or r.get("status","").startswith("error"): return None
        sc = r.get("scores", {})
        v = sc.get("overall", sc.get("keyword_score"))
        return v if v and v > 0 else None

    def s9(id_):
        r = data9.get(id_)
        return r["scores"]["overall"] if r else None

    STD = [
        ("數學",              ["math_1","math_2","math_3","math_4","math_5"]),
        ("程式",              ["prog_1","prog_2","prog_3","prog_4","prog_5"]),
        ("時間規劃",          ["time_1","time_2","time_3","time_4","time_5"]),
        ("LLM Agent",         ["agent_1","agent_2","agent_3","agent_4"]),
        ("MCP",               ["mcp_1","mcp_2","mcp_3"]),
        ("LangChain/LangGraph",["lc_1","lc_2","lc_3"]),
        ("整合比較",          ["int_1","int_2"]),
    ]
    LABEL = {r["id"]: r["label"] for r in data9_list}

    all30 = [(id_, s30(id_)) for _, ids in STD for id_ in ids if s30(id_) is not None]
    all9  = [(id_, s9(id_))  for _, ids in STD for id_ in ids if s9(id_)  is not None]
    avg30 = sum(v for _,v in all30) / len(all30)
    avg9  = sum(v for _,v in all9)  / len(all9)

    lines = [
        "# Qwen3-30B-A3B-4bit vs Qwen3.5-9B-8bit 完整對比報告（30B 補全版）",
        "",
        f"> 生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        "> 測試題數：27 題（全部）",
        "",
        "---", "",
        "## 一、總覽", "",
        "| 指標 | 30B-4bit | 9B-8bit |",
        "|------|---------|---------|",
        f"| 有效題數 | {len(all30)}/27 | {len(all9)}/27 |",
        f"| 平均分 | **{avg30:.2f}/10** | **{avg9:.2f}/10** |",
        f"| 速度中位 | ~58s（兩機分散）| ~196s（單機）|",
        "",
        "---", "",
        "## 二、分域對比", "",
        "| 域 | 30B-4bit | 9B-8bit | 差距 |",
        "|-----|---------|---------|------|",
    ]

    for label, ids in STD:
        s30s = [s30(i) for i in ids if s30(i) is not None]
        s9s  = [s9(i)  for i in ids if s9(i)  is not None]
        a30 = sum(s30s)/len(s30s) if s30s else None
        a9  = sum(s9s)/len(s9s)   if s9s  else None
        a30s = f"{a30:.2f} ({len(s30s)}/{len(ids)})" if a30 is not None else "—"
        a9s  = f"{a9:.2f}" if a9 is not None else "—"
        if a30 and a9:
            d = a30 - a9
            ds = f"+{d:.2f} 30B↑" if d > 0.3 else f"{d:.2f} 9B↑" if d < -0.3 else f"{d:.2f} ≈"
        else:
            ds = "—"
        lines.append(f"| {label} | {a30s} | {a9s} | {ds} |")

    lines += [
        f"| **均分** | **{avg30:.2f}** | **{avg9:.2f}** | **{avg30-avg9:+.2f}** |",
        "",
        "---", "",
        "## 三、逐題對比", "",
        "| ID | 題目 | 域 | 30B | 9B | ▲ |",
        "|----|----|---|----|----|---|",
    ]
    for label, ids in STD:
        for id_ in ids:
            ql = LABEL.get(id_, id_)
            v30 = s30(id_); v9 = s9(id_)
            v30s = f"{v30:.1f}" if v30 is not None else "—"
            v9s  = f"{v9:.1f}"  if v9  is not None else "—"
            if v30 and v9:
                d = v30 - v9
                m = "30B" if d > 0.5 else "9B" if d < -0.5 else "≈"
            else:
                m = "—"
            lines.append(f"| {id_} | {ql} | {label} | {v30s} | {v9s} | {m} |")

    lines += [
        "",
        "---", "",
        "## 四、使用建議", "",
        "| 情境 | 建議 | 理由 |",
        "|------|------|------|",
        "| 即時對話 / 快速草稿 | **9B-8bit** | 單機即可，速度 ~3× 快 |",
        "| 複雜演算法 / 程式分析 | **30B-4bit** | prog_4 排序複雜度 30B 10.0 vs 9B 6.8 |",
        "| Agent / MCP 概念 | **9B-8bit** | 9B 在此域明顯領先 |",
        "| 整合架構選型 | **30B-4bit** | 跨域分析能力更強 |",
        "| M4 Mini 離線 | **9B-8bit** | 30B 需兩機合計 ~40GB |",
        "",
        "---",
        "",
        "*自動生成 by patch_30b_missing.py | 2026-06-03*",
    ]

    out = RESULTS_DIR / "FINAL_compare_30B_vs_9B.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"報告已更新: {out}")
    print(f"\n30B {avg30:.2f}/10 ({len(all30)}/27)  |  9B {avg9:.2f}/10 ({len(all9)}/27)")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  30B 補跑：lc_3, int_1, int_2")
    print("  請先在 Exo dashboard 載入 Qwen3-30B-A3B-4bit")
    print("=" * 60)
    print()

    if not warmup():
        print("✗ 無法連接 30B，請確認 Exo dashboard 已載入模型")
        exit(1)

    new_results = {}
    for test in MISSING_TESTS:
        print(f"[{test['id']}] {test['label']}", flush=True)
        print(f"Q: {test['prompt'][:100]}...", flush=True)
        try:
            resp, elapsed = chat(test["prompt"])
            sc = score(resp, test["expect_keywords"])
            r = {**test, "response": resp, "elapsed_sec": round(elapsed, 2),
                 "scores": sc, "status": "ok", "usage": {}}
            print(f"  → {elapsed:.1f}s | score {sc['overall']}/10 | {sc['length']} chars", flush=True)
        except Exception as e:
            r = {**test, "response": "", "elapsed_sec": 0,
                 "scores": {"overall": 0, "keyword_hits": [], "length": 0},
                 "status": f"error: {e}", "usage": {}}
            print(f"  → ERROR: {e}", flush=True)
        new_results[test["id"]] = r
        time.sleep(3)

    print("\n" + "=" * 60)
    print("  合併結果並更新報告...")
    print("=" * 60)
    merge_and_update_report(new_results)
