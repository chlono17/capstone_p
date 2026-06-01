---
title: [LLM中的Tokenization機制與BPE演算法探究]
date: 2026-05-22
author: chuYi
model: qwen2.5-14b-instruct-mlx
source: https://www.youtube.com/watch?v=zduSFxRajkE
tags:
  - Tokenization
  - BPE演算法
  - LLM訓練與使用
  - 模型效能
---

## 摘要
在實際操作中，需要理解LLM中的Tokenization機制以優化模型表現。首先要將文字轉換為UTF-8位元組序列，為了進一步壓縮資料，使用BPE演算法迭代合併最常出現的相鄰Token對。在訓練Tokenizer時，若加入大量日文或程式碼，將會讓這些語言的Token被壓縮得更短。此外，GPT系列模型執行BPE之前會先用Regex斷開文字，確保某些類別永遠不會被合併在一起。而像GPT-4這樣的模型，對連續空白字元的處理則是將其合併為單一Token。在特殊Tokens方面，模型微調過程中會引入新的特殊Tokens以區分內容。詞彙表大小的選擇需權衡序列長度與運算負擔。

## 問答
**Q: GPT 系列模型在執行 BPE 之前為什麼要先用 Regex 斷開文字？**
GPT 系列模型


**Q: 在處理非英語文本時，為什麼 Tokenizer 的訓練資料中包含較少的外語會導致 LLM 在處理這些語言時表現不佳？**
非英語文本在 Tokenizer 的訓練資料中佔比較低，這使得模型對於外語（如韓文）的處理能力較差。當非英語文本被切碎成極多個 Token（稱為Bloat），迅速耗盡模型的上下文長度，進而影響最終的表現。

**Q: 文章中提到的 "Solid Gold Magikarp" 這個例子，為什麼會造成模型出現未定義的行為？**
這是一種極端案例。因為 "SolidGoldMagikarp" 這個帳號名稱在 Tokenizer 的訓練資料中頻繁出現，獲得了一個專屬 Token。然而，在 LLM 的文本訓練集中從未出現過這個詞，導致該 Token 的參數在整個訓練過程中從未被更新。當使用者在提示詞中輸入這個詞時，會喚醒這組隨機初始化的參數，促使模型產生完全未定義、胡言亂語的行為。

## 模型補充問答
無