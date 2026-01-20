# 22_fullwidth_number_with_paren

## テスト内容

新規ラベルパターン2: 全角数字 + ） (`１）`形式)

## 期待される動作

- Subitem1要素内のList要素で、1つ目のColumnに「１）」「２）」などの全角数字 + ）のラベルがある
- このListがSubitem2要素に変換される
- 1つ目のColumnの内容（例：「１）」）がSubitem2Titleに配置される
- 2つ目のColumnの内容がSubitem2Sentenceに配置される

## 誤認識防止の検証

以下のパターンは**変換されずにList要素のまま残る**ことを確認：
- `（１）` - 既存の括弧全角数字（`paren_fullwidth_number`）
- `１` - 括弧なしの全角数字（`fullwidth_number`）
- `４．１` - ドット区切り数字（別の新規パターン）

## ColumnなしListの検証

- Subitem1要素内のColumnなしListは、前のSubitem2要素（ColumnありListから変換されたSubitem2）にList要素として追加されることを確認
