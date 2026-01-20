# 41_no_column_text_split_mode_with_figstruct

## テスト内容

モード2において、途中でTableStructまたはFigStructなどの要素が登場した場合の取り込みロジックをテストします。

## 期待される動作

- ParagraphSentence直後の最初のColumnなしListがItem要素に変換される
- FigStructが登場した場合、最初のItem要素の直接の子要素として取り込まれる（ItemSentenceの後）
- FigStructの後のカラムなしリストは、それぞれ別々のItem要素に変換される（並列分割を継続）

## 注意事項

- FigStructはItemSentence内ではなく、Item要素の直接の子要素として配置されます（スキーマ準拠）
- Fig要素には`src`属性が必須です

## 設定

このテストケースは、`no_column_text_split_mode`設定が`enabled: true`の場合に動作します。

## 統計情報

変換統計に `converted_no_column_list: 3` がカウントされるはずです。


