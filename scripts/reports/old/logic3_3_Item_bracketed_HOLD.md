# Itemの括弧見出し処理ロジック（保留）

**注意: このロジックは現在保留中です。実装は一時停止されています。**

## 本文章のスコープ
Item要素内に現れる括弧付きの見出し（例: 〔指導項目〕）を検出し、Subitem1に変換するロジックについて説明する。

**前提**: Itemのfocused, textsplitの修正ロジックが完了済みであること。

---

## 基本ロジック

このスクリプトは、Item要素の内部を走査する。
Itemの子要素として、特定の括弧（〔〕）で囲まれたテキストのみを含む List 要素（以下、括弧見出しList）を検出した場合、Itemを分割し、括弧見出しをタイトルとする新しいSubitem1を作成する。

---

### 処理1: 括弧見出しによる分割とSubitem1の作成

#### 条件
- `Item`の子要素であること。
- `<List>` 要素であり、`<Column>` を含まないこと。
- `<ListSentence>` 内の `<Sentence>` のテキスト全体が `〔...〕` のパターンに一致すること。
- **重要**: 処理対象の括弧見出しは `〔指導項目〕` に限定する。
- **スキップ条件**: 処理中のItem要素の`ItemSentence`内の`Sentence`のテキストが括弧見出し（`〔...〕`形式）である場合、そのItem内の括弧見出しListは処理をスキップする。
  - これは、科目名（例: `〔医療と社会〕`）がItemSentenceにある場合、その配下の`〔指導項目〕`は当該Itemに取り込むことを意味する。

#### 動作
1.  **Itemの分割**: 括弧見出しListが出現した時点で、Itemを分割する。括弧見出しListより前の要素は、元のItemに残る。
2.  **新しいItemの作成**: 元のItemと同じ階層に、新しいItemを作成する。
3.  **Subitem1の作成**: 新しく作成したItemの中に、Subitem1を作成する。
4.  **タイトルの設定**: 括弧見出しListのテキスト（例: `〔指導項目〕`）を、新しく作成したSubitem1のSubitem1Titleに設定する。
5.  **後続要素の集約**: 元の括弧見出しListの後に続いていた要素を、すべて新しく作成したSubitem1の内部に移動する。

#### 例1: 通常の処理（ItemSentenceが括弧見出しでない場合）

**入力**
```xml
<Paragraph Num="1">
  ...
  <Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>内容１</ItemSentence>
    <List>
      <ListSentence><Sentence>テキスト１</Sentence></ListSentence>
    </List>
    <List> <!-- 括弧見出しList -->
      <ListSentence><Sentence>〔指導項目〕</Sentence></ListSentence>
    </List>
    <TableStruct>...</TableStruct> <!-- 後続要素 -->
  </Item>
  ...
</Paragraph>
```

**出力**
```xml
<Paragraph Num="1">
  ...
  <Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>内容１</ItemSentence>
    <List>
      <ListSentence><Sentence>テキスト１</Sentence></ListSentence>
    </List>
  </Item>
  <Item Num="2">
    <ItemTitle/>
    <ItemSentence><Sentence/></ItemSentence>
    <Subitem1 Num="1">
      <Subitem1Title>〔指導項目〕</Subitem1Title>
      <Subitem1Sentence><Sentence/></Subitem1Sentence>
      <TableStruct>...</TableStruct> <!-- 集約される -->
    </Subitem1>
  </Item>
  ...
</Paragraph>
```

#### 例2: スキップ条件（ItemSentenceが科目名の括弧見出しの場合）

**入力**
```xml
<Paragraph Num="1">
  ...
  <Item Num="1">
    <ItemTitle/>
    <ItemSentence>
      <Sentence Num="1">〔医療と社会〕</Sentence>
    </ItemSentence>
    <List>
      <ListSentence><Sentence>目標テキスト</Sentence></ListSentence>
    </List>
    <List> <!-- この〔指導項目〕は処理をスキップ -->
      <ListSentence><Sentence>〔指導項目〕</Sentence></ListSentence>
    </List>
    <TableStruct>...</TableStruct>
  </Item>
  ...
</Paragraph>
```

**出力**
```xml
<Paragraph Num="1">
  ...
  <Item Num="1">
    <ItemTitle/>
    <ItemSentence>
      <Sentence Num="1">〔医療と社会〕</Sentence>
    </ItemSentence>
    <List>
      <ListSentence><Sentence>目標テキスト</Sentence></ListSentence>
    </List>
    <List> <!-- そのまま保持される -->
      <ListSentence><Sentence>〔指導項目〕</Sentence></ListSentence>
    </List>
    <TableStruct>...</TableStruct>
  </Item>
  ...
</Paragraph>
```

**説明**: ItemSentenceが `〔医療と社会〕` という括弧見出しであるため、このItem内の `〔指導項目〕` List要素は処理をスキップし、そのままItem内に保持される。

