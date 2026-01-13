# 42_table_struct_order_preservation

## テスト内容

TableStructの順序保持をテストします。TableStructが複数のItemの間に配置されている場合、元の位置を保持する必要があります。

## 期待される動作

- ParagraphSentence直後の最初のColumnなしListがItem要素に変換される
- TableStructは元の位置を保持し、Itemの子要素ではなく、Paragraphの直接の子要素として配置される
- TableStructの後のカラムなしリストは、それぞれ別々のItem要素に変換される（並列分割を継続）
- TableStructの順序が正しく保持される（表１、表２の順序）

## 修正前の問題

修正前は、TableStructが`append_to_last_child`で処理されていたため、最後のItemに追加され、順序が失われていました。

## 修正後の動作

修正後は、TableStructが`append_child`で処理されるため、元の位置を保持します。

## 設定

このテストケースは、`no_column_text_split_mode`設定が`enabled: true`の場合に動作します。

## 統計情報

変換統計に `converted_no_column_list: 3` がカウントされるはずです。
