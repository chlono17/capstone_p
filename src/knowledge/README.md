# 知識沉澱

事件處理完成後回寫知識庫，供未來事件比對使用。資料依賴度低，GitHub Issues 本身就是活資料。

## 模組

| 模組 | 說明 |
|------|------|
| `writeback/` | 將處理過的事件整理進知識庫 |
| `taxonomy/` | 知識庫標籤體系，對照公開 IT ticket 分類 schema 校準 |

## 資料來源

- **主要**：GitHub Issues 本身、知識庫（原共筆已改用 Linear Document 管理）
- **補強**：HuggingFace [`Noise144/ticket_classification_IT_EN`](https://huggingface.co/datasets/Noise144/ticket_classification_IT_EN)（18 類 IT ticket 分類），以及 `DavinciTech/BERT_Categorizer`、`TuShar2309/ticket-classifier` 這類模型採用的 ITIL 標準分類欄位（Impact/Urgency/Type，12 類服務台分類），用來校準標籤體系
