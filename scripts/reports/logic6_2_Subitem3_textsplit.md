# Subitem3修正ロジック（テキスト分割）

## 対応スクリプト
`convert_subitem3_textsplit.py`

## 本文章のスコープ
Subitem3の変換ロジックの第二段階（textsplit: テキスト分割）について説明する。

**前提**: Subitem3の修正ロジックのステップ１（`convert_subitem3_focused.py`）が完了済みであること。

---

## 基本ロジック

このスクリプトは、`Subitem2`要素内を順番に処理し、`Subitem3`要素内の構造に基づいて、以下のルールで`Subitem3`自体を分割する。

1.  **Subitem3の分割**: `Subitem3`の`Subitem3Title`と`Subitem3Sentence`が空であり、その子要素として`<Column>`を含まない`List`が存在し、さらにその後に別の要素が続く場合に、`Subitem3`を分割する。

---

### 処理1: Subitem3の分割

#### 条件
- `Subitem3`の`Subitem3Title`が空である。
- `Subitem3`の`Subitem3Sentence`が空である。
- `Subitem3`の子要素に、`<Column>`を含まない`List`が存在する。
- その`<Column>`を含まない`List`の弟要素に、`<Column>`を含む`List`や`TableStruct`など、別の構造が存在する。

#### 動作
- `<Column>`を含まない`List`の終わりで`Subitem3`を分割する。
- 分割された後半の要素は、新しい`Subitem3`に格納される。

#### 例
**入力**
```xml
<Subitem3 Num="1">
  <Subitem3Title />
  <Subitem3Sentence>
    <Sentence />
  </Subitem3Sentence>
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
</Subitem3>
```

**出力**
```xml
<Subitem3 Num="1">
  <Subitem3Title />
  <Subitem3Sentence>
    <Sentence />
  </Subitem3Sentence>
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト1</Sentence>
    </ListSentence>
  </List>
</Subitem3>
<Subitem3 Num="2">
  <Subitem3Title />
  <Subitem3Sentence>
    <Sentence />
  </Subitem3Sentence>
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
</Subitem3>
```

---

### 処理2: Subitem3要素のNum属性の再付与

#### 条件
- `Subitem2`要素内の`Subitem3`要素すべて。

#### 動作
- `Subitem2`要素内での出現順に、`Subitem3`要素の`Num`属性に1からの連番を振り直す。
