# 34_no_column_text_aggregate

## テスト内容

no_column_textタイプ同士の取り込みロジックをテストします。

## 期待される動作

- ParagraphSentence直後の最初のColumnなしListがItem要素に変換される
- 2つ目のColumnなしListは、1つ目のItem要素に取り込まれる（List要素として）
- ColumnありListも、1つ目のItem要素に取り込まれる（List要素として）
- no_column_textタイプ同士は分割されず、全て取り込まれる

## 検証ポイント

- 複数のColumnなしListが1つのItemにまとめられる
- 親要素のSentenceの次のList要素がno_column_textに該当する場合、それ以降の弟要素を全て取り込む

