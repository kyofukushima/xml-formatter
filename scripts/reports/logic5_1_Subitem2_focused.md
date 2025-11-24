# Subitem2修正ロジック（分割と集約）

## 対応スクリプト
`convert_subitem2_focused.py`

## 本文章のスコープ
Subitem2の変換ロジックの第一段階（focused: 分割と集約）について説明する。

**前提**: Subitem1の修正ロジックが完了済みであること。

---

## 基本ロジック

このスクリプトは、`Subitem1`要素内を順番に処理し、まず`Subitem1Sentence`以降の子要素から`Subitem2`を作成し、その後`Subitem2`要素とその弟要素の関係性に基づいて、以下のルールで構造を変換する。

1.  **Subitem2の初期作成**: `Subitem1`要素内に`Subitem2`が存在しない場合、`Subitem1Sentence`以降の子要素から最初の`Subitem2`を作成する。（作成しない例外もある）
2.  **Subitem2の分割**: `Subitem2`の弟要素が、その`Subitem2`と**同じ階層レベル**のラベルを持つ`List`要素だった場合、その`List`を新しい`Subitem2`要素に変換する。
3.  **Subitem2への集約**: 上記の条件に当てはまらない全ての弟要素（階層が異なる`List`、`TableStruct`など）は、先行する`Subitem2`要素の**子要素（末尾）**として移動させる。

これにより、`Subitem1`内に散らばった関連要素が、適切な`Subitem2`の配下に集約される。

---

### 処理0: Subitem2の初期作成

#### 条件
- `Subitem1`要素内に、まだ`Subitem2`要素が存在しない状態
- `Subitem1`要素内のSubitem1Title、Subitem1Sentence>Sentence のいずれかに値が存在する。
- `Subitem1Sentence`以降に子要素が存在する

#### 動作

このスクリプトは、`Subitem1Sentence`以降の最初の子要素の種類に応じて、以下の2つのパターンでSubitem2を作成する。

**パターンA: 2カラムListからの作成**
- 最初の子要素が、`Column`を2つ持つ`List`要素である場合
- 1つ目の`Column`の内容を`Subitem2Title`に設定
- 2つ目の`Column`の内容を`Subitem2Sentence`に設定

**パターンB: 空のSubitem2の作成**
- 最初の子要素が、2カラムList以外（`TableStruct`、`Column`が2つでない`List`等）の場合
- 空の`Subitem2Title`と`Subitem2Sentence`を持つ`Subitem2`を作成
- その要素を、作成した`Subitem2`の子要素として格納

#### 例（パターンA: 2カラムListからの作成）

**入力**
```xml
<Subitem1 Num="1">
  <Subitem1Title>ア</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">各教科・科目及び単位数等</Sentence>
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>（ア）</Sentence></Column>
      <Column Num="2"><Sentence>卒業までに履修させる単位数等</Sentence></Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">各学校においては、卒業までに履修させる...</Sentence>
    </ListSentence>
  </List>
</Subitem1>
```

**出力**
```xml
<Subitem1 Num="1">
  <Subitem1Title>ア</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">各教科・科目及び単位数等</Sentence>
  </Subitem1Sentence>
  <Subitem2 Num="1">
    <Subitem2Title>（ア）</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">卒業までに履修させる単位数等</Sentence>
    </Subitem2Sentence>
    <List>
      <ListSentence>
        <Sentence Num="1">各学校においては、卒業までに履修させる...</Sentence>
      </ListSentence>
    </List>
  </Subitem2>
</Subitem1>
```

#### 例（パターンB: 空のSubitem2の作成）

**入力**
```xml
<Subitem1 Num="1">
  <Subitem1Title>ア</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">内容</Sentence>
  </Subitem1Sentence>
  <TableStruct>...</TableStruct>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>（ア）</Sentence></Column>
      <Column Num="2"><Sentence>サブ内容</Sentence></Column>
    </ListSentence>
  </List>
</Subitem1>
```

**出力**
```xml
<Subitem1 Num="1">
  <Subitem1Title>ア</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">内容</Sentence>
  </Subitem1Sentence>
  <Subitem2 Num="1">
    <Subitem2Title/>
    <Subitem2Sentence>
      <Sentence Num="1"/>
    </Subitem2Sentence>
    <TableStruct>...</TableStruct>
  </Subitem2>
  <Subitem2 Num="2">
    <Subitem2Title>（ア）</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">サブ内容</Sentence>
    </Subitem2Sentence>
  </Subitem2>
</Subitem1>
```

---

### 処理1: Subitem2の分割（同階層のList）

#### 条件
- `Subitem2`の弟要素であること。
- `List`要素であり、`Column`を2つ持っていること。
- 1つ目の`Column`のラベルの階層レベルが、直前の`Subitem2`の`Subitem2Title`の階層レベルと**同じ**であること。

#### 動作
- `List`要素を、新しい`Subitem2`要素に変換する。
- 元の`List`は削除される。

#### 例
**入力**
```xml
<Subitem1 Num="1">
  ...
  <Subitem2 Num="1">
    <Subitem2Title>（ア）</Subitem2Title>
    <Subitem2Sentence>内容１</Subitem2Sentence>
  </Subitem2>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>（イ）</Sentence></Column>
      <Column Num="2"><Sentence>内容２</Sentence></Column>
    </ListSentence>
  </List>
  ...
</Subitem1>
```

**出力**
```xml
<Subitem1 Num="1">
  ...
  <Subitem2 Num="1">
    <Subitem2Title>（ア）</Subitem2Title>
    <Subitem2Sentence>内容１</Subitem2Sentence>
  </Subitem2>
  <Subitem2 Num="2">
    <Subitem2Title>（イ）</Subitem2Title>
    <Subitem2Sentence>内容２</Sentence></Subitem2Sentence>
  </Subitem2>
  ...
</Subitem1>
```

---

### 処理2: Subitem2への集約（上記以外の要素）

#### 条件
- `Subitem2`の弟要素であること。
- 「処理1」の分割条件に当てはまらない、すべての要素。
  - 階層が深い`List`
  - `TableStruct`、`FigStruct`などのその他の要素

#### 動作
- その弟要素を、直前の`Subitem2`要素の**末尾に移動**させる。

#### 例
**入力**
```xml
<Subitem1 Num="1">
  ...
  <Subitem2 Num="1">
    <Subitem2Title>（ア）</Subitem2Title>
    <Subitem2Sentence>内容１</Subitem2Sentence>
  </Subitem2>
  <List> <!-- 階層が深いList -->
    <ListSentence>
      <Column Num="1"><Sentence>ａ</Sentence></Column>
      <Column Num="2"><Sentence>内容２</Sentence></Column>
    </ListSentence>
  </List>
  ...
</Subitem1>
```

**出力**
```xml
<Subitem1 Num="1">
  ...
  <Subitem2 Num="1">
    <Subitem2Title>（ア）</Subitem2Title>
    <Subitem2Sentence>内容１</Subitem2Sentence>
    <List> <!-- 中に移動される -->
      <ListSentence>
        <Column Num="1"><Sentence>ａ</Sentence></Column>
        <Column Num="2"><Sentence>内容２</Sentence></Column>
      </ListSentence>
    </List>
  </Subitem2>
  ...
</Subitem1>
```
