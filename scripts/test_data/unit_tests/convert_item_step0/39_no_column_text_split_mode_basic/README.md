# 39_no_column_text_split_mode_basic

## テスト内容

モード2（no_column_text_split_mode）の基本的な並列分割ロジックをテストします。

## 期待される動作

- ParagraphSentence直後の最初のColumnなしListがItem要素に変換される
- 2つ目以降のColumnなしListは、それぞれ別々のItem要素に変換される（並列分割）
- no_column_textタイプ同士は分割される（モード2）

## 設定

このテストケースは、`no_column_text_split_mode`設定が`enabled: true`の場合に動作します。

## 統計情報

変換統計に `converted_no_column_list: 3` がカウントされるはずです。


