# 從零開始建構 GPT — 學習筆記
> 根據 Andrej Karpathy 教學影片《Let's build GPT: from scratch, in code, spelled out》整理
> 原始影片：https://youtu.be/kCc8FmEb1nY

---

## 目錄
1. [資料處理與標記化](#一資料處理與標記化)
2. [Bigram 基準語言模型](#二bigram-基準語言模型)
3. [自注意力機制](#三自注意力機制)
4. [位置編碼](#四位置編碼)
5. [縮放自注意力](#五縮放自注意力)
6. [三種注意力機制比較](#六三種注意力機制比較)
7. [完整 Transformer 區塊](#七完整-transformer-區塊)
8. [三種 Transformer 架構](#八三種-transformer-架構)
9. [預訓練、微調與 RLHF](#九預訓練微調與-rlhf)

---

## 一、資料處理與標記化

### 為什麼需要 Tokenization？

電腦無法直接處理文字，只能處理數字。Tokenization 的目的是**把文字轉換成整數序列**。

影片採用最簡單的**字元級 (character-level) tokenization**：

```python
chars = sorted(list(set(text)))
vocab_size = len(chars)  # 莎士比亞資料集約 65 個字元

stoi = { ch:i for i,ch in enumerate(chars) }  # string → int
itos = { i:ch for i,ch in enumerate(chars) }  # int → string

encode = lambda s: [stoi[c] for c in s]
decode = lambda l: ''.join([itos[i] for i in l])
```

| 方式 | 詞彙表大小 | 說明 |
|------|-----------|------|
| 字元級（影片） | ~65 | 簡單易懂，適合教學 |
| BPE（GPT-2/3） | ~50,000 | 子詞組合，實際應用 |

### Train / Val Split

```python
data = torch.tensor(encode(text), dtype=torch.long)

n = int(0.9 * len(data))
train_data = data[:n]   # 前 90% 訓練集
val_data   = data[n:]   # 後 10% 驗證集
```

驗證集用於**偵測過擬合 (overfitting)**，確認模型是真的學到規律而非死記訓練資料。

---

## 二、Bigram 基準語言模型

### 核心概念

> **只看當前字元，來預測下一個字元**（完全不考慮更早的上下文）

```python
class BigramLanguageModel(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.token_embedding_table = nn.Embedding(vocab_size, vocab_size)

    def forward(self, idx, targets=None):
        logits = self.token_embedding_table(idx)  # (B, T, C)

        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits  = logits.view(B*T, C)
            targets = targets.view(B*T)
            loss    = F.cross_entropy(logits, targets)

        return logits, loss
```

### 損失函數：Cross-Entropy Loss

$$\mathcal{L} = -\log P(\text{正確的下一個 token})$$

**初始 loss 理論值**：$-\log(\frac{1}{65}) \approx 4.17$（可作為 sanity check）

### 文本生成（自回歸）

```python
def generate(self, idx, max_new_tokens):
    for _ in range(max_new_tokens):
        logits, loss = self(idx)
        logits    = logits[:, -1, :]                        # 取最後時間步
        probs     = F.softmax(logits, dim=-1)
        idx_next  = torch.multinomial(probs, num_samples=1) # 隨機抽樣
        idx       = torch.cat((idx, idx_next), dim=1)
    return idx
```

> 使用 `multinomial` **隨機抽樣**而非 `argmax`，讓生成文本有多樣性。

### Bigram 的根本限制

| 問題 | 說明 |
|------|------|
| 記憶太短 | 只看前一個字元，忽略更早上下文 |
| 生成品質差 | 無長程語意連貫性 |
| 存在的意義 | 作為**基準線**，後續改進都要比它好 |

---

## 三、自注意力機制

### 注意力是一種「溝通」形式

每個 token 產生三個向量：

```
Q (Query)：「我想知道什麼？」
K (Key)  ：「我有什麼資訊？」
V (Value)：「如果你選我，我給你這個」
```

### 四個版本的演進

#### 版本 1：for 迴圈（最直觀但最慢）
```python
for b in range(B):
    for t in range(T):
        x_prev = x[b, :t+1, :]
        x_bow[b, t] = x_prev.mean(0)
```

#### 版本 2：矩陣乘法（核心技巧）

用**下三角矩陣**一次完成所有位置的加權聚合：

```python
a = torch.tril(torch.ones(T, T))
a = a / a.sum(dim=1, keepdim=True)  # 歸一化
out = a @ x  # (T,T) @ (T,C) = (T,C)
```

```
歸一化後的下三角矩陣：
[[1.00, 0.00, 0.00, 0.00],
 [0.50, 0.50, 0.00, 0.00],
 [0.33, 0.33, 0.33, 0.00],
 [0.25, 0.25, 0.25, 0.25]]
```

#### 版本 3：加入 Softmax + 遮蔽

```python
tril = torch.tril(torch.ones(T, T))
wei  = torch.zeros((T, T))
wei  = wei.masked_fill(tril == 0, float('-inf'))  # 遮蔽未來
wei  = F.softmax(wei, dim=-1)
out  = wei @ x
```

#### 版本 4：完整自注意力（可學習權重）

```python
k = key(x)    # (B, T, head_size)
q = query(x)  # (B, T, head_size)
v = value(x)  # (B, T, head_size)

wei = q @ k.transpose(-2, -1) * head_size**-0.5
wei = wei.masked_fill(tril == 0, float('-inf'))
wei = F.softmax(wei, dim=-1)
out = wei @ v
```

### 六個關鍵筆記

1. **注意力是溝通**：每個 token 主動決定要從哪些 token 蒐集資訊
2. **沒有空間概念**：本質上對「集合」操作，打亂順序結果相同
3. **Batch 維度不溝通**：不同樣本之間完全獨立
4. **Encoder vs Decoder**：有無遮蔽未來的差別
5. **三種注意力**：自注意力、交叉注意力、一般注意力
6. **縮放的必要性**：除以 `√head_size` 防止 Softmax 飽和

---

## 四、位置編碼

### 為什麼需要位置編碼？

純注意力機制把輸入視為**無序集合**，`"the cat sat"` 和 `"sat cat the"` 對它來說完全相同，必須手動注入位置資訊。

### 影片中的做法：可學習的位置嵌入

```python
self.token_embedding_table    = nn.Embedding(vocab_size, n_embd)  # 語意
self.position_embedding_table = nn.Embedding(block_size, n_embd)  # 位置

def forward(self, idx):
    B, T = idx.shape
    tok_emb = self.token_embedding_table(idx)
    pos_emb = self.position_embedding_table(torch.arange(T, device=device))
    x = tok_emb + pos_emb  # 語意 + 位置
```

### 兩種流派比較

| | 可學習位置嵌入（影片/GPT） | 固定三角函數（原始論文） |
|---|---|---|
| 優點 | 彈性高，模型自己學 | 可外推到更長序列 |
| 缺點 | 無法超過 `block_size` | 位置表示固定 |

原始論文公式：
$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{model}}}\right), \quad PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$

---

## 五、縮放自注意力

### 問題根源：點積數值過大

Q 和 K 的點積方差會隨 `head_size` 成比例膨脹：

$$\text{std}(q \cdot k) = \sqrt{\text{head\_size}}$$

| head_size | 點積標準差 |
|-----------|-----------|
| 8 | ≈ 2.8 |
| 16 | ≈ 4.0 |
| 64 | ≈ 8.0 |

### 數值過大如何破壞 Softmax？

```
輸入數值很大
    ↓
最大值的指數遠大於其他值
    ↓
Softmax 輸出趨近 one-hot
    ↓
注意力幾乎全集中在單一 token
    ↓
其他 token 資訊被忽略 + 梯度消失
    ↓
訓練初期就卡住
```

### 解法：除以 √head_size

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

縮放後方差恢復為 1，Softmax 正常運作。

```python
wei = q @ k.transpose(-2, -1) * (head_size ** -0.5)  # 縮放
```

---

## 六、三種注意力機制比較

### 核心差異：Q、K、V 來自哪裡？

| | Q 來源 | K 來源 | V 來源 | 典型場景 |
|---|---|---|---|---|
| **自注意力** | 序列本身 | 序列本身 | 序列本身 | GPT、BERT |
| **交叉注意力** | 序列 A | 序列 B | 序列 B | 機器翻譯 |
| **一般注意力** | 任意 | 任意 | 任意 | 早期 seq2seq |

### 直觀比喻

```
自注意力   = 一群人開會，每個人問其他同事問題
交叉注意力 = 翻譯員聽演講者說話，不斷查閱對方說過的內容
一般注意力 = 最廣義的「查詢-資料庫」關係
```

### 在完整 Transformer 中的位置

```
Encoder（來源序列）：
  [雙向自注意力] → [Feed Forward]
       ↓ K, V
Decoder（目標序列）：
  [Masked 自注意力] → [交叉注意力] → [Feed Forward]
```

> GPT 只有 **Masked 自注意力**，沒有交叉注意力（純解碼器架構）

---

## 七、完整 Transformer 區塊

### 整體結構

```
輸入 x
  │
  ├─→ LayerNorm → Multi-Head Self-Attention → + ←─┐ 殘差
  │←──────────────────────────────────────────────┘
  │
  ├─→ LayerNorm → Feed Forward → + ←──────────────┐ 殘差
  │←──────────────────────────────────────────────┘
  │
輸出 x
```

### 前饋層 (Feed Forward)

```python
class FeedForward(nn.Module):
    def __init__(self, n_embd):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),  # 擴張 4 倍
            nn.ReLU(),
            nn.Linear(4 * n_embd, n_embd),  # 壓縮回來
            nn.Dropout(dropout),
        )
```

> **自注意力**是「開會蒐集資訊」；**前饋層**是「回座位獨立思考」

拿掉前饋層的後果：多層疊加仍是線性變換，無法學習非線性的複雜規律。

### 殘差連接 (Residual Connections)

```python
x = x + self.sa(self.ln1(x))    # 自注意力 + 殘差
x = x + self.ffwd(self.ln2(x))  # 前饋層 + 殘差
```

**數學意義**：$F(x) = x + G(x)$，模型只需學習「需要改變什麼」而非「整個表示應該是什麼」

| 解決的問題 | 機制 |
|-----------|------|
| 梯度消失 | 提供梯度直接傳遞的「高速公路」 |
| 訓練初期不穩定 | 子層輸出是雜訊時，$x + \text{雜訊} \approx x$，原始資訊得以保留 |

### 層歸一化 (Layer Normalization)

```python
class LayerNorm(nn.Module):
    def forward(self, x):
        mean = x.mean(dim=-1, keepdim=True)
        std  = x.std(dim=-1, keepdim=True)
        return self.gamma * (x - mean) / (std + 1e-8) + self.beta
```

**LayerNorm vs BatchNorm**：

```
BatchNorm：沿樣本維度歸一化（跨樣本）← 不適合序列長度不固定的場景
LayerNorm：沿特徵維度歸一化（跨特徵）← Transformer 採用此方式
```

**Pre-Norm（影片）vs Post-Norm（原始論文）**：
- 現代大型模型多採用 Pre-Norm，訓練更穩定

### 四個元件總結

| 元件 | 解決的問題 | 拿掉的後果 |
|------|-----------|-----------|
| Feed Forward | 缺乏非線性表達 | 模型退化成線性 |
| 殘差連接 | 梯度消失 | 超過幾層就無法訓練 |
| LayerNorm | 訓練不穩定 | 學習率難調，容易爆炸或停滯 |

---

## 八、三種 Transformer 架構

### 純編碼器 (Encoder-Only)

- **注意力方向**：雙向，所有 token 互相看
- **核心目標**：深度理解輸入語意
- **代表模型**：BERT、RoBERTa、ALBERT
- **應用**：文本分類、情感分析、問答

```
注意力矩陣（全部可見）：
     A  B  C  D
A  [ ✓  ✓  ✓  ✓ ]
B  [ ✓  ✓  ✓  ✓ ]
C  [ ✓  ✓  ✓  ✓ ]
D  [ ✓  ✓  ✓  ✓ ]
```

### 純解碼器 (Decoder-Only)

- **注意力方向**：單向（Masked），只看過去
- **核心目標**：自回歸地生成文本
- **代表模型**：GPT 系列、LLaMA、Gemini
- **應用**：文本生成、對話、程式碼生成

```
注意力矩陣（下三角）：
     A  B  C  D
A  [ ✓  ✗  ✗  ✗ ]
B  [ ✓  ✓  ✗  ✗ ]
C  [ ✓  ✓  ✓  ✗ ]
D  [ ✓  ✓  ✓  ✓ ]
```

### Encoder-Decoder（兩者兼具）

- **注意力方向**：Encoder 雙向 + Decoder 單向 + 交叉注意力
- **核心目標**：理解來源序列後生成目標序列
- **代表模型**：T5、BART、Whisper、原始 Transformer
- **應用**：機器翻譯、文本摘要、語音辨識

### 三種架構對比

| | 編碼器 | 解碼器 | 編碼器-解碼器 |
|---|---|---|---|
| 注意力方向 | 雙向 | 單向（Masked） | 兩者兼具 |
| 交叉注意力 | ✗ | ✗ | ✓ |
| 典型代表 | BERT | GPT | T5 |
| 核心任務 | 理解 | 生成 | 理解後生成 |

> **GPT 選擇純解碼器的原因**：文本生成是純生成任務，不需要雙向理解，且可做到無限長度生成。

---

## 九、預訓練、微調與 RLHF

### 整體訓練流程

```
預訓練 (Pretraining)
    海量網路文本 → 學會預測下一個 token
    產出：基礎模型 (Base Model)
         ↓
監督式微調 (SFT)
    人工標注對話 → 學會對話格式
    產出：SFT 模型
         ↓
RLHF
    人類偏好回饋 → 學會符合人類價值觀
    產出：ChatGPT
```

### 預訓練 (Pretraining)

**目標**：預測下一個 token（與 nanoGPT 完全相同，只是規模極大）

| | nanoGPT（影片） | GPT-3 |
|---|---|---|
| 資料 | 莎士比亞全集 (~1MB) | CommonCrawl 等 (~570GB) |
| 訓練時間 | 幾分鐘 | 幾個月 |
| 參數量 | ~10M | 175B |

**模型從預測 token 中學到的能力**：
- 語言規則（語法、詞形變化）
- 事實知識（地理、歷史）
- 邏輯推理能力
- 程式碼規律

**根本問題**：預訓練模型只會「續寫文字」，不會真正「對話」。

### 監督式微調 (Supervised Finetuning, SFT)

用人工精心撰寫的高品質對話繼續訓練：

```
[Human]: 請解釋什麼是黑洞？
[Assistant]: 黑洞是一種重力極強的天體...（高品質回答）
```

| | 預訓練 | SFT |
|---|---|---|
| 資料 | 隨機網路文字 | 精選對話 |
| 數量 | 數千億 tokens | 數萬到數十萬筆 |
| 目標 | 學會語言 | 學會助理行為 |

### RLHF：人類回饋強化學習

**為什麼需要？** SFT 學會了格式，但不一定給出人類真正偏好的回答。

#### 三個步驟

**步驟一：收集人類偏好資料**
```
同一問題產生多個回答 → 人類標注員排名 → B > A > C
```

**步驟二：訓練獎勵模型 (Reward Model)**
```python
reward_model.train(
    輸入 = (問題, 回答),
    輸出 = 人類偏好分數
)
```

**步驟三：用強化學習（PPO）優化語言模型**
```
語言模型產生回答 → 獎勵模型打分 → PPO 更新參數 → 迭代
```

### 三個階段完整對比

| | 預訓練 | SFT | RLHF |
|---|---|---|---|
| 資料來源 | 網路文字 | 人工對話 | 人類排名偏好 |
| 資料量 | 超大（TB 級） | 中等（萬筆） | 較小（千筆） |
| 訓練目標 | 預測下一 token | 模仿好回答 | 最大化人類偏好 |
| 學到什麼 | 語言與知識 | 對話格式 | 價值觀對齊 |

### Karpathy 的關鍵洞察

> **預訓練**是把人類所有知識「壓縮」進模型參數的過程（99% 的工作量）；SFT 和 RLHF 只是「解鎖」這些已存在的能力。

```
預訓練 = 學習所有知識（壓縮網路）
SFT   = 教它如何表達知識（格式調整）
RLHF  = 教它表達符合人類價值觀的知識（行為對齊）
```

### 從 nanoGPT 到 ChatGPT

```
nanoGPT（影片）：        ChatGPT：
架構  ✓ GPT Transformer  架構  ✓ 相同
預訓練 ✓ 莎士比亞（小）  預訓練 ✓ 全網路（巨大）
SFT   ✗ 無              SFT   ✓ 數萬筆對話
RLHF  ✗ 無              RLHF  ✓ 人類偏好 + 強化學習
```

---

## 總結：完整架構一覽

```
原始文字
    ↓ Tokenization
整數序列
    ↓ Token Embedding + Position Embedding
向量表示
    ↓ × N 個 Transformer Block
    │   ├── LayerNorm
    │   ├── Multi-Head Self-Attention（token 溝通）
    │   ├── 殘差連接
    │   ├── LayerNorm
    │   ├── Feed Forward（獨立思考）
    │   └── 殘差連接
    ↓
最終表示
    ↓ Linear + Softmax
下一個 token 的機率分布
    ↓ 自回歸生成
文本輸出
```
