# INPUT 層

使用者的知識輸入管道，支援多種格式，統一轉換為結構化文字後送入 AGENT 層。

## 輸入類型（待實作）

| 模組 | 輸入類型 | 技術選項 |
|------|---------|---------|
| `ocr/` | 手寫 / 相機 | Tesseract / PaddleOCR |
| `stt/` | 語音 | Whisper（本地） |
| `markdown/` | 文字 / Markdown | 直接解析 |
| `web_pdf/` | 網頁 / PDF | 爬蟲 + pdfplumber |

## 輸出格式

所有輸入最終轉換為標準化的 Markdown 文字，傳遞給 AGENT 層處理。
