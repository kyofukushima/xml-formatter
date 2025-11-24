# Subitem2修正ロジック

## 本文章のスコープ
`Subitem1`要素内部の`List`要素を`Subitem2`へ変換する、新しい特化スクリプト`convert_subitem2.py`のロジックを定義します。

**前提**: `convert_subitem1_focused.py`による`Subitem1`の生成処理が完了していること。入力XMLは、`Subitem1`要素の子要素として、処理対象の`List`やその他の要素がフラットに並んでいる状態であることを想定します。

---

## 処理の概要
各`Subitem1`要素の内部を走査し、`Subitem1Sentence`以降の子要素を、その種類に応じて`Subitem2`に変換、または`Subitem2`の内部に再配置します。

---

### 処理: `column`を持つ`List`要素の階層化

#### 説明
`Subitem1`の子要素である`List`を、`Subitem2`に変換します。これは、`Subitem1`内にネストされるべき階層構造を意味的に表現するためです。

#### 適用条件
- `Subitem1`要素の直下に存在する`List`要素であること。
- その`List`要素が、`ListSentence` > `Column` x 2 の構造を持つこと。
- 1つ目の`Column`がタイトル（例: `（ア）`）、2つ目が本文と見なせるパターンであること。

#### 例
**入力**
```xml
<Subitem1 Num="1">
  <Subitem1Title>ア</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">各教科・科目及び単位数等</Sentence>
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（ア）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">卒業までに履修させる単位数等</Sentence>
      </Column>
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

### 処理詳細
1.  **`Subitem2`への変換**:
    -   `Subitem1`要素内を走査し、適用条件に一致する`List`要素を見つけ、新しい`Subitem2`要素を生成します。
    -   `List`内の1つ目の`Column`の内容を`Subitem2Title`に、2つ目の`Column`の内容を`Subitem2Sentence`にそれぞれ移動します。
2.  **後続要素の内部移動 (ネスト)**:
    -   `Subitem2`に変換された`List`の後続にある要素（`List`, `TableStruct`など）は、次に新しい`Subitem2`が生成されるまで、すべて現在処理中の`Subitem2`の子要素として内部に移動させます。

---
