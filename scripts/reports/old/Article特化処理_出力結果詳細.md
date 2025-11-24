# Article特化処理の出力結果詳細

## 実施日
2025年10月28日

## 対象ファイル
- **入力**: `test_input5.xml`
- **出力**: `test_input5_article_v2.xml`
- **スクリプト**: `convert_article_focused.py` (連続番号判定版)

---

## 1. 全体統計

### 要素数の変化

| 要素名 | 入力 | 出力 | 差分 |
|--------|------|------|------|
| Article | 13 | 14 | +1 |
| Paragraph | 13 | 86 | **+73** |
| Item | 0 | 0 | 0 |
| List | 593 | 512 | -81 |

### ParagraphNumの分布変化

| ParagraphNum | 入力 | 出力 | 差分 |
|-------------|------|------|------|
| **１** | 8 | 18 | **+10** |
| **２** | 0 | 4 | **+4** |
| **３** | 0 | 1 | **+1** |
| **４** | 0 | 1 | **+1** |
| **５** | 0 | 1 | **+1** |
| **６** | 0 | 1 | **+1** |
| **(空)** | 5 | 60 | **+55** |
| **合計** | 13 | 86 | **+73** |

---

## 2. 変換の詳細

### 2.1. 数字ラベルを持つList要素の分布（入力XML）

入力XMLで数字ラベル（純粋な数字、括弧なし）を持つList要素: **49個**

| ラベル | 出現回数 |
|--------|---------|
| ２ | 17個 |
| ３ | 14個 |
| １ | 10個 |
| ４ | 5個 |
| ５ | 2個 |
| ６ | 1個 |

### 2.2. 実際に変換されたList要素

- **変換されたList**: 81個（593 - 512 = 81）
- **新規作成されたParagraph**: 73個（86 - 13 = 73）

**差異:** 81個のListが変換されたが、73個のParagraphが作成された。
→ **差: 8個**（複数のListが1つのParagraphに統合された可能性）

### 2.3. ParagraphNum別の新規作成数

| ParagraphNum | 新規作成数 |
|-------------|----------|
| １ | +10個 |
| ２ | +4個 |
| ３ | +1個 |
| ４ | +1個 |
| ５ | +1個 |
| ６ | +1個 |
| (空) | **+55個** |

**合計新規作成:** 73個

---

## 3. 各Articleの構造

### Article[0] - Num=999999999
- **Paragraph数**: 2個
- **ParagraphNum**: `(空), １`
- **List残存**: 0個

### Article[1] - Num=999999999
- **Paragraph数**: 5個
- **ParagraphNum**: `１, ２, (空), (空), (空)`
- **List残存**: 10個
- **特徴**: 連続番号`１→２`が正しく変換されている

### Article[2] - Num=999999999
- **Paragraph数**: 12個
- **ParagraphNum**: `１, (空)×11`
- **List残存**: 97個
- **特徴**: `１`の後は空のParagraphが続く

### Article[8] - Num=999999999
- **Paragraph数**: 6個
- **ParagraphNum**: `１, ２, ３, ４, ５, ６`
- **List残存**: 0個
- **特徴**: **連続番号が完璧に変換されている！**

### Article[13] - Num=2, Title=第２
- **Paragraph数**: 36個
- **ParagraphNum**: `(空)×2, １, (空)×4, １, (空)×26...`
- **List残存**: 358個
- **特徴**: **Article分割後の新しいArticle**、最も多くのParagraphを持つ

---

## 4. 成功した変換パターン

### ✅ パターン1: 連続番号の完全変換（Article[8]）

**入力（推定）:**
```xml
<Article>
  <Paragraph>
    <List><Column>１</Column><Column>内容1</Column></List>
    <List><Column>２</Column><Column>内容2</Column></List>
    <List><Column>３</Column><Column>内容3</Column></List>
    <List><Column>４</Column><Column>内容4</Column></List>
    <List><Column>５</Column><Column>内容5</Column></List>
    <List><Column>６</Column><Column>内容6</Column></List>
  </Paragraph>
</Article>
```

**出力:**
```xml
<Article>
  <Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>...</ParagraphSentence>
  </Paragraph>
  <Paragraph Num="2">
    <ParagraphNum>２</ParagraphNum>
    <ParagraphSentence>...</ParagraphSentence>
  </Paragraph>
  <!-- ... ６まで -->
</Article>
```

**結果:** ✅ **完璧な変換**

### ✅ パターン2: Article分割（Article[12] → Article[13]）

**入力（推定）:**
```xml
<Article>
  <Paragraph>
    <List><Column>第１</Column><Column>目標</Column></List>
    ...
    <List><Column>第２</Column><Column>各科目</Column></List>
    ...
  </Paragraph>
</Article>
```

**出力:**
```xml
<Article Num="1">
  <ArticleTitle>第１</ArticleTitle>
  ...
</Article>
<Article Num="2">
  <ArticleTitle>第２</ArticleTitle>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>各科目</Sentence>
    </ParagraphSentence>
  </Paragraph>
  ...
</Article>
```

**結果:** ✅ **正常に分割**

---

## 5. 問題のあるパターン

### ⚠️ 問題1: 空のParagraphNumの大量作成（+55個）

**現象:**
- 入力: 5個の空ParagraphNum
- 出力: 60個の空ParagraphNum
- 差分: **+55個**

**原因（推定）:**
1. **既存Paragraphの保持**: 入力XMLの既存Paragraph要素がそのまま出力に含まれている
2. **List要素のColumn構造なし**: 一部のList要素はColumn構造を持たず、そのまま保持されている
3. **変換されなかったList要素の親Paragraph**: 変換されなかったList要素を含むParagraphがそのまま保持されている

**具体例（Article[2]）:**
```
入力:
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>...</ParagraphSentence>
  <List><Column>（１）</Column>...</List>  ← 括弧付き数字、変換されない
  <List><Column>（２）</Column>...</List>  ← 括弧付き数字、変換されない
  ...
</Paragraph>

出力:
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>...</ParagraphSentence>
</Paragraph>
<Paragraph Num="2">
  <ParagraphNum>(空)</ParagraphNum>  ← 新規作成
  <List><Column>（１）</Column>...</List>  ← 保持されたまま
  <List><Column>（２）</Column>...</List>  ← 保持されたまま
  ...
</Paragraph>
```

### ⚠️ 問題2: 連続していない数字の扱い

**入力XMLのラベル分布:**
- `１`: 10個
- `２`: 17個（`１`より多い！）
- `３`: 14個

**推定される構造:**
```xml
<Paragraph>
  <List><Column>（１）</Column>...</List>  ← 括弧付き
  <List><Column>（２）</Column>...</List>  ← 括弧付き
  <List><Column>２</Column>...</List>      ← 純粋な数字、でも連続していない
</Paragraph>
```

**現在のロジック:**
- `２`は純粋な数字
- しかし、前のParagraphNumが`（１）`（括弧付き）または存在しない場合、連続性判定で`False`
- したがって、List要素として保持される

**結果:** ✅ **意図通りの動作**（括弧付きから数字への移行は連続とみなさない）

---

## 6. 残存List要素の分析

### 残存List要素: 512個

**すべてColumn構造を持つ:**
- サンプル50個すべてがColumn構造あり
- これらはItem特化処理で処理される予定

**ラベルの種類（推定）:**
1. 括弧付き数字: `（１）`, `（２）`, `（３）`など
2. カタカナ: `ア`, `イ`, `ウ`など
3. 括弧付きカタカナ: `（ア）`, `（イ）`, `（ウ）`など
4. 二重括弧カタカナ: `（（ア））`, `（（イ））`など
5. アルファベット: `a`, `b`, `c`など
6. 連続していない数字: `３`（`１→３`は非連続）

---

## 7. 統計サマリー

### 変換統計（スクリプト出力）

```
処理したArticle: 13個
分割したArticle: 1個
作成したParagraph: 72個
変換したList: 80個
保持したList: 512個（Item特化処理用）
```

### 実測値との比較

| 項目 | スクリプト統計 | 実測値 | 差異 |
|------|--------------|--------|------|
| Article分割 | 1個 | 1個 | ✅ 一致 |
| 作成したParagraph | 72個 | 73個 | -1個 |
| 変換したList | 80個 | 81個 | -1個 |
| 保持したList | 512個 | 512個 | ✅ 一致 |

**差異の原因（推定）:**
- カウント方法の違い（既存Paragraphの扱い）
- タイミングの問題（統計記録のタイミング）

---

## 8. 結論

### ✅ 正常に動作している部分

1. **Article分割**: `第１` → `第２`の分割が正常に動作
2. **連続番号変換**: `１→２→３→４→５→６`のような連続番号が正しく変換される（Article[8]）
3. **括弧付き数字の除外**: `（１）`, `（２）`などはParagraphに変換されず、Item特化処理用に保持される
4. **List要素の保持**: 512個のList要素が適切に保持され、Column構造も維持される

### ⚠️ 課題

1. **空のParagraphNumの大量作成**: +55個（期待値との差: +49個の一部）
2. **既存Paragraph要素の処理**: 入力XMLの13個のParagraphがどのように扱われているか不明確
3. **List要素の親Paragraph**: 変換されなかったList要素を含むParagraphの扱い

### 📊 精度評価

| 指標 | 期待値 | 実際 | 達成率 |
|------|--------|------|--------|
| Article要素 | 14 | 14 | **100%** ✅ |
| Paragraph要素 | 37 | 86 | **43%** ⚠️ |
| List要素（残存） | 38 | 512 | **7%** 🔄 |

**総合評価:** Article分割と連続番号変換は正常に動作しているが、Paragraph要素の過剰作成が課題。これは主に既存Paragraph要素の処理とList要素の親Paragraphの扱いに起因する。

### 📝 推奨される次のステップ

1. **Item特化処理の実行**: 現在の出力（512個のList要素）をItem要素に変換
2. **統合テスト**: Article特化 → Item特化の連続実行で最終結果を確認
3. **詳細な原因分析**: 必要に応じて、空のParagraphNumが作成される具体的なケースを特定

---

**作成日**: 2025年10月28日  
**分析者**: AI Assistant  
**入力ファイル**: `test_input5.xml` (593個のList要素)  
**出力ファイル**: `test_input5_article_v2.xml` (512個のList要素残存)

