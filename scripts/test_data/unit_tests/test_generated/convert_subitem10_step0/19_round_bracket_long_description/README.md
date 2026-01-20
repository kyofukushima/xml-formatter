# 19_round_bracket_long_description

## テスト内容

処理1-分岐2-2: 丸括弧付き長い説明文List → Item変換

## 期待される動作

- ParagraphSentence直後のList要素が検出される
- Listの内容が「（相談窓口の担当者が適切に対応することができるようにしていると認められる例）」という丸括弧付き長い説明文である
- このListがItem要素に変換される
- ItemTitleは空要素になる
- 丸括弧付き説明文がItemSentenceに配置される

## 統計情報

変換統計に `converted_subject_name_list: 1` がカウントされるはずです。

## 注意点

丸括弧付き説明文は「（...）」形式で、subject_labelパターンとして認識されることをテストします。
