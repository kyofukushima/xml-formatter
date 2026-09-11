# 18_halfwidth_dot_separated_number_patterns

## テスト内容

半角のドット区切り数字・範囲パターンの検証テストです。

## 含まれるパターン

- **ドット区切り半角数字（ドット1つ）**（`dot_separated_halfwidth_number_single`）: `4.1`, `4.2`
- **ドット区切り半角数字（ドット2つ）**（`dot_separated_halfwidth_number_double`）: `4.3.1`, `4.3.2`
- **半角数字＋ピリオド**（`halfwidth_number_with_dot`）: `2.`, `3.`
- **半角数字の範囲**（`number_range_hyphen_halfwidth`）: `1-3`, `4-6`

## 期待される動作

- 全角版（`４．１` `４．３．１` `２．` `１―３`）と同じ構造で、半角版がそれぞれ別のラベルIDとして認識され、種類ごとに別の階層になる

## 階層構造

```
Item Num="1": 4.1 半角ドット区切り4.1
Item Num="2": 4.2 半角ドット区切り4.2
  └─ Subitem1 Num="1": 4.3.1 半角ドット区切り4.3.1
  └─ Subitem1 Num="2": 4.3.2 半角ドット区切り4.3.2
    └─ Subitem2 Num="1": 2. 半角数字ピリオド2.
    └─ Subitem2 Num="2": 3. 半角数字ピリオド3.
      └─ Subitem3 Num="1": 1-3 半角数字範囲1-3
      └─ Subitem3 Num="2": 4-6 半角数字範囲4-6
```
