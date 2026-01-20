# 20_empty_parent_create_item

## テストケース: 親要素が空の場合でもItem要素を作成

### 目的
親要素（Paragraph）のParagraphNumとParagraphSentenceが空の場合でも、Item要素を作成し、List要素のSentence要素をItemSentenceに挿入することを検証する。

### 入力
- ParagraphNum: 空
- ParagraphSentence/Sentence: 空
- List要素: ColumnなしList（1つ）

### 期待結果
親要素が空でも、Item要素を作成し、List要素のSentence要素のテキストをItemSentenceに設定する。

### 統計情報
- CONVERTED_NO_COLUMN_LIST_TO_ITEM: 1






