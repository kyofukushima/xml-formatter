# Paragraph修正ロジック1

## 対応スクリプト
`convert_paragraph_step1.py`

## 本文章のスコープ
Paragraph特化スクリプト（Step1: ParagraphNum補完）

**前提**: Article特化スクリプト（`convert_article_focused.py`）の処理済みであること

## 項目ラベル定義

項目ラベルの詳細な定義については、[common/label_definitions.md](common/label_definitions.md) を参照してください。

---

## 処理1　ParagraphNumが空の場合

Paragraph要素にParagraphNum要素が存在しない場合は、Paragraph要素の最初に空で追加する

※ ただし、この例は実例として未発見

### 入力例

```xml
<Paragraph Num="1">
  <List>
    <ListSentence>
      <Sentence Num="1">高等部における教育については，学校教育法第７２条に定める目的を実現するために，生徒の障害の状態や特性及び心身の発達の段階等を十分考慮して，次に掲げる目標の達成に努めなければならない。</Sentence>
    </ListSentence>
  </List>
</Paragraph>
```

### 出力例

```xml
<Paragraph Num="1">
  <ParagraphNum />
  <List>
    <ListSentence>
      <Sentence Num="1">高等部における教育については，学校教育法第７２条に定める目的を実現するために，生徒の障害の状態や特性及び心身の発達の段階等を十分考慮して，次に掲げる目標の達成に努めなければならない。</Sentence>
    </ListSentence>
  </List>
</Paragraph>
```

## 処理の詳細

### アルゴリズム

1. すべてのParagraph要素を検索
2. 各Paragraph要素について、ParagraphNum要素の存在を確認
3. ParagraphNum要素が存在しない場合:
   - 空の`<ParagraphNum />`要素を作成
   - Paragraph要素の先頭（index=0）に挿入

### 実装上の注意点

- この処理は後続の処理（処理2以降）の前提条件となる
- ParagraphNum要素が存在することで、後続の処理でList要素をParagraphSentenceに変換する際の基準点となる
- 空のParagraphNum要素は、後の処理でラベル値が挿入される可能性がある

## 統計情報

スクリプト実行時に以下の統計情報が出力される：

- `total_paragraphs`: 処理したParagraph要素の総数
- `paragraphs_with_num`: すでにParagraphNum要素が存在していたParagraph要素の数
- `paragraphs_without_num`: ParagraphNum要素が存在しなかったParagraph要素の数
- `added_paragraph_nums`: 新たに追加したParagraphNum要素の数

## 次のステップ

この処理の後、以下の処理を実行する：

- **Paragraph修正ロジック2**: ParagraphNumの次のList要素をParagraphSentenceに変換
