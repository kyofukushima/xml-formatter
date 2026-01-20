# 23_dot_separated_number_single

## テスト内容

新規ラベルパターン3: ドット区切り数字（ドット1つ） (`４．１`形式)

## 期待される動作

- Item要素内のList要素で、1つ目のColumnに「４．１」「４．２」などのドット1つで区切られた数字のラベルがある
- このListがSubitem1要素に変換される
- 1つ目のColumnの内容（例：「４．１」）がSubitem1Titleに配置される
- 2つ目のColumnの内容がSubitem1Sentenceに配置される

## 誤認識防止の検証

以下のパターンは**変換されずにList要素のまま残る**ことを確認：
- `４` - 単一の全角数字（`fullwidth_number`）
- `４．３．２` - ドット区切り数字（ドット2つ）（別の新規パターン）
- `（４）` - 括弧付き数字（`paren_fullwidth_number`）

## ColumnなしListの検証

- Item要素内のColumnなしListは、前のSubitem1要素（ColumnありListから変換されたSubitem1）にList要素として追加されることを確認
