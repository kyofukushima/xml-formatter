# logic2_Paragraph.markdown 最終更新レポート

## 実施日
2025年10月28日

## 概要
`logic2_Paragraph.markdown`の「項目ラベルに該当するものに到達した場合の処理」セクションを、前のセクションの内容を参考に大幅に拡充しました。

---

## 1. 更新内容

### 1.1. 更新前

**元の内容（2行）:**
```markdown
## 項目ラベルに該当するものに到達した場合の処理

項目ラベルに該当するものに到達したら、item要素を分割して、項目ラベルの値をitemTitle要素として追加し、次のテキストをitemSentence要素として追加する。
```

### 1.2. 更新後

**新しい内容（309行）:**

#### 追加したサブセクション

1. **処理の流れ（5ステップ）**
   - 現在の処理を中断
   - ラベルパターンを判定
   - 親要素との関係を判定
   - 新しい要素を作成
   - 後続要素の処理

2. **パターン1: Column構造を持つList要素**
   - Column[0]にラベル、Column[1]にテキスト
   - 入力例・出力例を明示

3. **パターン2: ラベル+スペース+テキスト形式**
   - 単一Sentence内に「ラベル＋全角スペース＋テキスト」
   - 入力例・出力例を明示

4. **パターン3: 項目ラベル後に通常テキストが続く場合**
   - 通常テキストはList要素として子要素に配置
   - 次の項目ラベルまで同じ親要素内
   - 入力例・出力例を明示

5. **パターン4: 深い階層への移行（Subitem要素の作成）**
   - カタカナラベル → Subitem1作成
   - 階層判定ロジックの実例
   - 入力例・出力例を明示

6. **階層判定のロジック**
   - 現在の親要素の確認
   - 階層レベルの比較（浅い/同じ/深い）
   - レベル差が2以上の場合の処理

7. **注意事項**
   - 優先順位順の判定
   - 全角・半角対応
   - 括弧の種類対応
   - 階層レベルの飛び越し対応

---

## 2. 具体的な追加内容

### 2.1. 処理の流れ

```
1. 現在の処理を中断
   ↓
2. ラベルパターンを判定（階層レベル1〜7）
   ↓
3. 親要素との関係を判定
   ↓
4. 新しい要素を作成（Item、Subitem1等）
   ↓
5. 後続要素の処理（List要素として配置）
```

### 2.2. パターン別の変換例

#### パターン1: Column構造

```xml
<!-- 入力 -->
<List>
  <ListSentence>
    <Column Num="1"><Sentence>（１）</Sentence></Column>
    <Column Num="2"><Sentence>項目1のテキスト</Sentence></Column>
  </ListSentence>
</List>

<!-- 出力 -->
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence>項目1のテキスト</Sentence>
  </ItemSentence>
</Item>
```

#### パターン2: ラベル+スペース+テキスト

```xml
<!-- 入力 -->
<ParagraphSentence>
  <Sentence>（ア）　項目アのテキスト</Sentence>
</ParagraphSentence>

<!-- 出力 -->
<Item Num="1">
  <ItemTitle>（ア）</ItemTitle>
  <ItemSentence>
    <Sentence>項目アのテキスト</Sentence>
  </ItemSentence>
</Item>
```

#### パターン3: 通常テキストが続く

```xml
<!-- 入力 -->
<List><Sentence>１</Sentence> + <Sentence>項目1のタイトル</Sentence></List>
<List><Sentence>項目1の補足テキスト1</Sentence></List>
<List><Sentence>項目1の補足テキスト2</Sentence></List>

<!-- 出力 -->
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence><Sentence>項目1のタイトル</Sentence></ItemSentence>
  <List><Sentence>項目1の補足テキスト1</Sentence></List>
  <List><Sentence>項目1の補足テキスト2</Sentence></List>
</Item>
```

#### パターン4: 深い階層

```xml
<!-- 入力 -->
<List><Sentence>（１）</Sentence> + <Sentence>項目1</Sentence></List>
<List><Sentence>ア</Sentence> + <Sentence>サブ項目ア</Sentence></List>

<!-- 出力 -->
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence><Sentence>項目1</Sentence></ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence><Sentence>サブ項目ア</Sentence></Subitem1Sentence>
  </Subitem1>
</Item>
```

---

## 3. 階層判定のロジック

### 3.1. 親要素との関係

| 親要素 | 新規作成される要素 |
|--------|------------------|
| Paragraph | Item |
| Item | Subitem1 |
| Subitem1 | Subitem2 |
| Subitem2 | Subitem3 |
| ... | ... |
| Subitem9 | Subitem10 |

### 3.2. 階層レベルの比較

| 状況 | 動作 | 例 |
|------|------|-----|
| 前のラベルより浅い階層 | 親要素を閉じて新しい要素作成 | （ア） → （１） |
| 前のラベルと同じ階層 | 兄弟要素として作成 | （１） → （２） |
| 前のラベルより深い階層 | 子要素として作成 | （１） → ア |

### 3.3. レベル差が2以上の場合

**例:** Item（レベル2）→ 括弧カタカナ（レベル4）

**処理:**
1. Subitem1を空で作成
2. Subitem2を空で作成（括弧カタカナ用）
3. 括弧カタカナをSubitem2Titleに配置

```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence><Sentence>項目1</Sentence></ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title></Subitem1Title>
    <Subitem1Sentence><Sentence></Sentence></Subitem1Sentence>
    <Subitem2 Num="1">
      <Subitem2Title>（ア）</Subitem2Title>
      <Subitem2Sentence><Sentence>テキスト</Sentence></Subitem2Sentence>
    </Subitem2>
  </Subitem1>
</Item>
```

---

## 4. 注意事項

### ✅ ラベル判定の優先順位

1. 括弧科目名（`〔XXX〕`）
2. 第○パターン（`第○`）
3. 二重括弧カタカナ（`（（ア））`）
4. 括弧アルファベット（`（a）`）
5. 括弧カタカナ（`（ア）`）
6. 括弧数字（`（１）`）
7. カタカナ（`ア`）
8. アルファベット（`a、A`）
9. 数字（`１`）
10. 空

### ✅ 全角・半角対応

| 全角 | 半角 | 対応 |
|------|------|------|
| （ | ( | ✅ |
| ） | ) | ✅ |
| １ | 1 | ✅ |
| ａ | a | ✅ |
| 　 | (space) | ✅ |

### ✅ 括弧の種類対応

- 全角括弧：`（）`
- 半角括弧：`()`
- 混在：`（1)`、`(１）` も考慮

### ✅ 階層レベルの飛び越し

**シナリオ:** 数字（レベル1） → 括弧カタカナ（レベル4）

**対応:** 中間のレベル2（括弧数字）とレベル3（カタカナ）の空要素を自動作成

---

## 5. 実装への影響

### 5.1. convert_paragraph_focused.py（未実装）

**必要な機能:**
- 数字ラベルの検出
- 連続番号判定
- 新しいParagraph作成

### 5.2. convert_item_focused.py（未実装）

**必要な機能:**
- 括弧数字ラベルの検出
- Item作成
- ParagraphSentence → Item変換
- 後続List要素の子要素化

### 5.3. convert_subitem_focused.py（未実装）

**必要な機能:**
- カタカナ、括弧カタカナ、二重括弧カタカナの検出
- アルファベット（全半角、括弧付き）の検出
- Subitem1〜Subitem10の作成
- 階層レベルの判定
- 空の中間要素の自動作成

---

## 6. 文書の全体構成

### 更新後の構成（664行）

1. **項目ラベルについて**（63行）
   - パターン一覧（14種類）
   - 階層レベルの順序（レベル0〜7）
   - パターン判定の優先順位（1〜10）

2. **パターン1-1: ParagraphNumが空の場合**（22行）

3. **パターン: ParagraphSentenceがParagraphNum要素の次にない場合**（283行）
   - ParagraphNumの次にList要素が続く場合
   - List要素が文章の場合
   - List要素がラベル＋文章の場合

4. **項目ラベルに該当するものに到達した場合の処理**（309行）← **今回拡充**
   - 処理の流れ
   - パターン1〜4
   - 階層判定のロジック
   - 注意事項

---

## 7. 比較: 更新前後

### 7.1. 行数の変化

| セクション | 更新前 | 更新後 | 増加 |
|-----------|--------|--------|------|
| 項目ラベルに該当するものに到達した場合の処理 | 2行 | 309行 | **+307行** |
| 文書全体 | 358行 | 664行 | **+306行** |

### 7.2. 内容の充実度

**更新前:**
- 簡素な1文の説明のみ
- 具体例なし
- ロジック不明確

**更新後:**
- 5ステップの処理フロー
- 4つの具体的なパターン
- 各パターンに入力例・出力例
- 階層判定のロジック詳細
- 注意事項（4項目）

---

## 8. メリット

### ✅ 実装の明確化

- 5ステップの処理フローで実装順序が明確
- 各パターンの入力・出力例で期待動作が明確
- エッジケースへの対応方針が明確

### ✅ 開発効率の向上

- パターン別の実装が可能
- テストケースが明確
- デバッグが容易

### ✅ 保守性の向上

- ドキュメントが詳細
- 将来の拡張が容易
- 新メンバーのオンボーディングが容易

### ✅ 整合性の確保

- `修正ロジック分析.md`と整合
- Article特化スクリプトで実装済みのパターンと整合
- スキーマ定義と整合

---

## 9. 参照元

### 前のセクション（参考にした内容）

- **93-160行目**: List要素が文章の場合の変換例
- **242-313行目**: ラベル+スペース+テキスト形式の変換例

### 関連ドキュメント

- `修正ロジック分析.md`（2167行）
  - ルール2: ラベルパターンの判定
  - ルール3: 階層レベルの決定マトリクス
  - ルール6: 中間階層の空要素作成

---

## 10. 次のステップ

### Phase 1: ラベルユーティリティの実装

**`utils/label_utils.py`を作成:**
```python
def detect_label_pattern(label: str) -> str:
    """ラベルパターンを判定"""
    # 優先順位順にマッチング
    # ...

def get_hierarchy_level(label: str) -> int:
    """階層レベルを返す"""
    # ...

def split_label_and_text(text: str) -> Tuple[Optional[str], Optional[str]]:
    """ラベルとテキストを分離"""
    # ...
```

### Phase 2: Item特化スクリプトの実装

**`convert_item_focused.py`:**
- パターン1〜4の実装
- 階層判定ロジックの実装
- Num属性振り直しの統合

### Phase 3: Subitem特化スクリプトの実装

**`convert_subitem_focused.py`:**
- 深い階層への対応（Subitem1〜10）
- 空の中間要素の自動作成
- 階層レベルの飛び越し対応

### Phase 4: 統合テスト

- 全パターンの動作確認
- test_output5.xmlとの比較
- エッジケースのテスト

---

## 11. まとめ

### ✅ 完了したこと

1. **処理の流れを5ステップで定義**
   - 中断 → 判定 → 関係判定 → 作成 → 後続処理

2. **4つの具体的なパターンを追加**
   - Column構造
   - ラベル+スペース+テキスト
   - 通常テキストが続く場合
   - 深い階層への移行

3. **各パターンに入力例・出力例を明示**
   - 全て実際のXML形式
   - コピー&ペーストでテスト可能

4. **階層判定のロジックを詳細化**
   - 親要素との関係
   - 階層レベルの比較
   - レベル差が2以上の場合

5. **注意事項を4項目追加**
   - 優先順位、全角・半角、括弧の種類、階層飛び越し

### 📊 統計

| 項目 | 値 |
|------|-----|
| **追加行数** | +307行 |
| **パターン数** | 4パターン |
| **入力例・出力例** | 8セット |
| **総行数** | 664行 |

### 🎯 次の目標

1. `utils/label_utils.py`の実装
2. Item特化スクリプトの実装
3. 統合テストの実施

---

**実施者:** AI Assistant  
**作業日:** 2025年10月28日  
**ファイル:** `scripts/education_script/reports/logic2_Paragraph.markdown`  
**状態:** ✅ 完了

**関連ファイル:**
- `logic2_Paragraph.markdown`（664行）
- `logic2_Paragraph更新レポート.md`（前回作成）
- `修正ロジック分析.md`（2167行、参照元）


