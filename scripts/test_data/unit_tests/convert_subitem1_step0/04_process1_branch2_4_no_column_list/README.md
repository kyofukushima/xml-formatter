# 04_process1_branch2_4_no_column_list

## テスト内容

処理1-分岐2-4: ColumnなしList → Subitem1内Listとして配置

## 期待される動作

- ItemSentence直後のList要素が検出される
- ListにColumnがなく、内容がある（括弧付き科目名・指導項目ではない）
- 空のSubitem1要素が作成され、その子要素として元のListが配置される
- Subitem1Titleは空要素になる
- Subitem1Sentenceには空のSentence要素が含まれる
- 元のList要素がSubitem1Sentenceの後に配置される

## 統計情報

変換統計に `converted_no_column_list_to_subitem1: 1` がカウントされるはずです。








