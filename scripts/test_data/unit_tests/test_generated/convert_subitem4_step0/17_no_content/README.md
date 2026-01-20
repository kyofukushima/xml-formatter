# 17_no_content

## テスト内容

ParagraphNumとParagraphSentenceが空の場合の、複数のColumnなしListの取り込みロジックをテストします。

## 期待される動作

- ParagraphSentenceが空でも、最初のColumnなしListがItem要素に変換される
- 2つ目以降のColumnなしListは、1つ目のItem要素に取り込まれる（List要素として）
- no_column_textタイプ同士は分割されず、全て取り込まれる

## 統計情報

変換統計に `converted_no_column_list: 1` がカウントされるはずです。
