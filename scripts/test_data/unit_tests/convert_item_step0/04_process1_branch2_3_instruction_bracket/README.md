# 04_process1_branch2_3_instruction_bracket

## テスト内容

処理1-分岐2-3: 括弧付き指導項目List → Item変換

## 期待される動作

- ParagraphSentence直後のList要素が検出される
- Listの内容が「〔指導項目〕」という括弧付き指導項目である
- このListがItem要素に変換される
- ItemTitleは空要素になる
- 括弧付き指導項目「〔指導項目〕」がItemSentenceに配置される

## 統計情報

変換統計に `converted_instruction_list: 1` がカウントされるはずです。

## 注意点

括弧付き指導項目は「〔指導項目〕」または「【指導項目】」形式で判定します。
