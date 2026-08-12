# 32_image_list_split_mode_formula_variables

## テスト内容

実データ（告示の数式規定）を模したパターンで、画像List（数式のQuoteStruct/Fig）の後に数式の変数説明のテキストListが連続する場合の並列分割ロジックを、Subitem8レベルでテストします。

- 画像List：数式の画像（QuoteStruct/Fig、テキストなし）
- テキストList1：「この式において、Ｅ<Sub>ＡＣ</Sub>、…は、それぞれ次の数値を表すものとする。」（Sub要素を含む）
- テキストList2〜3：「Ｅ<Sub>ＡＣ</Sub>：…」形式の変数定義（Sub要素を含む）

## 期待される動作

- 画像ListがSubitem8要素に変換される（Subitem8Titleは空、Subitem8SentenceにQuoteStruct入りSentenceを保持）
- 後続の変数説明のテキストListは、同一Subitem8Sentence内のSentence連続（Num=2, 3, …）として統合されず、それぞれ別々のSubitem8要素に変換される（並列分割）
- Sentence内のSub要素・WritingMode属性がそのまま保持される
- Subitem8 Numは1から連番で再採番される

## 設定

このテストケースは、`label_config.json` の `conversion_behaviors.image_list_split_mode` が `enabled: true` の場合に動作します。

## 統計情報

変換統計に ColumnなしList: 4箇所 がカウントされるはずです。
