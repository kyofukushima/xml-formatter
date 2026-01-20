# 40_no_column_text_split_mode_with_column_list

## テスト内容

モード2において、途中でカラムありリスト（ラベル付き）が登場した場合の並列分割終了ロジックをテストします。

## 期待される動作

- ParagraphSentence直後の最初のColumnなしListがItem要素に変換される
- カラムありリスト（ラベル付き）が登場した場合、並列分割を終了し、その後のカラムなしリストはList要素として取り込まれる
- カラムありリストとその後のカラムなしリストは、最初のItem要素に取り込まれる

## 設定

このテストケースは、`no_column_text_split_mode`設定が`enabled: true`の場合に動作します。

## 統計情報

変換統計に `converted_no_column_list: 1` がカウントされるはずです。


