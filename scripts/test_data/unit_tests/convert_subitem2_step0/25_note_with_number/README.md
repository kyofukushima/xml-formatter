# 25_note_with_number

## テスト内容

新規ラベルパターン5: 注記 + 数字 (`注記１`形式)

## 期待される動作

- Subitem1要素内のList要素で、1つ目のColumnに「注記１」「注記２」などの注記 + 数字のラベルがある
- このListがSubitem2要素に変換される
- 1つ目のColumnの内容（例：「注記１」）がSubitem2Titleに配置される
- 2つ目のColumnの内容がSubitem2Sentenceに配置される

## 誤認識防止の検証

以下のパターンは**変換されずにList要素のまま残る**ことを確認：
- `注記` - 数字なしの注記（ラベルパターンに該当しない）
- `注記（１）` - 注記 + 括弧付き数字（ラベルパターンに該当しない）
- `注記１）` - 注記 + 数字 + ）（ラベルパターンに該当しない）

## ColumnなしListの検証

- Subitem1要素内のColumnなしListは、前のSubitem2要素（ColumnありListから変換されたSubitem2）にList要素として追加されることを確認
