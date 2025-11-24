# Item修正ロジック（簡易版）

## 本文章のスコープ
Item特化スクリプト `convert_item_step1_focused.py` の簡易化されたロジックについて説明する。

**前提**: Paragraph修正ロジックが全て完了済みであること。

---

## 基本ロジック

このスクリプトは、`Paragraph`要素内を順番に処理し、`Item`要素とその弟要素の関係性に基づいて、以下の2つのシンプルなルールで構造を変換する。

1.  **Itemの分割**: `Item`の弟要素が、その`Item`と**同じ階層レベル**のラベルを持つ`List`要素だった場合、その`List`を新しい`Item`要素に変換する。
2.  **Itemへの集約**: 上記の条件に当てはまらない全ての弟要素（階層が異なる`List`、`Column`を含まない`List`、`TableStruct`など）は、先行する`Item`要素の**子要素（末尾）**として移動させる。

これにより、`Paragraph`内に散らばった関連要素が、適切な`Item`の配下に集約される。

---

### 処理1: Itemの分割（同階層のList）

#### 条件
- `Item`の弟要素であること。
- `List`要素であり、`Column`を2つ持っていること。
- 1つ目の`Column`のラベルの階層レベルが、直前の`Item`の`ItemTitle`の階層レベルと**同じ**であること。

#### 動作
- `List`要素を、新しい`Item`要素に変換する。
- 元の`List`は削除される。

#### 例
**入力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>項目名１</ItemSentence>
</Item>
<List>
  <ListSentence>
    <Column Num="1"><Sentence>（２）</Sentence></Column>
    <Column Num="2"><Sentence>項目名２</Sentence></Column>
  </ListSentence>
</List>
```

**出力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>項目名１</ItemSentence>
</Item>
<Item Num="2">
  <ItemTitle>（２）</ItemTitle>
  <ItemSentence>項目名２</ItemSentence>
</Item>
```

---

### 処理2: Itemへの集約（上記以外の要素）

#### 条件
- `Item`の弟要素であること。
- 「処理1」の分割条件に当てはまらない、すべての要素。
  - 階層が異なる`List`
  - `Column`を持たない`List`
  - `TableStruct`、`FigStruct`などのその他の要素

#### 動作
- その弟要素を、直前の`Item`要素の**末尾に移動**させる。

#### 例
**入力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>項目名１</ItemSentence>
</Item>
<List> <!-- 階層が深いList -->
  <ListSentence>
    <Column Num="1"><Sentence>ア</Sentence></Column>
    <Column Num="2"><Sentence>項目名２</Sentence></Column>
  </ListSentence>
</List>
<TableStruct>...</TableStruct>
```

**出力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>項目名１</ItemSentence>
  <List> <!-- 中に移動される -->
    <ListSentence>
      <Column Num="1"><Sentence>ア</Sentence></Column>
      <Column Num="2"><Sentence>項目名２</Sentence></Column>
    </ListSentence>
  </List>
  <TableStruct>...</TableStruct> <!-- 中に移動される -->
</Item>
```

---

### 注意事項
この簡易版ロジックでは、`Subitem1`, `Subitem2`などの詳細な階層構造は生成されない。そのロジックは `archived_item_logic.py` および `logic3_1_Item_archive.md` に退避されている。
