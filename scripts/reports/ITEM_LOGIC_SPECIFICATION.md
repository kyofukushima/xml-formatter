# Item要素変換ロジック仕様書

## 目次

1. [概要](#概要)
2. [処理フロー全体像](#処理フロー全体像)
3. [処理1: ParagraphSentence直後の要素をItem化](#処理1-paragraphsentence直後の要素をitem化)
4. [処理2: Item要素の弟要素を順次処理](#処理2-item要素の弟要素を順次処理)
5. [補足事項](#補足事項)

---

## 概要

本仕様書は、Paragraph要素内のList要素をItem要素に変換するロジックを定義する。変換は以下の2段階で実行される：

- **処理1**: ParagraphSentenceの次の弟要素（最初の1つのみ）をItem要素に変換
- **処理2**: 処理1で生成されたItem要素の弟要素（Paragraph要素内）を順次処理し、Item要素への取り込みまたは分割を実行
- **処理3**: 特殊な分割を実行

処理2でItem要素が分割された場合、新しく生成されたItem要素に対して処理1から再実行される。

---

## 処理フロー全体像

`convert_item_step0.py`は、`Paragraph`要素を1つずつ処理する。各`Paragraph`内では、`ParagraphSentence`の直後から末尾までの弟要素（`List`, `TableStruct`など）を対象に、**処理モード**に基づいて`Item`要素への変換・集約を行う。

### 処理モードの概念

`Paragraph`内の最初の`List`要素の種類によって、その後の要素の扱い方を決定する「モード」を導入する。これにより、単純なリストだけでなく、複数のリストを一つの項目にまとめる複雑なパターン（パターン3, 5）にも対応する。

| モード | 状態 | 移行条件 | 処理内容 |
| :--- | :--- | :--- | :--- |
| `LOOKING_FOR_FIRST_ITEM` | **初期状態** | `Paragraph`の処理開始時 | 最初の`List`要素を待つ。 |
| `AGGREGATING_INTO_CONTAINER` | **コンテナ集約モード** | 最初の`List`が**Columnなし**の場合 | 空のコンテナ`Item`を1つだけ作成し、後続の`List`要素をすべてその中に取り込む。 |
| `NORMAL_PROCESSING` | **通常処理モード** | 最初の`List`が**Columnあり**の場合 | 従来通り、`List`要素ごとに`are_same_hierarchy`関数で階層を比較し、`Item`の取り込み・分割を判断する。 |

---

## Paragraph内要素の処理詳細

`Paragraph`ごとに、`ParagraphSentence`以降の弟要素を走査する際の具体的な処理の流れを以下に示す。

### Step 1: 処理モードの決定（最初の弟要素の処理）

`ParagraphSentence`の直後にある**最初の弟要素**の種類によって、処理モードが決定される。

1.  **弟要素が「ColumnなしList」の場合（パターン3, 5）**
    1.  処理モードを `AGGREGATING_INTO_CONTAINER` に設定する。
    2.  **空のコンテナ`Item`** を1つ作成し、`Paragraph`に追加する。
    3.  この`List`要素を、作成したコンテナ`Item`の子要素として挿入する。
    4.  以降の弟要素は、Step 2の`AGGREGATING_INTO_CONTAINER`モードで処理される。

    **入力例（パターン3, 5の起点）**
    ```xml
    <Paragraph Num="1">
      <ParagraphNum/>
      <ParagraphSentence>...</ParagraphSentence>
      <List>
        <ListSentence>
          <Sentence Num="1">これはColumnなしListです。</Sentence>
        </ListSentence>
      </List>
      <List>
        <ListSentence>
          <Column Num="1">
            <Sentence>（１）</Sentence>
          </Column>
          ...
        </ListSentence>
      </List>
      ...
    </Paragraph>
    ```

    **このステップでの出力**
    ```xml
    <Paragraph Num="1">
       <ParagraphNum/>
      <ParagraphSentence>...</ParagraphSentence>
      <Item Num="1">
        <ItemTitle/>
          <ItemSentence Num="1">
            <Sentence Num="1"></Sentence>
          </ItemSentence>
        <List>
          <ListSentence>
            <Sentence>これはColumnなしListです。</Sentence>
          </ListSentence>
        </List>
      </Item>
      <!-- ↓後続のListは次のステップで処理される -->
      <List>
        <ListSentence>
          <Column Num="1">
            <Sentence>（１）</Sentence>
            </Column>
            ...
        </ListSentence>
      </List>
      ...
    </Paragraph>
    ```

2.  **弟要素が「ColumnありList」の場合**
    1.  処理モードを `NORMAL_PROCESSING` に設定する。
    2.  この`List`要素を新しい`Item`要素に変換する。
        - `Column[1]` を `ItemTitle` に変換。
        - `Column[2]` を `ItemSentence` に変換。
    3.  以降の弟要素は、Step 2の`NORMAL_PROCESSING`モードで処理される。

3.  **弟要素が`List`以外（`TableStruct`など）の場合**
    1.  処理モードを `AGGREGATING_INTO_CONTAINER` に設定する（ColumnなしListと同様の扱い）。
    2.  空のコンテナ`Item`を1つ作成し、この要素をその中に格納する。

### Step 2: 後続の弟要素の処理

最初の弟要素の処理後、決定された処理モードに基づいて残りの弟要素を処理する。

1.  **`AGGREGATING_INTO_CONTAINER` モードの場合**
    -   後続の弟要素が`List`であろうと`TableStruct`であろうと、**すべてをStep 1で作成した単一のコンテナ`Item`の中に、順番にそのまま追加していく。**
    -   このモードでは、`Item`の分割は一切発生しない（ただし、後続の処理3で分割される可能性はある）。

    **最終的な出力例（パターン3, 5）**
    ```xml
    <Paragraph Num="1">
      <ParagraphNum/>
      <ParagraphSentence>...</ParagraphSentence>
      <Item Num="1">
        <ItemTitle/>
        <ItemSentence Num="1"><Sentence Num="1"></Sentence></ItemSentence>
        <List>
          <ListSentence><Sentence>これはColumnなしListです。</Sentence></ListSentence>
        </List>
        <List>
          <ListSentence><Column Num="1"><Sentence>（１）</Sentence></Column>...</ListSentence>
        </List>
        <List>
          <ListSentence><Column Num="1"><Sentence>（２）</Sentence></Column>...</ListSentence>
        </List>
      </Item>
    </Paragraph>
    ```
    > この構造は、後続の`convert_subitem1_step0.py`などのスクリプトによって、さらに`Subitem1`などに変換されることを想定している。

2.  **`NORMAL_PROCESSING` モードの場合**
    -   後続の弟要素（`List`）が見つかるたびに、`are_same_hierarchy`関数を呼び出し、直前の`Item`との階層関係を比較する。
    -   **`are_same_hierarchy`が`False`（下位階層・同一階層の継続）を返した場合:**
        -   その`List`要素を、直前の`Item`の子要素として**取り込む**。
    -   **`are_same_hierarchy`が`True`（同階層への分割・上位階層への復帰）を返した場合:**
        -   新しい`Item`を作成して**分割**する。
        -   この新しい`Item`を「直前の`Item`」として更新し、以降の処理の比較基準とする。
    -   `List`以外の要素は、直前の`Item`にそのまま取り込まれる。

---

## 処理2: Item要素の弟要素を順次処理 (※NORMAL_PROCESSINGモードの詳細)

`NORMAL_PROCESSING`モードにおける、`Item`の取り込み・分割ロジックは以下の通り。

### 目的

`NORMAL_PROCESSING`モードにおいて、`Item`要素の弟要素を順番に見ていき、その種類によって以下のように処理する：
- **取り込み**: 既存のItem要素の子要素として追加
- **分割**: 新しいItem要素を作成し、弟要素を新Item要素の起点とする

### 分岐条件

| 分岐 | 条件 | 階層判定 | 処理内容 |
|------|------|----------|----------|
| 分岐1-1 | ColumnありList要素 | `are_same_hierarchy`が`True` | Item分割 |
| 分岐1-2 | ColumnありList要素 | `are_same_hierarchy`が`False` | Item取り込み |
| 分岐2-1 | ColumnなしList要素（通常テキスト） | - | Item取り込み |
| 分岐2-2-1 | ColumnなしList要素（括弧付き科目名） | `are_same_hierarchy`が`True` | Item分割 |
| 分岐2-2-2 | ColumnなしList要素（括弧付き科目名） | `are_same_hierarchy`が`False` | Item取り込み |
| 分岐2-3-1 | ColumnなしList要素（括弧付き指導項目） | `are_same_hierarchy`が`True` | Item分割 |
| 分岐2-3-2 | ColumnなしList要素（括弧付き指導項目） | `are_same_hierarchy`が`False` | Item取り込み |
| 分岐3 | List要素以外（TableStruct、FigStruct等） | - | Item取り込み |

### 分岐1-1: ColumnありList要素で同階層（Item分割）

**処理内容**  
既存ItemのItemTitleの値と、弟要素の1つ目のColumnの値を比較し、同階層の項目ラベルと判定された場合、Item要素を分割する。分割点以降の要素は新しいItem要素に移動する。

**入力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>
      <Sentence Num="1">１</Sentence>
    </ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
  </Item>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">２</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">項目名2</Sentence>
      </Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">３</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">項目名3</Sentence>
      </Column>
    </ListSentence>
  </List>
</Paragraph>
```

**出力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>１</ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
  </Item>
  <Item Num="2">
    <ItemTitle>２</ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">項目名2</Sentence>
    </ItemSentence>
  </Item>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">３</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">項目名3</Sentence>
      </Column>
    </ListSentence>
  </List>
</Paragraph>
```

### 分岐1-2: ColumnありList要素で異なる階層（Item取り込み）

**処理内容**  
既存ItemのItemTitleの値と、弟要素の1つ目のColumnの値を比較し、異なる階層の項目ラベルと判定された場合、弟要素を既存Item要素の子要素として取り込む。

**入力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>
      <Sentence Num="1">１</Sentence>
    </ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
  </Item>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（１）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">下位項目名1</Sentence>
      </Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（２）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">下位項目名2</Sentence>
      </Column>
    </ListSentence>
  </List>
</Paragraph>
```

**出力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>１</ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
    <List>
      <ListSentence>
        <Column Num="1">
          <Sentence Num="1">（１）</Sentence>
        </Column>
        <Column Num="2">
          <Sentence Num="1">下位項目名1</Sentence>
        </Column>
      </ListSentence>
    </List>
  </Item>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（２）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">下位項目名2</Sentence>
      </Column>
    </ListSentence>
  </List>
</Paragraph>
```

### 分岐2-1: ColumnなしList要素（通常テキスト）でItem取り込み

**処理内容**  
弟要素のList要素が通常のテキスト（括弧付きでない）の場合、既存Item要素の子要素として取り込む。

**入力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>
      <Sentence Num="1">１</Sentence>
    </ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
  </Item>
  <List>
    <ListSentence>
      <Sentence Num="1">項目1の説明テキスト1</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">項目1の説明テキスト2</Sentence>
    </ListSentence>
  </List>
</Paragraph>
```

**出力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>１</ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
    <List>
      <ListSentence>
        <Sentence Num="1">項目1の説明テキスト1</Sentence>
      </ListSentence>
    </List>
    <List>
      <ListSentence>
        <Sentence Num="1">項目1の説明テキスト2</Sentence>
      </ListSentence>
    </List>
  </Item>
</Paragraph>
```

### 分岐2-2-1: 括弧付き科目名で同階層（Item分割）

**処理内容**  
既存ItemのItemSentenceの値と、弟要素のSentenceの値を比較し、同階層の項目ラベルと判定された場合（両方とも括弧付き科目名）、Item要素を分割する。

**入力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle/>
    <ItemSentence Num="1">
      <Sentence Num="1">〔科目名1〕</Sentence>
    </ItemSentence>
  </Item>
  <List>
    <ListSentence>
      <Sentence Num="1">科目1の説明テキスト</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">〔科目名2〕</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">科目2の説明テキスト</Sentence>
    </ListSentence>
  </List>
</Paragraph>
```

**出力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle/>
    <ItemSentence Num="1">
      <Sentence Num="1">〔科目名1〕</Sentence>
    </ItemSentence>
    <List>
      <ListSentence>
        <Sentence Num="1">科目1の説明テキスト</Sentence>
      </ListSentence>
    </List>
  </Item>
  <Item Num="2">
    <ItemTitle/>
    <ItemSentence Num="1">
      <Sentence Num="1">〔科目名2〕</Sentence>
    </ItemSentence>
  </Item>
  <List>
    <ListSentence>
      <Sentence Num="1">科目2の説明テキスト</Sentence>
    </ListSentence>
  </List>
</Paragraph>
```

### 分岐2-2-2: 括弧付き科目名で異なる階層（Item取り込み）

**処理内容**  
既存ItemのItemSentenceの値と、弟要素のSentenceの値を比較し、異なる階層の項目ラベルと判定された場合（既存Itemが通常項目で弟要素が括弧付き科目名）、既存Item要素の子要素として取り込む。

**入力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>
      <Sentence Num="1">１</Sentence>
    </ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
  </Item>
  <List>
    <ListSentence>
      <Sentence Num="1">〔科目名1〕</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">科目1の説明テキスト</Sentence>
    </ListSentence>
  </List>
</Paragraph>
```

**出力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>１</ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
    <List>
      <ListSentence>
        <Sentence Num="1">〔科目名1〕</Sentence>
      </ListSentence>
    </List>
    <List>
      <ListSentence>
        <Sentence Num="1">科目1の説明テキスト</Sentence>
      </ListSentence>
    </List>
  </Item>
</Paragraph>
```

### 分岐2-3-1: 括弧付き指導項目で同階層（Item分割）

**処理内容**  
既存ItemのItemSentenceの値と、弟要素のSentenceの値を比較し、同階層の項目ラベルと判定された場合（両方とも括弧付き指導項目）、Item要素を分割する。

**入力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle/>
    <ItemSentence Num="1">
      <Sentence Num="1">〔指導項目〕</Sentence>
    </ItemSentence>
  </Item>
  <List>
    <ListSentence>
      <Sentence Num="1">指導項目の説明テキスト1</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">〔指導項目〕</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">指導項目の説明テキスト2</Sentence>
    </ListSentence>
  </List>
</Paragraph>
```

**出力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle/>
    <ItemSentence Num="1">
      <Sentence Num="1">〔指導項目〕</Sentence>
    </ItemSentence>
    <List>
      <ListSentence>
        <Sentence Num="1">指導項目の説明テキスト1</Sentence>
      </ListSentence>
    </List>
  </Item>
  <Item Num="2">
    <ItemTitle/>
    <ItemSentence Num="1">
      <Sentence Num="1">〔指導項目〕</Sentence>
    </ItemSentence>
  </Item>
  <List>
    <ListSentence>
      <Sentence Num="1">指導項目の説明テキスト2</Sentence>
    </ListSentence>
  </List>
</Paragraph>
```

### 分岐2-3-2: 括弧付き指導項目で異なる階層（Item取り込み）

**処理内容**  
既存ItemのItemSentenceの値と、弟要素のSentenceの値を比較し、異なる階層の項目ラベルと判定された場合（既存Itemが括弧付き科目名で弟要素が括弧付き指導項目）、既存Item要素の子要素として取り込む。

**入力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle/>
    <ItemSentence Num="1">
      <Sentence Num="1">〔科目名1〕</Sentence>
    </ItemSentence>
  </Item>
  <List>
    <ListSentence>
      <Sentence Num="1">〔指導項目〕</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">指導項目の説明テキスト</Sentence>
    </ListSentence>
  </List>
</Paragraph>
```

**出力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle/>
    <ItemSentence Num="1">
      <Sentence Num="1">〔科目名1〕</Sentence>
    </ItemSentence>
    <List>
      <ListSentence>
        <Sentence Num="1">〔指導項目〕</Sentence>
      </ListSentence>
    </List>
    <List>
      <ListSentence>
        <Sentence Num="1">指導項目の説明テキスト</Sentence>
      </ListSentence>
    </List>
  </Item>
</Paragraph>
```

### 分岐3: List要素以外でItem取り込み

**処理内容**  
弟要素がList要素以外（TableStruct、FigStruct、StyleStruct等）の場合、既存Item要素の子要素として取り込む。

**出力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>１</ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
  </Item>
  <TableStruct>
    <Table>
      <TableRow>
        <TableColumn>
          <Sentence Num="1">項目1に関連する表の内容</Sentence>
        </TableColumn>
      </TableRow>
    </Table>
  </TableStruct>
  <FigStruct>
    <Fig src="item1_figure.jpg"/>
  </FigStruct>
</Paragraph>
```

**出力例**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>
      <Sentence Num="1">１</Sentence>
    </ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
    <TableStruct>
      <Table>
        <TableRow>
          <TableColumn>
            <Sentence Num="1">項目1に関連する表の内容</Sentence>
          </TableColumn>
        </TableRow>
      </Table>
    </TableStruct>
    <FigStruct>
      <Fig src="item1_figure.jpg"/>
    </FigStruct>
  </Item>
</Paragraph>
```

---

## 処理3

### 目的

処理2で生成されたItem要素の弟要素（Paragraph要素内に最初に登場するもののみ）を確認し、条件に合致した場合に分割する：
- **分割**: 新しいItem要素を作成し、弟要素を新Item要素の起点とする

なお、処理3の分割によって新しく生成されたItem要素は、処理1,2の再実行は不要である。

### 分岐条件
**前提条件**
・Paragraph要素内の、ParagraphSentenceのすぐ次の弟要素のItem要素である。
・Item要素のItemTitle,ItemSentence>Sentence要素の値が空である。

**処理の流れ**
1. Item要素内を上から走査する
2. 出現した要素によって、以下の処理を実行。なお、分割処理が1回発生した時点で処理を終了する。（3の手順後、次のParagraph要素内の最初のItem要素の処理に移る）

ColumnありList要素：分割
ColumnなしList要素（括弧付き科目名）：分割
ColumnなしList要素（括弧付き指導項目）：分割
それ以外：スルー

3. 分割が発生した場合、Paragraph要素内のItem要素のNum属性を再度付番する

**入力例**

```xml
<Paragraph Num="4">
  <ParagraphNum>４</ParagraphNum>
  <ParagraphSentence>
    <Sentence Num="1">ParagraphSentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle/>
    <ItemSentence Num="1">
      <Sentence Num="1"/>
    </ItemSentence>
    <!-- columnなしList：スルー対象 -->
    <List>
      <ListSentence>
        <Sentence Num="1">テキスト</Sentence>
      </ListSentence>
    </List>
    <!-- columnありList：分割対象 -->
    <List>
      <ListSentence>
        <Column Num="1">
          <Sentence Num="1">（１）</Sentence>
        </Column>
        <Column Num="2">
          <Sentence Num="1">項目名1</Sentence>
        </Column>
      </ListSentence>
    </List>
    <List>
      <ListSentence>
        <Column Num="1">
          <Sentence Num="1">（２）</Sentence>
        </Column>
        <Column Num="2">
          <Sentence Num="1">項目名2</Sentence>
        </Column>
      </ListSentence>
    </List>
    {中略}
  </Item>
  <Item Num="2">
    <ItemTitle>ItemTitleの値</ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">ItemSentenceの値</Sentence>
    </ItemSentence>
    {中略}
  </Item>
</Paragraph>
```

**出力例**
```xml
<Paragraph Num="4">
  <ParagraphNum>４</ParagraphNum>
  <ParagraphSentence>
    <Sentence Num="1">ParagraphSentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle/>
    <ItemSentence Num="1">
      <Sentence Num="1"/>
    </ItemSentence>
    <List>
      <ListSentence>
        <Sentence Num="1">テキスト</Sentence>
      </ListSentence>
    </List>
    </Item>
    <!-- 分割 -->
    <Item Num="2">
    <ItemTitle/>
    <ItemSentence Num="1">
      <Sentence Num="1"/>
    </ItemSentence>
    <List>
      <ListSentence>
        <Column Num="1">
          <Sentence Num="1">（１）</Sentence>
        </Column>
        <Column Num="2">
          <Sentence Num="1">項目名1</Sentence>
        </Column>
      </ListSentence>
    </List>
    <List>
      <ListSentence>
        <Column Num="1">
          <Sentence Num="1">（２）</Sentence>
        </Column>
        <Column Num="2">
          <Sentence Num="1">項目名2</Sentence>
        </Column>
      </ListSentence>
    </List>
    {中略}
  </Item>
  <!-- 再付番 -->
  <Item Num="3">
    <ItemTitle>ItemTitleの値</ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">ItemSentenceの値</Sentence>
    </ItemSentence>
    {中略}
  </Item>
</Paragraph>
```

## 補足事項

### 用語定義

#### 空のItem要素
以下の構造を持つItem要素を指す：
```xml
<Item Num="1">
  <ItemTitle/>
  <ItemSentence Num="1">
    <Sentence Num="1"></Sentence>
  </ItemSentence>
</Item>
```

#### 括弧付き科目名
- `〔...〕`または`【...】`で囲まれたテキスト
- 例: `〔科目名1〕`、`【国語】`

#### 括弧付き指導項目
- `〔指導項目〕`または`【指導項目】`というテキスト
- 指導項目は科目名より階層が深くなる特殊な扱い

### 階層判定の基準

項目ラベルの種類（形式）で階層を判定する：
- **数字系**: `１`、`１．`、`1`、`1.`
- **括弧数字系**: `（１）`、`(1)`
- **カタカナ系**: `ア`、`イ`、`ウ`
- **ひらがな系**: `あ`、`い`、`う`
- **括弧付き科目名**: `〔科目名〕`
- **括弧付き指導項目**: `〔指導項目〕`

同じ種類のラベルは同階層と判定される。

### 処理の繰り返し

処理2でItem要素が分割された場合：
1. 新しいItem要素が作成される
2. 分割点以降の弟要素が残る
3. 新しいItem要素に対して**処理1から再実行**される
4. 全ての弟要素が処理されるまで繰り返す

### 実装上の注意点

- 処理1は常に最初の弟要素のみを処理する
- 処理2は全ての弟要素を順次処理する
- 階層判定は項目ラベルの形式で行う（内容ではない）
- TableStruct、FigStruct等の非List要素は常に取り込み対象
- Num属性は適切に連番を付与する

---





**更新履歴**
- 2025年XX月XX日: 初版作成
