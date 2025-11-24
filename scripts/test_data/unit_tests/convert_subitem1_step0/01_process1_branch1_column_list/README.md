# 01_process1_branch1_column_list

## テスト内容

処理1-分岐1: ColumnありListでラベルがある場合 → Subitem1TitleとSubitem1Sentenceに変換

## 期待される動作

- ItemSentence直後のList要素が検出される
- ListにColumnが2つあり、1つ目のColumnにラベル「（ア）」がある
- このListがSubitem1要素に変換される
- 1つ目のColumnの内容「（ア）」がSubitem1Titleに配置される
- 2つ目のColumnの内容「ColumnありListの内容」がSubitem1Sentenceに配置される

## 統計情報

変換統計に `converted_labeled_list_to_subitem1: 1` がカウントされるはずです。







