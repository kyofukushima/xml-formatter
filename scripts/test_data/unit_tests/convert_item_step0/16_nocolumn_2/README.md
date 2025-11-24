# 02_process1_branch2_1_no_column_list

## テスト内容

処理1-分岐2-1: ColumnなしList → ItemSentenceに変換

## 期待される動作

- ParagraphSentence直後のList要素が検出される
- ListにColumnがなく、ListSentence/Sentenceの内容がある
- このListがItem要素に変換される
- ItemTitleは空要素になる
- ListSentenceの内容「ColumnなしListの内容」がItemSentenceにコピーされる

## 統計情報

変換統計に `converted_no_column_list: 1` がカウントされるはずです。
