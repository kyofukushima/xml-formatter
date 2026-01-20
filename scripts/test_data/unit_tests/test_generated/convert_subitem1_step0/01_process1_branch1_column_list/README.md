# 01_process1_branch1_column_list

## テスト内容

処理1-分岐1: ColumnありListでラベルがある場合 → ItemTitleとItemSentenceに変換

## 期待される動作

- ParagraphSentence直後のList要素が検出される
- ListにColumnが2つあり、1つ目のColumnにラベル「（１）」がある
- このListがItem要素に変換される
- 1つ目のColumnの内容「（１）」がItemTitleに配置される
- 2つ目のColumnの内容「ColumnありListの内容」がItemSentenceに配置される

## 統計情報

変換統計に `converted_labeled_list_to_item: 1` がカウントされるはずです。
