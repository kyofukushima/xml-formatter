# 37_no_column_list_with_ruby

## テスト内容

Ruby要素（ルビ）を含むColumnなしListの変換をテストします。

## 期待される動作

- ColumnなしListがItem要素に変換される
- Ruby要素（`<Ruby>`と`<Rt>`）が保持される
- Sentence要素の属性（`WritingMode`など）が保持される
- Ruby要素内のテキスト構造が保持される

## 統計情報

変換統計に `converted_no_column_list: 1` がカウントされるはずです。

## 注意事項

このテストケースは、Ruby要素などの子要素構造が変換時に失われないことを確認するためのものです。
修正前は、Ruby要素が失われてテキストのみが残る問題が発生していました。
