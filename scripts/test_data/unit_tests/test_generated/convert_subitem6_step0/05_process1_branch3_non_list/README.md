# 05_process1_branch3_non_list

## テスト内容

処理1-分岐3: 非List要素(TableStruct, FigStruct, StyleStruct) → Item内要素変換

## 期待される動作

- ParagraphSentence直後のTableStruct要素が検出される
- TableStruct要素がItem要素に変換される
- ItemTitleは空要素になる
- ItemSentenceには空のSentence要素が含まれる
- 元のTableStruct要素がItemSentenceの後に配置される

## 統計情報

変換統計に `converted_non_list_to_item: 1` がカウントされるはずです。

## 注意点

FigStruct, StyleStruct要素も同様に処理されます。
