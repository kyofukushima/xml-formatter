# convert_subitem2_step0.py 単体テストデータ

`convert_subitem2_step0.py` の単体テスト用データです。

## 処理概要

Subitem1要素内のList要素をSubitem2要素に変換するスクリプトです。

### 処理1: Subitem1Sentence直後の要素（最初の1つのみ）をSubitem2化

- **分岐1**: ColumnありList（2カラム）でラベルがある場合 → Subitem2TitleとSubitem2Sentenceに変換
- **分岐2-2**: 括弧付き科目名List → 空のSubitem2Titleと科目名をSubitem2Sentenceに
- **分岐2-3**: 括弧付き指導項目List → 空のSubitem2Titleと指導項目をSubitem2Sentenceに
- **分岐2-4**: ColumnなしList → Subitem2Sentenceに変換
- **分岐3**: 非List要素(TableStruct, FigStruct, StyleStruct) → Subitem2内要素に

### 処理2: Subitem2要素の弟要素を順次処理（取り込みまたは分割）

- 同じ階層判定による分割/取り込み

### 特別処理
- **親が空の場合**: Subitem1TitleとSubitem1Sentenceが両方空の場合、ColumnなしListをSubitem2化せずそのまま配置
- **Noneチェック**: last_subitem2がNoneの場合のAttributeError防止

## テストケース

| フォルダ | テスト内容 | 説明 |
|---------|-----------|------|
| 01_process1_branch1_column_list | ColumnありList（2カラム） → Subitem2変換 | ラベル付きColumnありListがSubitem2に変換されることをテスト |
| 02_process1_branch2_2_subject_bracket | 括弧付き科目名 → Subitem2変換 | 〔科目名〕形式のListがSubitem2に変換されることをテスト |
| 03_process1_branch2_3_instruction_bracket | 括弧付き指導項目 → Subitem2変換 | 〔指導項目〕形式のListがSubitem2に変換されることをテスト |
| 04_process1_branch2_4_no_column_list | ColumnなしList → Subitem2内List変換 | ColumnなしListがSubitem2内に配置されることをテスト |
| 05_process1_branch3_non_list | 非List要素 → Subitem2内要素変換 | TableStruct等の非List要素がSubitem2内に配置されることをテスト |
| 06_process2_split_and_aggregate | 分割/取り込みロジック | 処理2の分割と取り込みのロジックをテスト |
| 12_process2_split_and_aggregate_subject_bracket | convert_subitem1_step0結果検証 | convert_subitem1_step0のprocess2_split_and_aggregate_subject_bracket結果に対するSubitem2変換を検証 |
| 13_process2_split_and_grade1 | convert_subitem1_step0結果検証 | convert_subitem1_step0のprocess2_split_and_grade1結果に対するSubitem2変換を検証 |
| 14_process2_split_and_grade2 | convert_subitem1_step0結果検証 | convert_subitem1_step0のprocess2_split_and_grade2結果に対するSubitem2変換を検証 |
| 15_process2_split_and_instruction | convert_subitem1_step0結果検証 | convert_subitem1_step0のprocess2_split_and_instruction結果に対するSubitem2変換を検証 |

## 使用方法

各テストケースフォルダには以下のファイルが含まれます：

- `input.xml`: 変換前のXML
- `expected.xml`: 期待される変換結果
- `README.md`: そのテストケースの詳細説明

スクリプトのテスト実行例：
```bash
python3 ../../../convert_subitem2_step0.py input.xml output.xml
```
