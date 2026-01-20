# convert_item_step0 テストケース分析レポート

## 実装されているロジック

### 処理1: ParagraphSentence直後の要素（最初の1つのみ）をItem化

#### 分岐1: ColumnありListでラベルがある場合
- **分岐1**: Columnが2つでラベル付き → ItemTitleとItemSentenceに変換
- **分岐1-1**: Columnが2つで最初がテキスト → Sentence要素2つに変換
- **分岐1-2**: Columnが3つ以上で最初がラベル → ItemTitleと複数Sentenceに変換
- **分岐1-3**: Columnが3つ以上で最初がテキスト → ItemTitleと複数Sentenceに変換

#### 分岐2: ColumnなしList
- **分岐2-1-1**: 学年（2つ記載）List → 空のItemTitleと学年をItemSentenceに
- **分岐2-1-2**: 学年（1つ記載）List → 空のItemTitleと学年をItemSentenceに
- **分岐2-2**: 括弧付き科目名List → 空のItemTitleと科目名をItemSentenceに
- **分岐2-3**: 括弧付き指導項目List → 空のItemTitleと指導項目をItemSentenceに
- **分岐2-4**: ColumnなしList（その他） → ItemSentenceに変換

#### 分岐3: 非List要素
- **分岐3**: 非List要素(TableStruct, FigStruct, StyleStruct) → Item内要素に

### 処理2: Item要素の弟要素を順次処理（取り込みまたは分割）
- 同じ階層判定による分割/取り込み
- 学年パターン同士の分割
- 科目名と指導項目の混合処理
- ラベル重複時の処理

## テストケースと実装ロジックの対応関係

| テストケース | テスト内容 | 対応する実装ロジック | 状態 |
|------------|----------|-------------------|------|
| 01_process1_branch1_column_list | ColumnありList → Item変換 | 処理1-分岐1 | ✅ |
| 02_process1_branch2_1_no_column_list | ColumnなしList → ItemSentence変換 | 処理1-分岐2-4 | ✅ |
| 03_process1_branch2_2_subject_bracket | 括弧付き科目名 → Item変換 | 処理1-分岐2-2 | ✅ |
| 04_process1_branch2_3_instruction_bracket | 括弧付き指導項目 → Item変換 | 処理1-分岐2-3 | ✅ |
| 05_process1_branch3_non_list | 非List要素 → Item内要素変換 | 処理1-分岐3 | ✅ |
| 06_process2_split_and_aggregate | 分割/取り込みロジック | 処理2 | ✅ |
| 07_process1_branch2_1_2_grade_single_bracket | 学年（1つ記載） → Item変換 | 処理1-分岐2-1-2 | ✅ |
| 08_process1_branch2_1_1_grade_double_bracket | 学年（2つ記載） → Item変換 | 処理1-分岐2-1-1 | ✅ |
| 08_circled_number_in_item | 丸数字ラベル | 処理1-分岐1（特殊ラベル） | ✅ |
| 09_process2_split_grade_patterns | 学年パターン分割ロジック | 処理2（学年パターン分割） | ✅ |
| 10_process_mixed_subject_instruction | 科目名と指導項目の混合処理 | 処理2（混合処理） | ✅ |
| 12_process2_split_and_aggregate_subject_bracket | 科目名括弧の分割と集約 | 処理2（科目名分割） | ✅ |
| 13_process2_split_and_grade1 | 分割と学年1 | 処理2（学年分割） | ✅ |
| 14_process2_split_and_grade2 | 分割と学年2 | 処理2（学年分割） | ✅ |
| 15_process2_split_and_aggregate_instruction_bracket | 指導項目括弧の分割と集約 | 処理2（指導項目分割） | ✅ |
| 16_nocolumn_2 | Columnなし2 | 処理1-分岐2-4（複数） | ✅ |
| 17_no_content | コンテンツなし | 処理1-分岐2-4（空） | ✅ |
| 18_process1_branch1_column_list_3columns | ColumnありList（3列） | 処理1-分岐1-2または分岐1-3 | ✅ |
| 19_round_bracket_long_description | 丸括弧長い説明 | 処理2（丸括弧見出し） | ✅ |
| 20_empty_parent_create_item | 空の親要素でItem作成 | 処理1（空ParagraphでもItem作成） | ✅ |
| 21_fullwidth_lowercase_alphabet_with_paren | 全角小文字アルファベット括弧付き | 処理1-分岐1（特殊ラベル） | ✅ |
| 22_fullwidth_number_with_paren | 全角数字括弧付き | 処理1-分岐1（特殊ラベル） | ✅ |
| 23_dot_separated_number_single | ドット区切り数字単一 | 処理1-分岐1（特殊ラベル） | ✅ |
| 24_dot_separated_number_double | ドット区切り数字二重 | 処理1-分岐1（特殊ラベル） | ✅ |
| 25_note_with_number | 数字付き注記 | 処理1-分岐1（特殊ラベル） | ✅ |
| 26_column_list_non_label_first_column | Columnリスト非ラベル最初のColumn | 処理1-分岐1-1（2列、テキスト） | ✅ |
| 27_column_list_three_or_more_with_label | Columnリスト3つ以上ラベル付き | 処理1-分岐1-2（3列以上、ラベル） | ✅ |
| 28_duplicate_label_keep_as_list | 重複ラベルをリストとして保持 | 処理2（ラベル重複処理） | ✅ |
| 29_instruction_bracket_duplicate | 指導項目括弧重複 | 処理2（指導項目重複） | ✅ |
| 30_dot_separated_number_with_alphabet_children | ドット区切り数字とアルファベット子要素 | 処理2（ドット区切り数字とアルファベット） | ✅ |

## 不足している可能性のあるテストケース

### 処理1の分岐で不足している可能性があるケース

1. **Columnが3つ以上で最初が空の場合**
   - 実装: `create_element_from_list`で変換をスキップ（そのままList要素として残す）
   - テストケース: ❌ 不足

2. **Columnが2つで最初がテキストの場合（処理1-分岐1-1）**
   - 実装: Sentence要素2つに変換
   - テストケース: ✅ 26_column_list_non_label_first_column でカバー

3. **Columnが3つ以上で最初がテキストの場合（処理1-分岐1-3）**
   - 実装: ItemTitleと複数Sentenceに変換
   - テストケース: ✅ 27_column_list_three_or_more_with_label でカバー（一部）

### 処理2の分岐で不足している可能性があるケース

1. **Columnが3つ以上で最初がラベルでない場合の分割/取り込み**
   - 実装: `handle_multi_column_non_labeled_list`で処理
   - テストケース: ⚠️ 27_column_list_three_or_more_with_label で一部カバーされているが、分割/取り込みの詳細なテストが不足している可能性

2. **Columnが2つで最初がテキストの場合の分割/取り込み**
   - 実装: `handle_two_column_non_labeled_list`で処理
   - テストケース: ⚠️ 26_column_list_non_label_first_column で一部カバーされているが、分割/取り込みの詳細なテストが不足している可能性

## 推奨事項

### 追加すべきテストケース

1. **Columnが3つ以上で最初が空の場合のテスト**
   - 入力: Columnが3つ以上で最初のColumnが空のList
   - 期待値: List要素がそのまま残る（変換されない）

2. **Columnが3つ以上で最初がテキストの場合の分割/取り込みテスト**
   - 入力: 複数のColumnが3つ以上で最初がテキストのList要素
   - 期待値: 適切な分割/取り込みが行われる

3. **Columnが2つで最初がテキストの場合の分割/取り込みテスト**
   - 入力: 複数のColumnが2つで最初がテキストのList要素
   - 期待値: 適切な分割/取り込みが行われる

## 結論

現在のテストケースは、実装されているロジックの大部分をカバーしています。ただし、以下の点で不足があります：

1. **Columnが3つ以上で最初が空の場合のテストケースが不足**
2. **Columnが3つ以上で最初がテキストの場合の分割/取り込みの詳細なテストが不足**
3. **Columnが2つで最初がテキストの場合の分割/取り込みの詳細なテストが不足**

これらのテストケースを追加することで、より完全なテストカバレッジが得られます。










