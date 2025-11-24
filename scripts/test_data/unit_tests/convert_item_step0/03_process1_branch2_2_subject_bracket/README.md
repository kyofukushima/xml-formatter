# 03_process1_branch2_2_subject_bracket

## テスト内容

処理1-分岐2-2: 括弧付き科目名List → Item変換

## 期待される動作

- ParagraphSentence直後のList要素が検出される
- Listの内容が「〔国語〕」という括弧付き科目名である
- このListがItem要素に変換される
- ItemTitleは空要素になる
- 括弧付き科目名「〔国語〕」がItemSentenceに配置される

## 統計情報

変換統計に `converted_subject_name_list: 1` がカウントされるはずです。

## 注意点

括弧付き科目名は「〔...〕」形式で、「指導項目」が含まれないものを科目名と判定します。
