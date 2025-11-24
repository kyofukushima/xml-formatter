# 07_process_mixed_grade_patterns

## テスト内容

学年パターン同士および科目名が混在する場合の処理

## 期待される動作

- 最初の学年（1つ記載）「〔第１学年〕」が処理1でSubitem1 Num="1"に変換される
- 次の学年（2つ記載）「〔第３学年及び第４学年〕」は同じ種類なので取り込まれ、Subitem1 Num="1"の子要素になる
- 最後の科目名「〔国語〕」は異なる種類なので取り込まれ、Subitem1 Num="1"の子要素になる

## 詳細な処理フロー

1. **処理1**: 学年（1つ記載） → Subitem1 Num="1" 作成
2. **処理2**: 学年（2つ記載） → 同じ階層判定 → Subitem1 Num="1"に取り込み
3. **処理2**: 科目名 → 異なる階層判定 → Subitem1 Num="1"に取り込み

## 統計情報

変換統計:
- `converted_grade_single_list_to_subitem1: 1` (学年（1つ記載）が変換された)
- `converted_grade_double_list_to_subitem1: 0` (学年（2つ記載）は変換されず取り込まれた)
- `converted_subject_name_list_to_subitem1: 0` (科目名は変換されず取り込まれた)

## 注意点

学年パターン同士は同じ階層として扱われ、最初の学年パターンのSubitem1に他の学年パターンのListが取り込まれます。科目名は異なる階層として扱われます。
