# 46_image_list_split_mode_basic

## テスト内容

画像List（QuoteStruct/FigのみでテキストのないColumnなしList）の後にテキストのColumnなしListが連続する場合の並列分割ロジックをテストします。

## 背景

画像ListはSentenceにテキストがないため、変換後の要素は `no_column_text` タイプではなく `other` タイプと判定されます。そのため `no_column_text_split_mode`（モード2）が有効でも並列分割が適用されず、後続のテキストListは同じItemSentence内に連続するSentence要素（Num=2, 3, …）として統合されていました。

本オプション（`image_list_split_mode`）を有効にすると、画像Listから変換された要素の後に続くテキストのColumnなしListも、それぞれ並列の要素（Item等）に分割されます。

## 期待される動作

- 画像List（QuoteStruct/Fig）がItem要素に変換される（ItemTitleは空、ItemSentenceにQuoteStruct入りSentenceを保持）
- 後続のテキストのColumnなしListは、Sentenceとして統合されず、それぞれ別々のItem要素に変換される（並列分割）
- Item Numは1から連番で再採番される

## 設定

このテストケースは、`label_config.json` の `conversion_behaviors.image_list_split_mode` が `enabled: true` の場合に動作します。
2つ目以降のテキストList同士の並列分割には `no_column_text_split_mode` も `enabled: true` である必要があります（run_tests.pyが両方を一時的に有効化します）。

## 統計情報

変換統計に ColumnなしList: 3箇所 がカウントされるはずです。
