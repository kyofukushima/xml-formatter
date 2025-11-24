# Subitem1の括弧見出し処理ロジック（保留）

**注意: このロジックは現在保留中です。実装は一時停止されています。**

## 本文章のスコープ
Subitem1要素内に現れる括弧付きの見出し（例: 〔指導項目〕）を検出し、Subitem2に変換するロジックについて説明する。

**前提**: Subitem1のfocused, textsplitの修正ロジックが完了済みであること。

---

## 基本ロジック

このスクリプトは、Subitem1要素の内部を走査する。
Subitem1の子要素として、特定の括弧（〔〕）で囲まれたテキストのみを含む List 要素（以下、括弧見出しList）を検出した場合、Subitem1を分割し、括弧見出しをタイトルとする新しいSubitem2を作成する。

---

### 処理1: 括弧見出しによる分割とSubitem2の作成

#### 条件
- `Subitem1`の子要素であること。
- `<List>` 要素であり、`<Column>` を含まないこと。
- `<ListSentence>` 内の `<Sentence>` のテキスト全体が `〔...〕` のパターンに一致すること。

#### 動作
1.  **Subitem1の分割**: 括弧見出しListが出現した時点で、Subitem1を分割する。括弧見出しListより前の要素は、元のSubitem1に残る。
2.  **新しいSubitem1の作成**: 元のSubitem1と同じ階層に、新しいSubitem1を作成する。
3.  **Subitem2の作成**: 新しく作成したSubitem1の中に、Subitem2を作成する。
4.  **タイトルの設定**: 括弧見出しListのテキストを、新しく作成したSubitem2のSubitem2Titleに設定する。
5.  **後続要素の集約**: 元の括弧見出しListの後に続いていた要素を、すべて新しく作成したSubitem2の内部に移動する。

#### 例

**入力**
```xml
<Item Num="1">
  ...
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence>内容１</Subitem1Sentence>
    <List>
      <ListSentence><Sentence>テキスト１</Sentence></ListSentence>
    </List>
    <List> <!-- 括弧見出しList -->
      <ListSentence><Sentence>〔指導項目〕</Sentence></ListSentence>
    </List>
    <TableStruct>...</TableStruct> <!-- 後続要素 -->
  </Subitem1>
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
    <List>
      <ListSentence><Sentence>テキスト１</Sentence></ListSentence>
    </List>
  </Subitem1>
  <Subitem1 Num="2">
    <Subitem1Title/>
    <Subitem1Sentence><Sentence/></Subitem1Sentence>
    <Subitem2 Num="1">
      <Subitem2Title>〔指導項目〕</Subitem2Title>
      <Subitem2Sentence><Sentence/></Subitem2Sentence>
      <TableStruct>...</TableStruct> <!-- 集約される -->
    </Subitem2>
  </Subitem1>
  ...
</Item>
```
