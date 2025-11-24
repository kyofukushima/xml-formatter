# Subitem1修正ロジック（分割と集約）

## 対応スクリプト
`convert_subitem1_focused.py`

## 本文章のスコープ
Subitem1の変換ロジックの第一段階（focused: 分割と集約）について説明する。

**前提**: ItemおよびParagraphの修正ロジックが完了済みであること。

---

## 基本ロジック

このスクリプトは、`Item`要素内を順番に処理し、まず`ItemSentence`以降の子要素から`Subitem1`を作成し、その後`Subitem1`要素とその弟要素の関係性に基づいて、以下のルールで構造を変換する。

1.  **Subitem1の初期作成**: `Item`要素内に`Subitem1`が存在しない場合、`ItemSentence`以降の子要素から最初の`Subitem1`を作成する。
2.  **Subitem1の分割**: `Subitem1`の弟要素が、その`Subitem1`と**同じ階層レベル**のラベルを持つ`List`要素だった場合、その`List`を新しい`Subitem1`要素に変換する。
3.  **Subitem1への集約**: 上記の条件に当てはまらない全ての弟要素（階層が異なる`List`、`TableStruct`など）は、先行する`Subitem1`要素の**子要素（末尾）**として移動させる。

これにより、`Item`内に散らばった関連要素が、適切な`Subitem1`の配下に集約される。

---

### 処理0: Subitem1の初期作成

#### 条件
- `Item`要素内に、まだ`Subitem1`要素が存在しない状態
- `ItemSentence`以降に子要素が存在する

#### 動作

このスクリプトは、`ItemSentence`以降の最初の子要素の種類に応じて、以下の2つのパターンでSubitem1を作成する。

**パターンA: 2カラムListからの作成**
- 最初の子要素が、`Column`を2つ持つ`List`要素である場合
- 1つ目の`Column`の内容を`Subitem1Title`に設定
- 2つ目の`Column`の内容を`Subitem1Sentence`に設定

**パターンB: 空のSubitem1の作成**
- 最初の子要素が、2カラムList以外（`TableStruct`、`Column`が2つでない`List`等）の場合
- 空の`Subitem1Title`と`Subitem1Sentence`を持つ`Subitem1`を作成
- その要素を、作成した`Subitem1`の子要素として格納

#### 例（パターンA: 2カラムListからの作成）

**入力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">教育課程の編成</Sentence>
  </ItemSentence>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>ア</Sentence></Column>
      <Column Num="2"><Sentence>各教科・科目及び単位数等</Sentence></Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">各学校においては、次の事項を踏まえて...</Sentence>
    </ListSentence>
  </List>
</Item>
```

**出力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">教育課程の編成</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence>
      <Sentence Num="1">各教科・科目及び単位数等</Sentence>
    </Subitem1Sentence>
    <List>
      <ListSentence>
        <Sentence Num="1">各学校においては、次の事項を踏まえて...</Sentence>
      </ListSentence>
    </List>
  </Subitem1>
</Item>
```

#### 例（パターンB: 空のSubitem1の作成）

**入力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">内容</Sentence>
  </ItemSentence>
  <TableStruct>...</TableStruct>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>ア</Sentence></Column>
      <Column Num="2"><Sentence>サブ内容</Sentence></Column>
    </ListSentence>
  </List>
</Item>
```

**出力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">内容</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title/>
    <Subitem1Sentence>
      <Sentence Num="1"/>
    </Subitem1Sentence>
    <TableStruct>...</TableStruct>
  </Subitem1>
  <Subitem1 Num="2">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence>
      <Sentence Num="1">サブ内容</Sentence>
    </Subitem1Sentence>
  </Subitem1>
</Item>
```

---

### 処理1: Subitem1の分割（同階層のList）

#### 条件
- `Subitem1`の弟要素であること。
- `List`要素であり、`Column`を2つ持っていること。
- 1つ目の`Column`のラベルの階層レベルが、直前の`Subitem1`の`Subitem1Title`の階層レベルと**同じ**であること。

#### 動作
- `List`要素を、新しい`Subitem1`要素に変換する。
- 元の`List`は削除される。

#### 例
**入力**
```xml
<Item Num="1">
  ...
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence>内容１</Subitem1Sentence>
  </Subitem1>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>イ</Sentence></Column>
      <Column Num="2"><Sentence>内容２</Sentence></Column>
    </ListSentence>
  </List>
  ...
</Item>
```

**出力**
```xml
<Item Num="1">
  ...
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence>内容１</Subitem1Sentence>
  </Subitem1>
  <Subitem1 Num="2">
    <Subitem1Title>イ</Subitem1Title>
    <Subitem1Sentence>内容２</Sentence></Subitem1Sentence>
  </Subitem1>
  ...
</Item>
```

---

### 処理2: Subitem1への集約（上記以外の要素）

#### 条件
- `Subitem1`の弟要素であること。
- 「処理1」の分割条件に当てはまらない、すべての要素。
  - 階層が深い`List`
  - `TableStruct`、`FigStruct`などのその他の要素

#### 動作
- その弟要素を、直前の`Subitem1`要素の**末尾に移動**させる。

#### 例
**入力**
```xml
<Item Num="1">
  ...
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence>内容１</Subitem1Sentence>
  </Subitem1>
  <List> <!-- 階層が深いList -->
    <ListSentence>
      <Column Num="1"><Sentence>（ア）</Sentence></Column>
      <Column Num="2"><Sentence>内容２</Sentence></Column>
    </ListSentence>
  </List>
  <TableStruct>...</TableStruct>
  ...
</Item>
```

**出力**
```xml
<Item Num="1">
  ...
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence>内容１</Subitem1Sentence>
    <List> <!-- 中に移動される -->
      <ListSentence>
        <Column Num="1"><Sentence>（ア）</Sentence></Column>
        <Column Num="2"><Sentence>内容２</Sentence></Column>
      </ListSentence>
    </List>
    <TableStruct>...</TableStruct> <!-- 中に移動される -->
  </Subitem1>
  ...
</Item>
```
