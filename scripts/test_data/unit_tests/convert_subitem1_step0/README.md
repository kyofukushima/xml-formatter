# convert_subitem1_step0.py 単体テストデータ

`convert_subitem1_step0.py` の単体テスト用データです。

## 処理概要

Item要素内のList要素をSubitem1要素に変換するスクリプトです。

### 処理1: ItemSentence直後の要素（最初の1つのみ）をSubitem1化

- **分岐1**: ColumnありListでラベルがある場合 → Subitem1TitleとSubitem1Sentenceに変換
- **分岐2-2**: 括弧付き科目名List → 空のSubitem1Titleと科目名をSubitem1Sentenceに
- **分岐2-3**: 括弧付き指導項目List → 空のSubitem1Titleと指導項目をSubitem1Sentenceに
- **分岐2-4**: ColumnなしList → Subitem1Sentenceに変換、またはSubitem1内Listとして配置
- **分岐3**: 非List要素(TableStruct, FigStruct, StyleStruct) → Subitem1内要素に

### 処理2: Subitem1要素の弟要素を順次処理（取り込みまたは分割）

- 同じ階層判定による分割/取り込み

### 特別処理
- **親が空の場合**: ItemTitleとItemSentenceが両方空の場合、ColumnなしListをSubitem1化せずそのまま配置
- **Noneチェック**: last_subitem1がNoneの場合のエラーを防止

## テストケース

| フォルダ | テスト内容 | 説明 |
|---------|-----------|------|
| 01_process1_branch1_column_list | ColumnありList → Subitem1変換 | ラベル付きColumnありListがSubitem1に変換されることをテスト |
| 02_process1_branch2_2_subject_bracket | 括弧付き科目名 → Subitem1変換 | 〔科目名〕形式のListがSubitem1に変換されることをテスト |
| 03_process1_branch2_3_instruction_bracket | 括弧付き指導項目 → Subitem1変換 | 〔指導項目〕形式のListがSubitem1に変換されることをテスト |
| 04_process1_branch2_4_no_column_list | ColumnなしList → Subitem1内List変換 | ColumnなしListがSubitem1内に配置されることをテスト |
| 05_process1_branch3_non_list | 非List要素 → Subitem1内要素変換 | TableStruct等の非List要素がSubitem1内に配置されることをテスト |
| 06_process2_split_and_aggregate | 分割/取り込みロジック | 処理2の分割と取り込みの両方の動作をテスト |
| 07_process_mixed_subject_instruction | 科目名と指導項目の混合処理 | 科目名と指導項目の混合における分割ロジックをテスト |
| 08_process1_branch2_1_2_grade_single_bracket | 学年（1つ記載） → Subitem1変換 | 〔第１学年〕形式のListがSubitem1に変換されることをテスト |
| 09_process1_branch2_1_1_grade_double_bracket | 学年（2つ記載） → Subitem1変換 | 〔第１学年及び第２学年〕形式のListがSubitem1に変換されることをテスト |
| 10_process2_split_grade_patterns | 学年パターン分割ロジック | 学年パターン同士の分割と取り込みのロジックをテスト |
| 11_process2_split_and_aggregate_subject_bracket | 科目名パターン取り込みロジック | 科目名パターンのItemに対して異なる種類のList要素がすべてSubitem1に取り込まれることをテスト |
| 12_process2_split_and_aggregate_subject_bracket | convert_item_step0結果検証 | convert_item_step0のprocess2_split_and_aggregate_subject_bracket結果に対するSubitem1変換を検証 |
| 13_process2_split_and_grade1 | convert_item_step0結果検証 | convert_item_step0のprocess2_split_and_grade1結果に対するSubitem1変換を検証 |
| 14_process2_split_and_grade2 | convert_item_step0結果検証 | convert_item_step0のprocess2_split_and_grade2結果に対するSubitem1変換を検証 |
| 15_process2_split_and_instruction | convert_item_step0結果検証 | convert_item_step0のprocess2_split_and_instruction結果に対するSubitem1変換を検証 |

## 使用方法

各テストケースフォルダには以下のファイルが含まれます：

- `input.xml`: 変換前のXML
- `expected.xml`: 期待される変換結果
- `README.md`: そのテストケースの詳細説明

スクリプトのテスト実行例：
```bash
python3 ../../../convert_subitem1_step0.py input.xml output.xml
```
