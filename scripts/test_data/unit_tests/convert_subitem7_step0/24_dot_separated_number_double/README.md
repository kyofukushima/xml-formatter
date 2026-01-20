# 24_dot_separated_number_double

## テスト内容

新規ラベルパターン4: ドット区切り数字（ドット2つ） (`４．３．２`形式)

## 期待される動作

- Subitem2要素内のList要素で、1つ目のColumnに「４．３．２」「４．３．３」などのドット2つで区切られた数字のラベルがある
- このListがSubitem7要素に変換される
- 1つ目のColumnの内容（例：「４．３．２」）がSubitem7Titleに配置される
- 2つ目のColumnの内容がSubitem7Sentenceに配置される

## 誤認識防止の検証

以下のパターンは**変換されずにList要素のまま残る**ことを確認：
- `４．１` - ドット区切り数字（ドット1つ）（別の新規パターン）
- `４` - 単一の全角数字（`fullwidth_number`）
- `４．３` - ドット1つだが異なる数字（ドット1つのパターンに該当しない）

## ColumnなしListの検証

- Subitem2要素内のColumnなしListは、前のSubitem7要素（ColumnありListから変換されたSubitem7）にList要素として追加されることを確認
