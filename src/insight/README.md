# 智慧洞察

比對事件 log 與 SOP，找出異常與對應處理方式。資料依賴度高，是四個功能中唯一需要一批已知結論的歷史 case 才能驗證比對準不準的模組。

## 模組

| 模組 | 說明 |
|------|------|
| `parser/` | 讀取 GitHub Issues/PR/CI log，抽取事件特徵 |
| `anomaly/` | 對照歷史 case 判斷是否為已知異常模式 |
| `sop_match/` | 將事件對應到既有處理流程 |

## 資料來源

- **主要**：團隊自身 GitHub Issues、PR 討論、CI log
- **補強**：[LogHub](https://github.com/logpai/loghub)（HDFS/BGL/Thunderbird/Zookeeper 系統 log，有異常標籤，學界標準 benchmark），用於驗證異常偵測能力
