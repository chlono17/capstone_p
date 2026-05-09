# STORE 層

系統的儲存層，負責向量知識庫、結構化資料與媒體儲存。

## 儲存類型

| 目錄 | 類型 | 技術選項 | 用途 |
|------|------|---------|------|
| `vector/` | Vector DB | ChromaDB / FAISS | 語意搜尋，RAG 的知識來源 |
| `db/` | 結構化 DB | PostgreSQL / SQLite | 用戶資料、貼文、標籤 |
| `media/` | 媒體儲存 | 本地檔案系統 / MinIO | Podcast 音訊、圖片 |
