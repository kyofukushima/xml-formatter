# 06_process2_split_and_aggregate

## テスト内容

処理2: Item要素の弟要素を順次処理（取り込みまたは分割）

## 期待される動作

- 最初のList「（１）」が処理1でItemに変換される
- 次のList「（２）」は同じ階層ラベルなので分割され、新しいItem Num="2"になる
- 最後のColumnなしListは下位階層なので、Item Num="1"に取り込まれる

## 詳細な処理フロー

1. **処理1**: 最初のList → Item Num="1" 作成
2. **処理2**: 次のList「（２）」は同じ階層 → 分割してItem Num="2"作成
3. **処理2**: 最後のColumnなしListは下位階層 → Item Num="1"に取り込み

## 統計情報

変換統計:
- `converted_labeled_list_to_item: 2` (2つのラベル付きListが変換された)
- `converted_no_column_list: 0` (ColumnなしListは変換されず取り込まれた)

## 注意点

このテストケースは分割と取り込みの両方のロジックを検証します。
