# 21_fullwidth_lowercase_alphabet_with_paren

## テスト内容

新規ラベルパターン1: 全角小文字アルファベット + ） (`ａ）`形式)

## 期待される動作

- ColumnありList要素で、1つ目のColumnに「ａ）」「ｂ）」などの全角小文字アルファベット + ）のラベルがある
- このListがItem要素に変換される
- 1つ目のColumnの内容（例：「ａ）」）がItemTitleに配置される
- 2つ目のColumnの内容がItemSentenceに配置される

## 誤認識防止の検証

以下のパターンは**変換されずにList要素のまま残る**ことを確認：
- `（ａ）` - 既存の括弧全角小文字アルファベット（`paren_fullwidth_lowercase_alphabet`）
- `ａ` - 括弧なしの全角小文字アルファベット（`fullwidth_lowercase_alphabet`）
- `Ａ）` - 全角大文字アルファベット + ）（`fullwidth_uppercase_alphabet`）

## ColumnなしListの検証

- ParagraphSentenceのすぐ次でない位置にあるColumnなしListは、前のItem要素（ColumnありListから変換されたItem）にList要素として追加されることを確認

## 統計情報

変換統計に `converted_labeled_list_to_item: 4` がカウントされるはずです（`ａ）`、`（ａ）`、`ｂ）`、`Ａ）`の4つ）。
