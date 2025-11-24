# Subitem1修正ロジック（テキスト分割）

## 対応スクリプト
`convert_subitem1_textsplit.py`

## 本文章のスコープ
Subitem1の変換ロジックの第二段階（textsplit: テキスト分割）について説明する。

**前提**: Subitem1修正ロジックのステップ１（`convert_subitem1_focused.py`）が完了済みであること。

---

## 基本ロジック

このスクリプトは、`Item`要素内を順番に処理し、`Subitem1`要素内の構造に基づいて、以下のルールで`Subitem1`自体を分割する。

1.  **Subitem1の分割**: `Subitem1`の`Subitem1Title`と`Subitem1Sentence`が空であり、その弟要素として`<Column>`を含まない`List`が存在する場合、その`List`の直後で`Subitem1`を分割する。

---

### 処理1: Subitem1の分割

#### 条件
- `Subitem1`の`Subitem1Title`が空である。
- `Subitem1`の`Subitem1Sentence`が空である。
- `Subitem1`の子要素に、`<Column>`を含まない`List`が存在する。
- その`<Column>`を含まない`List`の弟要素に、`<Column>`を含む`List`や`TableStruct`など、別の構造が存在する。

#### 動作
- `<Column>`を含まない`List`の終わりで`Subitem1`を分割する。
- `<Column>`を含まない`List`が連続する場合は、それらをまとめて最初の`Subitem1`に保持する。
- 分割された後半の要素は、新しい`Subitem1`に格納される。

#### 例
**入力**
```xml
<Subitem1 Num="1">
  <Subitem1Title />
  <Subitem1Sentence>
    <Sentence />
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト1</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">ア</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">サブテキスト1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Subitem1>
```

**出力**
```xml
<Subitem1 Num="1">
  <Subitem1Title />
  <Subitem1Sentence>
    <Sentence />
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト1</Sentence>
    </ListSentence>
  </List>
</Subitem1>
<Subitem1 Num="2">
  <Subitem1Title />
  <Subitem1Sentence>
    <Sentence />
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">ア</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">サブテキスト1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Subitem1>
```

---

### 処理2: Subitem1要素のNum属性の再付与

#### 条件
- `Item`要素内の`Subitem1`要素すべて。

#### 動作
- `Item`要素内での出現順に、`Subitem1`要素の`Num`属性に1からの連番を振り直す。
