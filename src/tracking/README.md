# 總結追蹤

將事件討論串整理成結構化報告，並追蹤處理進度。

## 模組

| 模組 | 說明 |
|------|------|
| `report_gen/` | 從 bug/issue 討論串生成事件報告 |
| `status/` | 追蹤事件處理進度 |

## 資料來源

- **主要**：團隊真實踩過的 bug/issue 討論串
- **補強**：Kaggle [`suraj520/customer-support-ticket-dataset`](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset)——只借欄位 schema（type/subject/description/resolution/priority）當報告輸出格式的參考模板，不用其消費性支援內容
