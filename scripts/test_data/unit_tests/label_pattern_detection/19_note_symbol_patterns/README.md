# 19_note_symbol_patterns

## テスト内容

注・※パターンの検証テストです。

## 含まれるパターン

- **注記＋半角数字**（`note_with_number_halfwidth`）: `注記1`, `注記2`
- **注＋全角数字**（`note_fullwidth_number`）: `注１`, `注２`
- **※＋全角数字**（`asterisk_fullwidth_number`）: `※１`, `※２`
- **注（番号なし）**（`note_bare`、`repeatable_label_ids` 登録）: `注` ×3

## 期待される動作

- 番号付きの注・※は種類ごとに別の階層になる。番号なしの `注` は同じ値が繰り返されても「再スタート」とみなされず、`hierarchy_rules.repeatable_label_ids` により3つが同じ階層（兄弟）に並ぶ

## 階層構造

```
Item Num="1": 注記1 注記＋半角数字1
Item Num="2": 注記2 注記＋半角数字2
  └─ Subitem1 Num="1": 注１ 注＋全角数字1
  └─ Subitem1 Num="2": 注２ 注＋全角数字2
    └─ Subitem2 Num="1": ※１ ※＋全角数字1
    └─ Subitem2 Num="2": ※２ ※＋全角数字2
      └─ Subitem3 Num="1": 注 番号なしの注A
      └─ Subitem3 Num="2": 注 番号なしの注B
      └─ Subitem3 Num="3": 注 番号なしの注C
```
