# Item修正ロジック（簡易版）

## 本文章のスコープ
Item特化スクリプトにおける、2つ目の分割ロジックについて説明する。

**前提**: item修正ロジックのステップ１`convert_item_step1_focused.py`まで全て完了済みであること。

---

## 基本ロジック

このスクリプトは、`Paragraph`要素内を順番に処理し、`Item`要素の構造に基づいて、以下のルールで`Item`を分割する。

1.  **Itemの分割**: `Item`の`ItemTitle`と`ItemSentence`が空であり、その弟要素に`Column`を含まない`List`が存在する場合、その`List`の終わりで`Item`要素を分割する。`Column`を含まない`List`が連続する場合は、まとめて最初の`Item`に保持する。

---

### 処理1: Itemの分割

#### 条件
- `Item`の要素内のItemtitleの値が空
- ItemSentence要素内のSentence要素が空
- Itemsentence要素の弟要素が、`Column`を含まない`List`

#### 動作
- `List`要素の終わりでItem要素を分割する。`Column`を含まない`List`が連続する場合は、まとめて取り込む
- 元の`List`は削除される。
- 以下のいずれかに到達したら、分割を終了する
  - `Column`を含まない`List`であって、Sentenceの値が〔指導項目〕など、カッコ付きのラベル項目
  - Item要素の終わり
  - `Column`を含む`List`


#### 例
**入力**
```xml
<Item Num="1">
  <ItemTitle />
  <ItemSentence>
    <Sentence />
  </ItemSentence>
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト1</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（１）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">サブテキスト1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Item>
```

**出力**

```xml
<Item Num="1">
  <ItemTitle />
  <ItemSentence>
    <Sentence />
  </ItemSentence>
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト1</Sentence>
    </ListSentence>
  </List>
  </Item>
  <Item Num="">
  <ItemTitle />
  <ItemSentence>
    <Sentence />
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（１）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">サブテキスト1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Item>
```





### 処理x: Item要素のNum属性の再度付与

#### 条件
Item要素

#### 動作
- Paragraph要素内での出現順に、Item要素のNum属性に、1からの連番を振る。既存の値は無視する。

#### 例
**入力**
```xml
<Item Num="1">
  <ItemTitle></ItemTitle>
  <ItemSentence></ItemSentence>
</Item>
<Item Num="1">
  <ItemTitle></ItemTitle>
  <ItemSentence></ItemSentence>
</Item>
<Item Num="2">
  <ItemTitle></ItemTitle>
  <ItemSentence></ItemSentence>
</Item>
```

**出力**
```xml
<Item Num="1">
  <ItemTitle></ItemTitle>
  <ItemSentence></ItemSentence>
</Item>
<Item Num="2">
  <ItemTitle></ItemTitle>
  <ItemSentence></ItemSentence>
</Item>
<Item Num="3">
  <ItemTitle></ItemTitle>
  <ItemSentence></ItemSentence>
</Item>
```

---
