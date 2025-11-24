# Subitem1要素変換ロジック仕様書

## 目次

1. [概要](#概要)
2. [処理フロー全体像](#処理フロー全体像)
3. [処理1: ItemSentence直後の要素をSubitem1化](#処理1-itemsentence直後の要素をsubitem1化)
4. [処理2: Subitem1要素の弟要素を順次処理](#処理2-subitem1要素の弟要素を順次処理)
5. [補足事項](#補足事項)

---

## 概要

本仕様書は、Item要素内のList要素をSubitem1要素に変換するロジックを定義する。変換は以下の2段階で実行される：

- **処理1**: ItemSentenceの次の弟要素（最初の1つのみ）をSubitem1要素に変換
- **処理2**: 処理1で生成されたSubitem1要素の弟要素（Item要素内）を順次処理し、Subitem1要素への取り込みまたは分割を実行

処理2でSubitem1要素が分割された場合、新しく生成されたSubitem1要素に対して処理1から再実行される。

---

## 処理フロー全体像

```
Item要素
├─ ItemTitle
├─ ItemSentence
└─ 弟要素（複数）
    ↓
【処理1】最初の弟要素をSubitem1化
    ↓
【処理2】残りの弟要素を順次処理
    ├─ Subitem1取り込み → 既存Subitem1要素の子要素として追加
    └─ Subitem1分割 → 新Subitem1要素を作成
        ↓
        【処理1】から再実行
```

---

## 処理1: ItemSentence直後の要素をSubitem1化

### 目的

Item要素内のItemSentenceの次の弟要素（最初の1つのみ）を、条件に応じてSubitem1要素に変換する。

### 分岐条件

| 分岐 | 条件 | 処理内容 |
|------|------|----------|
| 分岐1 | 弟要素がColumnを含むList要素 | 1つ目のColumnをSubitem1Title、2つ目のColumnをSubitem1Sentenceに設定 |
| 分岐2-1 | （item要素内のTitle要素とItemSentence>Sentence要素の値が空である場合）弟要素がColumnを含まないList要素 | 処理をスキップ |
| 分岐2-2 | 弟要素がColumnを含まないList要素（括弧付き科目名） | 空のSubitem1要素を作成し、Sentenceの値をSubitem1Sentenceに設定 |
| 分岐2-3 | 弟要素がColumnを含まないList要素（括弧付き指導項目） | 空のSubitem1要素を作成し、Sentenceの値をSubitem1Sentenceに設定 |
| 分岐2-4 | 弟要素がColumnを含まないList要素（上記以外） | 空のSubitem1要素を作成し、List要素をSubitem1内に配置 |
| 分岐3 | 弟要素がList要素以外（TableStruct、FigStruct等） | 空のSubitem1要素を作成し、該当要素をSubitem1内に配置 |

### 分岐1: ColumnありList要素

**処理内容**  
弟要素のList要素の1つ目のColumnのSentence要素の値をSubitem1Titleに、2つ目のColumnのSentence要素の値をSubitem1Sentenceに設定する。

**(入力例・出力例は変更なし)**

### 分岐2-1: ColumnなしList要素(item要素が空の場合)

**処理内容**  
処理をスキップし、次のitem要素の処理に移る

**(入力例・出力例は変更なし)**

### 分岐2-2: ColumnなしList要素（括弧付き科目名）

**処理内容**  
空のSubitem1要素を作成し、弟要素のList要素のSentence要素の値をSubitem1Sentenceに設定する。

**入力例**
```xml
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
  </ItemSentence>
  <List>
    <ListSentence>
      <Sentence Num="1">〔科目名A〕</Sentence>
    </ListSentence>
  </List>
</Item>
```

**出力例**
```xml
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title/>
    <Subitem1Sentence>
      <Sentence Num="1">〔科目名A〕</Sentence>
    </Subitem1Sentence>
  </Subitem1>
</Item>
```

### 分岐2-3: ColumnなしList要素（括弧付き指導項目）

**処理内容**  
空のSubitem1要素を作成し、弟要素のList要素のSentence要素の値をSubitem1Sentenceに設定する。

**入力例**
```xml
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
  </ItemSentence>
  <List>
    <ListSentence>
      <Sentence Num="1">〔指導項目〕</Sentence>
    </ListSentence>
  </List>
</Item>
```

**出力例**
```xml
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title/>
    <Subitem1Sentence>
      <Sentence Num="1">〔指導項目〕</Sentence>
    </Subitem1Sentence>
  </Subitem1>
</Item>
```

### 分岐2-4: ColumnなしList要素（上記以外）

**処理内容**  
空のSubitem1要素を作成し、そのSubitem1要素の子要素にList要素として挿入する。

**(入力例・出力例は旧分岐2-1と同じ)**

### 分岐3: List要素以外（TableStruct、FigStruct等）

**(変更なし)**

---

## 処理2: Subitem1要素の弟要素を順次処理

### 目的
(変更なし)

### 分岐条件

| 分岐 | 条件 | 階層判定 | 処理内容 |
|------|------|----------|----------|
| 分岐1-1 | ColumnありList要素 | 同階層 | Subitem1分割 |
| 分岐1-2 | ColumnありList要素 | 異なる階層 | Subitem1取り込み |
| 分岐2-1 | ColumnなしList要素（通常テキスト） | - | Subitem1取り込み |
| 分岐2-2 | ColumnなしList要素（括弧付き科目名） | 同階層 | Subitem1分割 |
| 分岐2-3 | ColumnなしList要素（括弧付き指導項目） | 同階層 | Subitem1分割 |
| 分岐3 | List要素以外（TableStruct、FigStruct等） | - | Subitem1取り込み |

### 分岐1-1, 1-2, 2-1, 3
**(変更なし)**

### 分岐2-2: 括弧付き科目名で同階層（Subitem1分割）

**処理内容**  
既存Subitem1のSubitem1Sentenceの値と、弟要素のSentenceの値を比較し、同階層の項目ラベルと判定された場合（両方とも括弧付き科目名）、Subitem1要素を分割する。

**入力例**
```xml
<Item Num="1">
  <ItemTitle/>
  <ItemSentence>
    <Sentence Num="1"/>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title/>
    <Subitem1Sentence>
      <Sentence Num="1">〔科目名A〕</Sentence>
    </Subitem1Sentence>
  </Subitem1>
  <List>
    <ListSentence>
      <Sentence Num="1">〔科目名B〕</Sentence>
    </ListSentence>
  </List>
</Item>
```

**出力例**
```xml
<Item Num="1">
  <ItemTitle/>
  <ItemSentence>
    <Sentence Num="1"/>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title/>
    <Subitem1Sentence>
      <Sentence Num="1">〔科目名A〕</Sentence>
    </Subitem1Sentence>
  </Subitem1>
  <Subitem1 Num="2">
    <Subitem1Title/>
    <Subitem1Sentence>
      <Sentence Num="1">〔科目名B〕</Sentence>
    </Subitem1Sentence>
  </Subitem1>
</Item>
```

### 分岐2-3: 括弧付き指導項目で同階層（Subitem1分割）

**処理内容**  
既存Subitem1のSubitem1Sentenceの値と、弟要素のSentenceの値を比較し、同階層の項目ラベルと判定された場合（両方とも括弧付き指導項目）、Subitem1要素を分割する。

**(入力例・出力例は分岐2-2に準ずる)**

---

## 補足事項

### 用語定義

#### 空のSubitem1要素
(変更なし)

#### 括弧付き科目名
- `〔...〕`または`【...】`で囲まれたテキスト
- 例: `〔科目名A〕`、`【数学】`
- `指導項目`という文字列を含まない

#### 括弧付き指導項目
- `〔指導項目〕`または`【指導項目】`という完全一致のテキスト

### 階層判定の基準
(変更なし)

### 処理の繰り返し
(変更なし)

### 実装上の注意点
(変更なし)

---

**更新履歴**
- 2025年11月8日: 括弧付き科目名・指導項目の分岐を追加
- 2025年11月8日: 初版作成
