# 17_halfwidth_closing_paren_dot_patterns

## テスト内容

半角の閉じ括弧・ピリオド付きパターンの検証テストです。

## 含まれるパターン

- **半角数字＋閉じ括弧**（`halfwidth_number_with_paren`）: `1)`, `2)`
- **半角小文字＋閉じ括弧**（`lowercase_alphabet_with_paren`）: `a)`, `b)`
- **カタカナ＋半角閉じ括弧**（`katakana_with_halfwidth_paren`）: `ア)`, `イ)`
- **半角小文字＋ピリオド**（`lowercase_alphabet_with_dot`）: `a.`, `b.`

## 期待される動作

- 全角版（`１）` `ａ）` `ア）` `ａ．`）と同じ構造で、半角版がそれぞれ別のラベルIDとして認識され、種類ごとに別の階層になる

## 階層構造

```
Item Num="1": 1) 半角数字閉じ括弧1
Item Num="2": 2) 半角数字閉じ括弧2
  └─ Subitem1 Num="1": a) 半角小文字閉じ括弧a
  └─ Subitem1 Num="2": b) 半角小文字閉じ括弧b
    └─ Subitem2 Num="1": ア) カタカナ半角閉じ括弧ア
    └─ Subitem2 Num="2": イ) カタカナ半角閉じ括弧イ
      └─ Subitem3 Num="1": a. 半角小文字ピリオドa
      └─ Subitem3 Num="2": b. 半角小文字ピリオドb
```
