# Subitem2要素変換ロジック仕様書

## 目次

1. [概要](#概要)
2. [処理フロー全体像](#処理フロー全体像)
3. [処理1: Subitem1Sentence直後の要素をSubitem2化](#処理1-subitem1sentence直後の要素をsubitem2化)
4. [処理2: Subitem2要素の弟要素を順次処理](#処理2-subitem2要素の弟要素を順次処理)
5. [補足事項](#補足事項)

---

## 概要

本仕様書は、Subitem1要素内のList要素をSubitem2要素に変換するロジックを定義する。変換は以下の2段階で実行される：

- **処理1**: Subitem1Sentenceの次の弟要素（最初の1つのみ）をSubitem2要素に変換
- **処理2**: 処理1で生成されたSubitem2要素の弟要素（Subitem1要素内）を順次処理し、Subitem2要素への取り込みまたは分割を実行

処理2でSubitem2要素が分割された場合、新しく生成されたSubitem2要素に対して処理1から再実行される。

---

## 処理フロー全体像

```
Subitem1要素
├─ Subitem1Title
├─ Subitem1Sentence
└─ 弟要素（複数）
    ↓
【処理1】最初の弟要素をSubitem2化
    ↓
【処理2】残りの弟要素を順次処理
    ├─ Subitem2取り込み → 既存Subitem2要素の子要素として追加
    └─ Subitem2分割 → 新Subitem2要素を作成
        ↓
        【処理1】から再実行
```

---

## 処理1: Subitem1Sentence直後の要素をSubitem2化

### 目的

Subitem1要素内のSubitem1Sentenceの次の弟要素（最初の1つのみ）を、条件に応じてSubitem2要素に変換する。

### 分岐条件

| 分岐 | 条件 | 処理内容 |
|------|------|----------|
| 分岐1 | 弟要素がColumnを含むList要素 | 1つ目のColumnをSubitem2Title、2つ目のColumnをSubitem2Sentenceに設定 |
| 分岐2-1 | （subitem1要素内のTitle要素とSubitem1Sentence>Sentence要素の値が空である場合）弟要素がColumnを含まないList要素 | 処理をスキップ |
| 分岐2-2 | 弟要素がColumnを含まないList要素（括弧付き科目名） | 空のSubitem2要素を作成し、Sentenceの値をSubitem2Sentenceに設定 |
| 分岐2-3 | 弟要素がColumnを含まないList要素（括弧付き指導項目） | 空のSubitem2要素を作成し、Sentenceの値をSubitem2Sentenceに設定 |
| 分岐2-4 | 弟要素がColumnを含まないList要素（上記以外） | 空のSubitem2要素を作成し、List要素をSubitem2内に配置 |
| 分岐3 | 弟要素がList要素以外（TableStruct、FigStruct等） | 空のSubitem2要素を作成し、該当要素をSubitem2内に配置 |

### 分岐1: ColumnありList要素

**処理内容**  
弟要素のList要素の1つ目のColumnのSentence要素の値をSubitem2Titleに、2つ目のColumnのSentence要素の値をSubitem2Sentenceに設定する。

**入力例**
```xml
<Subitem1 Num="1">
  <Subitem1Title>（１）</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">ア</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">さらに下位の項目名1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Subitem1>
```

**出力例**
```xml
<Subitem1 Num="1">
  <Subitem1Title>（１）</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem1Sentence>
  <Subitem2 Num="1">
    <Subitem2Title>ア</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">さらに下位の項目名1</Sentence>
    </Subitem2Sentence>
  </Subitem2>
</Subitem1>
```

### 分岐2-1: ColumnなしList要素(subitem1要素が空の場合)

**処理内容**  
処理をスキップし、次のsubitem1要素の処理に移る

**入力例**
```xml
<Subitem1 Num="1">
  <Subitem1Title></Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1"></Sentence>
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Sentence Num="1">弟要素のList要素の1つ目のテキスト</Sentence>
    </ListSentence>
  </List>
</Subitem1>
```

**出力例**
```xml
<Subitem1 Num="1">
  <Subitem1Title></Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1"></Sentence>
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Sentence Num="1">弟要素のList要素の1つ目のテキスト</Sentence>
    </ListSentence>
  </List>
</Subitem1>
```

### 分岐2-2: ColumnなしList要素（括弧付き科目名）

**処理内容**  
空のSubitem2要素を作成し、弟要素のList要素のSentence要素の値をSubitem2Sentenceに設定する。

**入力例**
```xml
<Subitem1 Num="1">
  <Subitem1Title>（１）</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Sentence Num="1">〔科目名A〕</Sentence>
    </ListSentence>
  </List>
</Subitem1>
```

**出力例**
```xml
<Subitem1 Num="1">
  <Subitem1Title>（１）</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem1Sentence>
  <Subitem2 Num="1">
    <Subitem2Title/>
    <Subitem2Sentence>
      <Sentence Num="1">〔科目名A〕</Sentence>
    </Subitem2Sentence>
  </Subitem2>
</Subitem1>
```

### 分岐2-3: ColumnなしList要素（括弧付き指導項目）

**処理内容**  
空のSubitem2要素を作成し、弟要素のList要素のSentence要素の値をSubitem2Sentenceに設定する。

**入力例**
```xml
<Subitem1 Num="1">
  <Subitem1Title>（１）</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Sentence Num="1">〔指導項目〕</Sentence>
    </ListSentence>
  </List>
</Subitem1>
```

**出力例**
```xml
<Subitem1 Num="1">
  <Subitem1Title>（１）</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem1Sentence>
  <Subitem2 Num="1">
    <Subitem2Title/>
    <Subitem2Sentence>
      <Sentence Num="1">〔指導項目〕</Sentence>
    </Subitem2Sentence>
  </Subitem2>
</Subitem1>
```

### 分岐2-4: ColumnなしList要素（上記以外）

**処理内容**  
空のSubitem2要素を作成し、そのSubitem2要素の子要素にList要素として挿入する。

**入力例**
```xml
<Subitem1 Num="1">
  <Subitem1Title>（１）</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Sentence Num="1">弟要素のList要素の1つ目のテキスト</Sentence>
    </ListSentence>
  </List>
</Subitem1>
```

**出力例**
```xml
<Subitem1 Num="1">
  <Subitem1Title>（１）</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem1Sentence>
  <Subitem2 Num="1">
    <Subitem2Title/>
    <Subitem2Sentence>
      <Sentence Num="1"></Sentence>
    </Subitem2Sentence>
    <List>
      <ListSentence>
        <Sentence Num="1">弟要素のList要素の1つ目のテキスト</Sentence>
      </ListSentence>
    </List>
  </Subitem2>
</Subitem1>
```

### 分岐3: List要素以外（TableStruct、FigStruct等）

**処理内容**  
空のSubitem2要素を作成し、そのSubitem2要素の子要素として挿入する。

**入力例**
```xml
<Subitem1 Num="1">
  <Subitem1Title>（１）</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem1Sentence>
  <TableStruct>
    ...
  </TableStruct>
</Subitem1>
```

**出力例**
```xml
<Subitem1 Num="1">
  <Subitem1Title>（１）</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem1Sentence>
  <Subitem2 Num="1">
    <Subitem2Title/>
    <Subitem2Sentence>
      <Sentence Num="1"></Sentence>
    </Subitem2Sentence>
    <TableStruct>
      ...
    </TableStruct>
  </Subitem2>
</Subitem1>
```

---

## 処理2: Subitem2要素の弟要素を順次処理

### 分岐条件

| 分岐 | 条件 | 階層判定 | 処理内容 |
|------|------|----------|----------|
| 分岐1-1 | ColumnありList要素 | 同階層 | Subitem2分割 |
| 分岐1-2 | ColumnありList要素 | 異なる階層 | Subitem2取り込み |
| 分岐2-1 | ColumnなしList要素（通常テキスト） | - | Subitem2取り込み |
| 分岐2-2 | ColumnなしList要素（括弧付き科目名） | 同階層 | Subitem2分割 |
| 分岐2-3 | ColumnなしList要素（括弧付き指導項目） | 同階層 | Subitem2分割 |
| 分岐3 | List要素以外（TableStruct、FigStruct等） | - | Subitem2取り込み |

### 分岐1-1: ColumnありList要素で同階層（Subitem2分割）

**入力例**
```xml
<Subitem1 Num="1">
  ...
  <Subitem2 Num="1">
    <Subitem2Title>ア</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">さらに下位の項目名1</Sentence>
    </Subitem2Sentence>
  </Subitem2>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">イ</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">さらに下位の項目名2</Sentence>
      </Column>
    </ListSentence>
  </List>
</Subitem1>
```

**出力例**
```xml
<Subitem1 Num="1">
  ...
  <Subitem2 Num="1">
    <Subitem2Title>ア</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">さらに下位の項目名1</Sentence>
    </Subitem2Sentence>
  </Subitem2>
  <Subitem2 Num="2">
    <Subitem2Title>イ</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">さらに下位の項目名2</Sentence>
    </Subitem2Sentence>
  </Subitem2>
</Subitem1>
```

### 分岐1-2: ColumnありList要素で異なる階層（Subitem2取り込み）

**入力例**
```xml
<Subitem1 Num="1">
  ...
  <Subitem2 Num="1">
    <Subitem2Title>ア</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">さらに下位の項目名1</Sentence>
    </Subitem2Sentence>
  </Subitem2>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（ア）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">もっと下の項目</Sentence>
      </Column>
    </ListSentence>
  </List>
</Subitem1>
```

**出力例**
```xml
<Subitem1 Num="1">
  ...
  <Subitem2 Num="1">
    <Subitem2Title>ア</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">さらに下位の項目名1</Sentence>
    </Subitem2Sentence>
    <List>
      <ListSentence>
        <Column Num="1">
          <Sentence Num="1">（ア）</Sentence>
        </Column>
        <Column Num="2">
          <Sentence Num="1">もっと下の項目</Sentence>
        </Column>
      </ListSentence>
    </List>
  </Subitem2>
</Subitem1>
```

### 分岐2-1: ColumnなしList要素でSubitem2取り込み

**入力例**
```xml
<Subitem1 Num="1">
  ...
  <Subitem2 Num="1">
    <Subitem2Title>ア</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">さらに下位の項目名1</Sentence>
    </Subitem2Sentence>
  </Subitem2>
  <List>
    <ListSentence>
      <Sentence Num="1">説明テキスト</Sentence>
    </ListSentence>
  </List>
</Subitem1>
```

**出力例**
```xml
<Subitem1 Num="1">
  ...
  <Subitem2 Num="1">
    <Subitem2Title>ア</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">さらに下位の項目名1</Sentence>
    </Subitem2Sentence>
    <List>
      <ListSentence>
        <Sentence Num="1">説明テキスト</Sentence>
      </ListSentence>
    </List>
  </Subitem2>
</Subitem1>
```

---

## 補足事項

### 用語定義

#### 空のSubitem2要素
以下の構造を持つSubitem2要素を指す：
```xml
<Subitem2 Num="1">
  <Subitem2Title/>
  <Subitem2Sentence>
    <Sentence Num="1"></Sentence>
  </Subitem2Sentence>
</Subitem2>
```

#### 括弧付き科目名
- `〔...〕`または`【...】`で囲まれたテキスト
- 例: `〔科目名A〕`、`【数学】`
- `指導項目`という文字列を含まない

#### 括弧付き指導項目
- `〔指導項目〕`または`【指導項目】`という完全一致のテキスト

### 階層判定の基準

項目ラベルの種類（形式）で階層を判定する。

- **Itemレベル**: `１`、`２`
- **Subitem1レベル**: `（１）`、`(1)`、`ア`、`イ`
- **Subitem2レベル**: `(ア)`、`(イ)`、`ａ`、`ｂ`
- **Subitem3レベル**: `①`、`②`

同じ種類のラベルは同階層と判定される。

---

**更新履歴**
- 2025年11月8日: XML例を追記し、完全版として更新
- 2025年11月8日: Subitem1をベースにSubitem2用として作成