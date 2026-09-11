# 20_paren_note_patterns

## テスト内容

括弧付き注・※パターンの検証テストです。

## 含まれるパターン

- **括弧付き注＋全角数字**（`paren_note_fullwidth_number`）: `（注１）`, `（注２）`
- **括弧付き※＋全角数字**（`paren_asterisk_fullwidth_number`）: `（※１）`, `（※２）`
- **括弧付き注（番号なし）**（`paren_note_bare`、`repeatable_label_ids` 登録）: `（注）` ×2
- **括弧付き※（番号なし）**（`paren_asterisk_bare`、`repeatable_label_ids` 登録）: `（※）` ×2

## 期待される動作

- 括弧付きの注・※が丸括弧見出し（`subject_label_round`）ではなく専用ラベルとして認識される。番号なしの `（注）` `（※）` は繰り返されても同じ階層（兄弟）に並ぶ

## 階層構造

```
Item Num="1": （注１） 括弧付き注1
Item Num="2": （注２） 括弧付き注2
  └─ Subitem1 Num="1": （※１） 括弧付き※1
  └─ Subitem1 Num="2": （※２） 括弧付き※2
    └─ Subitem2 Num="1": （注） 番号なしの括弧付き注A
    └─ Subitem2 Num="2": （注） 番号なしの括弧付き注B
      └─ Subitem3 Num="1": （※） 番号なしの括弧付き※A
      └─ Subitem3 Num="2": （※） 番号なしの括弧付き※B
```
