# 20_skip_empty_parent

## テストケース: 親要素が空の場合に変換をスキップ

### 目的
親要素（Subitem3）のTitleとSentenceが両方空の場合、Subitem4要素の作成をスキップすることを検証する。

### 入力
- Subitem3Title: 空
- Subitem3Sentence/Sentence: 空
- List要素: ColumnなしList

### 期待結果
親要素が空のため、List要素をSubitem4に変換せず、そのまま保持する。

### 統計情報
- SKIPPED_DUE_TO_EMPTY_PARENT: 1
