# Git 使用指南

---

## 第一次設定（每台電腦只做一次）

### 設定你的身份
```bash
git config --global user.name "你的名字"
git config --global user.email "你的GitHub信箱"
```

### 設定 credential 儲存
Mac：
```bash
git config --global credential.helper osxkeychain
```
Windows：
```bash
git config --global credential.helper manager
```

### GitHub 登入用 Token，不是密碼

GitHub 不支援密碼登入，第一次 push 時會要求輸入：
- **Username**：你的 GitHub 帳號
- **Password**：填 Personal Access Token（不是你的 GitHub 密碼）

**建立 Token：**
1. 打開 https://github.com/settings/tokens/new
2. Note 填任意名稱（例如 `my-mac`）
3. Expiration 選 90 days 或 No expiration
4. 勾選 **repo**
5. 點 **Generate token** → 馬上複製，離開頁面就看不到了

設定好 credential helper 之後，輸入一次 token 就會記住，之後不用再輸入。

---

## 第一次建立 repo

```bash
cd 你的專案資料夾
git init
git remote add origin https://github.com/帳號/repo名稱.git
git add .
git commit -m "initial commit"
git branch -M main
git push -u origin main
```

> `git branch -M main` 和 `git push -u origin main` 只有第一次需要，之後直接 `git push`。

---

## 日常流程（改完東西就這樣）

```bash
git add .                      # 把所有改動加進來（或指定檔案）
git commit -m "說明你改了什麼"
git push
```

---

## 換 Remote（換到另一個 repo）

```bash
git remote set-url origin https://github.com/帳號/新repo名稱.git
git remote -v                  # 確認換掉了
git push -u origin main        # 第一次推加 -u
```

---

## 多人協作

### 組員第一次加入
```bash
git clone https://github.com/帳號/repo名稱.git
cd repo名稱
cp .env.example .env           # 建立自己的 .env，填自己的值
```

### 每次開始工作前，先拿最新版本
```bash
git pull
```

### 推上去讓大家看到
```bash
git add .
git commit -m "說明"
git push
```

---

## Branch（分支）

### 什麼時候用 branch？
- 要開發新功能，怕影響大家正在用的版本
- 要實驗性地改東西，不確定對不對
- 多人同時開發不同功能，避免互相干擾

### 常用 branch 指令

```bash
git branch                       # 看有哪些 branch，* 是你現在在哪
git switch -c 分支名稱            # 建立新 branch 並切換過去
git switch 分支名稱               # 切換到已有的 branch

git push -u origin 分支名稱      # 第一次把新 branch 推上 GitHub
git push                         # 之後直接 push
```

### 把 branch 合併回 main

```bash
git switch main                  # 切回 main
git pull                         # 拿最新的 main
git merge 分支名稱                # 把 branch 的內容合進來
git push
```

### 合併完刪掉 branch（選做）
```bash
git branch -d 分支名稱            # 刪本機的
git push origin --delete 分支名稱 # 刪 GitHub 上的
```

---

## 遇到衝突（Conflict）

衝突發生在：你和別人改了同一個檔案的同一行。

```bash
git pull   # 這時候 git 會告訴你哪個檔案有衝突
```

打開衝突的檔案，會看到：
```
<<<<<<< HEAD
你自己的版本
=======
別人的版本
>>>>>>> origin/main
```

手動決定要保留哪個版本，把 `<<<<<<<`、`=======`、`>>>>>>>` 這些行刪掉，然後：

```bash
git add 那個檔案
git commit -m "resolve conflict"
git push
```

**減少衝突的好習慣：**
- 每次開始工作前先 `git pull`
- 盡量每個人負責不同的檔案或 branch
- 常 commit、常 push，不要累積太多再一次推

---

## 不同裝置的情境

### 換了電腦，重新開始
```bash
git clone https://github.com/帳號/repo名稱.git
cd repo名稱
# 重新設定 .env，安裝環境
```

### 同一台電腦，繼續之前的工作
```bash
git pull    # 先拿最新版本，再開始改東西
```

### 組員 push 了，你要拿到他的更新
```bash
git pull
```

### 在 A 電腦 commit 了但忘記 push，換到 B 電腦
回 A 電腦補 push，然後 B 電腦 `git pull`。

### 用 git init 連到已有的 repo，pull 出現「no tracking information」

發生原因：`git init` 預設建的是 `master` branch，但 GitHub repo 是 `main`，對不上。

```bash
git checkout -b main origin/main   # 建立本機 main 並對應 GitHub 的 main
```

之後就可以正常 `git pull` 和 `git push` 了。

> 注意：`credential.helper` 要填 `osxkeychain`，不是 `osxkeygen`。

---

## 常見錯誤

| 錯誤訊息 | 原因 | 解法 |
|---------|------|------|
| `fatal: not a git repository` | 不在 repo 的資料夾裡 | `cd` 到正確的資料夾 |
| `Authentication failed` | 用了密碼，GitHub 要 Token | 用 Personal Access Token 當密碼 |
| `rejected - non-fast-forward` | 別人先 push 了，你版本比較舊 | 先 `git pull`，解完衝突再 push |
| `nothing to commit` | 沒有改任何東西 | 正常，不用擔心 |
| `Your branch is behind` | 本機版本比 GitHub 舊 | `git pull` |

---

## 常用指令速查

| 指令 | 做什麼 |
|------|--------|
| `git status` | 看哪些檔案改了 |
| `git log --oneline` | 看 commit 歷史（簡短版） |
| `git diff` | 看還沒 stage 的改動內容 |
| `git pull` | 從 GitHub 拉最新版本 |
| `git push` | 推上 GitHub |
| `git remote -v` | 看現在連到哪個 repo |
| `git restore 檔案` | 放棄某檔案的改動（還沒 add） |
| `git restore --staged 檔案` | 取消 git add（還沒 commit） |
| `git branch` | 看所有 branch |
| `git switch -c 名稱` | 建立並切換到新 branch |
| `git merge 名稱` | 把指定 branch 合併進來 |
