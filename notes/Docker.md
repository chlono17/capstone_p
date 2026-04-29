# Docker 使用指南

---

## 核心概念

| 名詞 | 意思 |
|------|------|
| **Image** | 像是軟體的安裝包，只讀，不會變 |
| **Container** | Image 跑起來之後的執行實體，像是「開啟的程式」 |
| **Volume** | Container 的資料儲存空間，Container 刪掉後資料還在 |
| **docker-compose** | 用一個 YAML 檔定義多個 Container，一次啟動/停止 |

---

## 最常用：docker compose 指令

### 啟動
```bash
docker compose up -d
```
- `up`：建立並啟動所有 Container
- `-d`：背景執行（detached）。**不加的話會佔住終端機，關掉視窗就停了**
- 第一次跑會自動下載 Image

### 停止
```bash
docker compose down
```
- 停止並移除 Container
- **Volume 不會刪除**，資料（n8n 的 workflow、設定）都還在
- 下次 `up` 會從同一個 Volume 繼續

### 什麼時候要 down 再 up？
| 情況 | 做法 |
|------|------|
| 修改了 docker-compose.yml | `down` → `up -d` |
| 修改了 `.env` | `down` → `up -d` |
| 電腦重開機後要恢復 | 直接 `up -d`（不需要 down） |
| 日常使用，不需要關 | 不用動，Container 會自動重啟 |
| 只是改了 n8n workflow JSON | 不需要 down，只需要跑 import |

---

## 查看狀態

```bash
docker compose ps          # 看哪些 Container 在跑、狀態是什麼
docker ps                  # 看所有 Container（不限這個 compose）
```

輸出會顯示：
- `running`：正在跑
- `exited`：已停止
- `restarting`：在重啟（通常是出錯了）

---

## 看 Log（出錯時最常用）

```bash
docker compose logs n8n              # 看 n8n 的 log
docker compose logs -f n8n           # 即時追蹤 log（-f = follow）
docker compose logs --tail=50 n8n    # 只看最後 50 行
```

> 遇到問題先看 log，通常錯誤訊息都在這裡。

---

## 強制移除特定 Container

```bash
docker rm -f container名稱
```

例如移除卡住的 import container：
```bash
docker rm -f para_n8n_import
```

> `-f` = force，就算 Container 還在跑也強制移除

---

## n8n workflow 匯入

```bash
# 第一次啟動後匯入，或更新 workflow JSON 後重新匯入
docker compose --profile import up n8n-import
```

如果出現網路錯誤（network not found）：
```bash
docker rm -f para_n8n_import          # 先強制刪掉舊的
docker compose --profile import up n8n-import   # 再重新跑
```

---

## Volume 管理

```bash
docker volume ls                       # 列出所有 Volume
docker volume inspect para-ai-system_n8n_data   # 查看 Volume 內容位置
```

**什麼時候 Volume 會被刪？**
```bash
docker compose down -v    # 加 -v 才會刪 Volume（危險！n8n 資料會消失）
docker compose down       # 不加 -v，Volume 保留（平常用這個）
```

---

## 進入 Container 內部（除錯用）

```bash
docker exec -it para_n8n sh    # 進入 n8n container 的 shell
exit                            # 離開
```

用途：確認環境變數有沒有生效
```bash
docker exec para_n8n env | grep LLM    # 看 LLM 相關的環境變數
docker exec para_n8n env | grep N8N    # 看 N8N 相關的環境變數
```

---

## 更新 Image

```bash
docker compose pull            # 拉最新版本的 Image
docker compose down
docker compose up -d
```

> 平常不需要常做，除非 n8n 有重要更新

---

## 常見錯誤

| 錯誤訊息 | 原因 | 解法 |
|---------|------|------|
| `network not found` | 網路設定殘留 | `docker compose down` 再 `up -d` |
| `port is already allocated` | port 被佔用 | 找出並關掉佔用 5678 的程式 |
| `no such service` | compose 檔案名稱或路徑不對 | 確認在正確資料夾 |
| Container 一直 `restarting` | 啟動時出錯 | `docker compose logs n8n` 看原因 |
| `permission denied` | 掛載的資料夾權限問題 | `chmod` 或確認路徑正確 |

---

## 這個專題的日常指令速查

```bash
# 每次開電腦要用系統前
docker compose up -d

# 修改 .env 或 docker-compose.yml 後
docker compose down && docker compose up -d

# 更新 workflow JSON 後
docker rm -f para_n8n_import
docker compose --profile import up n8n-import

# 出錯了，看 log
docker compose logs --tail=50 n8n

# 不用了，關掉（資料不會消失）
docker compose down
```
