# 03_process1_branch2_1_1_grade_double_bracket

## テスト内容

処理1-分岐2-1-1: 学年（2つ記載）List → Subitem1変換

## 期待される動作

- ItemSentence直後のList要素が検出される
- Listの内容が「〔第３学年及び第４学年〕」という学年（2つ記載）パターンである
- このListがSubitem1要素に変換される
- Subitem1Titleは空要素になる
- 学年パターン「〔第３学年及び第４学年〕」がSubitem1Sentenceに配置される

## 統計情報

変換統計に `converted_grade_double_list_to_subitem1: 1` がカウントされるはずです。

## 注意点

学年パターンは「〔第[1-6]学年及び第[1-6]学年〕」形式で判定します。
