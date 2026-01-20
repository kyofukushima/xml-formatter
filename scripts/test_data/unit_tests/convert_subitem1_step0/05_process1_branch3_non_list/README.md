# 05_process1_branch3_non_list

## テスト内容

処理1-分岐3: 非List要素(TableStruct, FigStruct, StyleStruct) → Subitem1内要素変換

## 期待される動作

- ItemSentence直後のTableStruct要素が検出される
- TableStruct要素がSubitem1要素に変換される
- Subitem1Titleは空要素になる
- Subitem1Sentenceには空のSentence要素が含まれる
- 元のTableStruct要素がSubitem1Sentenceの後に配置される

## 統計情報

変換統計に `converted_non_list_to_subitem1: 1` がカウントされるはずです。

## 注意点

FigStruct, StyleStruct要素も同様に処理されます。








