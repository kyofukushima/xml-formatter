# Subitem3修正ロジック（分割と集約）

## 対応スクリプト
`convert_subitem3_focused.py`

## 本文章のスコープ
Subitem3の変換ロジックの第一段階（focused: 分割と集約）について説明する。

**前提**: Subitem2の修正ロジックが完了済みであること。

---

## 基本ロジック

このスクリプトは、`Subitem2`要素内を順番に処理し、まず`Subitem2Sentence`以降の子要素から`Subitem3`を作成し、その後`Subitem3`要素とその弟要素の関係性に基づいて、以下のルールで構造を変換する。

1.  **Subitem3の初期作成**: `Subitem2`要素内に`Subitem3`が存在しない場合、`Subitem2Sentence`以降の子要素から最初の`Subitem3`を作成する。
2.  **Subitem3の分割**: `Subitem3`の弟要素が、その`Subitem3`と**同じ階層レベル**のラベルを持つ`List`要素だった場合、その`List`を新しい`Subitem3`要素に変換する。
3.  **Subitem3への集約**: 上記の条件に当てはまらない全ての弟要素（階層が異なる`List`、`TableStruct`など）は、先行する`Subitem3`要素の**子要素（末尾）**として移動させる。

これにより、`Subitem2`内に散らばった関連要素が、適切な`Subitem3`の配下に集約される。

---

### 処理0: Subitem3の初期作成

#### 条件
- `Subitem2`要素内に、まだ`Subitem3`要素が存在しない状態
- `Subitem2Sentence`以降に子要素が存在する

#### 動作

このスクリプトは、`Subitem2Sentence`以降の最初の子要素の種類に応じて、以下の2つのパターンでSubitem3を作成する。

**パターンA: 2カラムListからの作成**
- 最初の子要素が、`Column`を2つ持つ`List`要素である場合
- 1つ目の`Column`の内容を`Subitem3Title`に設定
- 2つ目の`Column`の内容を`Subitem3Sentence`に設定

**パターンB: 空のSubitem3の作成**
- 最初の子要素が、2カラムList以外（`TableStruct`、`Column`が2つでない`List`等）の場合
- 空の`Subitem3Title`と`Subitem3Sentence`を持つ`Subitem3`を作成
- その要素を、作成した`Subitem3`の子要素として格納

#### 例（パターンA: 2カラムListからの作成）

**入力**
```xml
<Subitem2 Num="1">
  <Subitem2Title>（ア）</Subitem2Title>
  <Subitem2Sentence>
    <Sentence Num="1">基礎的な内容</Sentence>
  </Subitem2Sentence>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>ａ</Sentence></Column>
      <Column Num="2"><Sentence>詳細項目</Sentence></Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">各学校においては...</Sentence>
    </ListSentence>
  </List>
</Subitem2>
```

**出力**
```xml
<Subitem2 Num="1">
  <Subitem2Title>（ア）</Subitem2Title>
  <Subitem2Sentence>
    <Sentence Num="1">基礎的な内容</Sentence>
  </Subitem2Sentence>
  <Subitem3 Num="1">
    <Subitem3Title>ａ</Subitem3Title>
    <Subitem3Sentence>
      <Sentence Num="1">詳細項目</Sentence>
    </Subitem3Sentence>
    <List>
      <ListSentence>
        <Sentence Num="1">各学校においては...</Sentence>
      </ListSentence>
    </List>
  </Subitem3>
</Subitem2>
```

#### 例（パターンB: 空のSubitem3の作成）

**入力**
```xml
<Subitem2 Num="1">
  <Subitem2Title>（ア）</Subitem2Title>
  <Subitem2Sentence>
    <Sentence Num="1">内容</Sentence>
  </Subitem2Sentence>
  <TableStruct>...</TableStruct>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>ａ</Sentence></Column>
      <Column Num="2"><Sentence>詳細項目</Sentence></Column>
    </ListSentence>
  </List>
</Subitem2>
```

**出力**
```xml
<Subitem2 Num="1">
  <Subitem2Title>（ア）</Subitem2Title>
  <Subitem2Sentence>
    <Sentence Num="1">内容</Sentence>
  </Subitem2Sentence>
  <Subitem3 Num="1">
    <Subitem3Title/>
    <Subitem3Sentence>
      <Sentence Num="1"/>
    </Subitem3Sentence>
    <TableStruct>...</TableStruct>
  </Subitem3>
  <Subitem3 Num="2">
    <Subitem3Title>ａ</Subitem3Title>
    <Subitem3Sentence>
      <Sentence Num="1">詳細項目</Sentence>
    </Subitem3Sentence>
  </Subitem3>
</Subitem2>
```

---

### 処理1: Subitem3の分割（同階層のList）

#### 条件
- `Subitem3`の弟要素であること。
- `List`要素であり、`Column`を2つ持っていること。
- 1つ目の`Column`のラベルの階層レベルが、直前の`Subitem3`の`Subitem3Title`の階層レベルと**同じ**であること。

#### 動作
- `List`要素を、新しい`Subitem3`要素に変換する。
- 元の`List`は削除される。

#### 例
**入力**
```xml
<Subitem2 Num="1">
  ...
  <Subitem3 Num="1">
    <Subitem3Title>（ア）</Subitem3Title>
    <Subitem3Sentence>内容１</Subitem3Sentence>
  </Subitem3>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>（イ）</Sentence></Column>
      <Column Num="2"><Sentence>内容２</Sentence></Column>
    </ListSentence>
  </List>
  ...
</Subitem2>
```

**出力**
```xml
<Subitem2 Num="1">
  ...
  <Subitem3 Num="1">
    <Subitem3Title>（ア）</Subitem3Title>
    <Subitem3Sentence>内容１</Subitem3Sentence>
  </Subitem3>
  <Subitem3 Num="2">
    <Subitem3Title>（イ）</Subitem3Title>
    <Subitem3Sentence>内容２</Sentence></Subitem3Sentence>
  </Subitem3>
  ...
</Subitem2>
```

---

### 処理2: Subitem3への集約（上記以外の要素）

#### 条件
- `Subitem3`の弟要素であること。
- 「処理1」の分割条件に当てはまらない、すべての要素。

#### 動作
- その弟要素を、直前の`Subitem3`要素の**末尾に移動**させる。
