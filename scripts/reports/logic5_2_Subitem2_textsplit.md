# Subitem2修正ロジック（テキスト分割）

## 対応スクリプト
`convert_subitem2_textsplit.py`

## 本文章のスコープ
Subitem2の変換ロジックの第二段階（textsplit: テキスト分割）について説明する。

**前提**: Subitem2修正ロジックのステップ１（`convert_subitem2_focused.py`）が完了済みであること。

---

## 基本ロジック

このスクリプトは、`Subitem1`要素内を順番に処理し、`Subitem2`要素内の構造に基づいて、以下のルールで`Subitem2`自体を分割する。

1.  **Subitem2の分割**: `Subitem2`の`Subitem2Title`と`Subitem2Sentence`が空であり、その弟要素として`<Column>`を含まない`List`が存在する場合、その`List`の直後で`Subitem2`を分割する。

---

### 処理1: Subitem2の分割

#### 条件
- `Subitem2`の`Subitem2Title`が空である。
- `Subitem2`の`Subitem2Sentence`が空である。
- `Subitem2`の子要素に、`<Column>`を含まない`List`が存在する。
- その`<Column>`を含まない`List`の弟要素に、`<Column>`を含む`List`や`TableStruct`など、別の構造が存在する。

#### 動作
- `<Column>`を含まない`List`の終わりで`Subitem2`を分割する。
- `<Column>`を含まない`List`が連続する場合は、それらをまとめて最初の`Subitem2`に保持する。
- 分割された後半の要素は、新しい`Subitem2`に格納される。

#### 例
**入力**
```xml
<Subitem2 Num="1">
  <Subitem2Title />
  <Subitem2Sentence>
    <Sentence />
  </Subitem2Sentence>
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト1</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（ア）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">サブテキスト1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Subitem2>
```

**出力**
```xml
<Subitem2 Num="1">
  <Subitem2Title />
  <Subitem2Sentence>
    <Sentence />
  </Subitem2Sentence>
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト1</Sentence>
    </ListSentence>
  </List>
</Subitem2>
<Subitem2 Num="2">
  <Subitem2Title />
  <Subitem2Sentence>
    <Sentence />
  </Subitem2Sentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（ア）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">サブテキスト1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Subitem2>
```

---

### 処理2: Subitem2要素のNum属性の再付与

#### 条件
- `Subitem1`要素内の`Subitem2`要素すべて。

#### 動作
- `Subitem1`要素内での出現順に、`Subitem2`要素の`Num`属性に1からの連番を振り直す。
