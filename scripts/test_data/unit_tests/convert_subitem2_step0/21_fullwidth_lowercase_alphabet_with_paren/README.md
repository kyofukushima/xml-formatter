# 21_fullwidth_lowercase_alphabet_with_paren

## テスト内容

新規ラベルパターン1: 全角小文字アルファベット + ） (`ａ）`形式)

## 期待される動作

- Subitem1要素内のList要素で、1つ目のColumnに「ａ）」「ｂ）」などの全角小文字アルファベット + ）のラベルがある
- このListがSubitem2要素に変換される
- 1つ目のColumnの内容（例：「ａ）」）がSubitem2Titleに配置される
- 2つ目のColumnの内容がSubitem2Sentenceに配置される

## 誤認識防止の検証

以下のパターンは**変換されずにList要素のまま残る**ことを確認：
- `（ａ）` - 既存の括弧全角小文字アルファベット（`paren_fullwidth_lowercase_alphabet`）
- `ａ` - 括弧なしの全角小文字アルファベット（`fullwidth_lowercase_alphabet`）
- `Ａ）` - 全角大文字アルファベット + ）（`fullwidth_uppercase_alphabet`）

## ColumnなしListの検証

- Subitem1要素内のColumnなしListは、前のSubitem2要素（ColumnありListから変換されたSubitem2）にList要素として追加されることを確認
