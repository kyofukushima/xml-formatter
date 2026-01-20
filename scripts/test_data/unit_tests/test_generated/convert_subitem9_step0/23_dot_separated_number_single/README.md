# 23_dot_separated_number_single

## テスト内容

新規ラベルパターン3: ドット区切り数字（ドット1つ） (`４．１`形式)

## 期待される動作

- ColumnありList要素で、1つ目のColumnに「４．１」「４．２」などのドット1つで区切られた数字のラベルがある
- このListがItem要素に変換される
- 1つ目のColumnの内容（例：「４．１」）がItemTitleに配置される
- 2つ目のColumnの内容がItemSentenceに配置される

## 誤認識防止の検証

以下のパターンは**変換されずにList要素のまま残る**ことを確認：
- `４` - 単一の全角数字（`fullwidth_number`）
- `４．３．２` - ドット区切り数字（ドット2つ）（別の新規パターン）
- `（４）` - 括弧付き数字（`paren_fullwidth_number`）

## ColumnなしListの検証

- ParagraphSentenceのすぐ次でない位置にあるColumnなしListは、前のItem要素（ColumnありListから変換されたItem）にList要素として追加されることを確認

## 統計情報

変換統計に `converted_labeled_list_to_item: 3` がカウントされるはずです（`４．１`、`４．２`、`（４）`の3つ）。
