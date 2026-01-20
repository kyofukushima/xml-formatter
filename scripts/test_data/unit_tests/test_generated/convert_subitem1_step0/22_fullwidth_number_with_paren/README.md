# 22_fullwidth_number_with_paren

## テスト内容

新規ラベルパターン2: 全角数字 + ） (`１）`形式)

## 期待される動作

- ColumnありList要素で、1つ目のColumnに「１）」「２）」などの全角数字 + ）のラベルがある
- このListがItem要素に変換される
- 1つ目のColumnの内容（例：「１）」）がItemTitleに配置される
- 2つ目のColumnの内容がItemSentenceに配置される

## 誤認識防止の検証

以下のパターンは**変換されずにList要素のまま残る**ことを確認：
- `（１）` - 既存の括弧全角数字（`paren_fullwidth_number`）
- `１` - 括弧なしの全角数字（`fullwidth_number`）
- `４．１` - ドット区切り数字（別の新規パターン）

## ColumnなしListの検証

- ParagraphSentenceのすぐ次でない位置にあるColumnなしListは、前のItem要素（ColumnありListから変換されたItem）にList要素として追加されることを確認

## 統計情報

変換統計に `converted_labeled_list_to_item: 3` がカウントされるはずです（`１）`、`（１）`、`２）`の3つ）。
