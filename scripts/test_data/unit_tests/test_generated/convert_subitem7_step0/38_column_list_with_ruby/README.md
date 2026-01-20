# 38_column_list_with_ruby

## テスト内容

Ruby要素（ルビ）を含むColumnありListの変換をテストします。

## 期待される動作

- ColumnありListがItem要素に変換される
- ItemTitleに1つ目のColumnの内容が設定される
- ItemSentenceに2つ目のColumnの内容が設定される
- Ruby要素（`<Ruby>`と`<Rt>`）が保持される
- Sentence要素の属性（`WritingMode`など）が保持される

## 統計情報

変換統計に `converted_labeled_list: 1` がカウントされるはずです。

## 注意事項

このテストケースは、ColumnありListの変換時にRuby要素などの子要素構造が保持されることを確認するためのものです。
