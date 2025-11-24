# convert_item_step0.py 単体テストデータ

`convert_item_step0.py` の単体テスト用データです。

## 処理概要

Paragraph要素内のList要素をItem要素に変換するスクリプトです。

### 処理1: ParagraphSentence直後の要素（最初の1つのみ）をItem化

- **分岐1**: ColumnありListでラベルがある場合 → ItemTitleとItemSentenceに変換
- **分岐2-1-1**: 学年（2つ記載）List → 空のItemTitleと学年をItemSentenceに
- **分岐2-1-2**: 学年（1つ記載）List → 空のItemTitleと学年をItemSentenceに
- **分岐2-1**: ColumnなしList → ItemSentenceに変換
- **分岐2-2**: 括弧付き科目名List → 空のItemTitleと科目名をItemSentenceに
- **分岐2-3**: 括弧付き指導項目List → 空のItemTitleと指導項目をItemSentenceに
- **分岐3**: 非List要素(TableStruct, FigStruct, StyleStruct) → Item内要素に

### 処理2: Item要素の弟要素を順次処理（取り込みまたは分割）

- 同じ階層判定による分割/取り込み

## テストケース

| フォルダ | テスト内容 | 説明 |
|---------|-----------|------|
| 01_process1_branch1_column_list | ColumnありList → Item変換 | ラベル付きColumnありListがItemに変換されることをテスト |
| 02_process1_branch2_1_no_column_list | ColumnなしList → ItemSentence変換 | ColumnなしListがItemSentenceに変換されることをテスト |
| 03_process1_branch2_2_subject_bracket | 括弧付き科目名 → Item変換 | 〔科目名〕形式のListがItemに変換されることをテスト |
| 04_process1_branch2_3_instruction_bracket | 括弧付き指導項目 → Item変換 | 〔指導項目〕形式のListがItemに変換されることをテスト |
| 05_process1_branch3_non_list | 非List要素 → Item内要素変換 | TableStruct等の非List要素がItem内に配置されることをテスト |
| 06_process2_split_and_aggregate | 分割/取り込みロジック | 処理2の分割と取り込みのロジックをテスト |
| 07_process1_branch2_1_2_grade_single_bracket | 学年（1つ記載） → Item変換 | 〔第１学年〕形式のListがItemに変換されることをテスト |
| 08_process1_branch2_1_1_grade_double_bracket | 学年（2つ記載） → Item変換 | 〔第１学年及び第２学年〕形式のListがItemに変換されることをテスト |
| 09_process2_split_grade_patterns | 学年パターン分割ロジック | 学年パターン同士の分割と取り込みのロジックをテスト |
| 10_process_mixed_subject_instruction | 科目名と指導項目の混合処理 | 科目名と指導項目の混合における分割ロジックをテスト |

## 使用方法

各テストケースフォルダには以下のファイルが含まれます：

- `input.xml`: 変換前のXML
- `expected.xml`: 期待される変換結果
- `README.md`: そのテストケースの詳細説明

スクリプトのテスト実行例：
```bash
python3 ../../../convert_item_step0.py input.xml output.xml
```
