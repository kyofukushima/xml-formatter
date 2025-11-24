# convert_subitem3_step0.py 単体テスト

Subitem2要素内のList要素をSubitem3要素に変換する処理のテストケースです。

## テストケース一覧

### 01_process1_branch1_column_list
- **概要**: ColumnありListをSubitem3に変換
- **入力**: Subitem2内にColumnありList（ラベル付き）
- **期待結果**: ColumnありListがSubitem3要素に変換される

### 02_process1_branch2_2_subject_bracket
- **概要**: 科目名括弧を含むColumnなしListをSubitem3に変換
- **入力**: Subitem2内に科目名括弧（〔医療と社会〕）を含むList
- **期待結果**: 科目名括弧がSubitem3Sentenceに設定される

### 03_process1_branch2_4_no_column_list
- **概要**: ColumnなしListをSubitem3内に保持
- **入力**: Subitem2内にColumnなしList
- **期待結果**: ColumnなしListがSubitem3内のListとして保持される

### 04_process2_split_and_aggregate
- **概要**: 複数のList要素の分割と集約
- **入力**: Subitem2内に複数のColumnありList
- **期待結果**: 最初のListがSubitem3に変換され、2番目のListはそのSubitem3内に保持される

### 06_process1_branch1_circled_number
- **概要**: 丸数字（①）をラベルとして扱うColumnありListをSubitem3に変換
- **入力**: Subitem2内にColumnありList（1つ目のColumnに丸数字「①」）
- **期待結果**: ColumnありListがSubitem3要素に変換され、「①」がSubitem3Titleに設定される

### 07_process2_multiple_circled_numbers
- **概要**: 複数の丸数字（①、②、③）をラベルとして扱うColumnありListを複数のSubitem3に変換
- **入力**: Subitem2内に複数のColumnありList（各Listの1つ目のColumnに丸数字）
- **期待結果**: 各ColumnありListが個別のSubitem3要素に変換され、丸数字がSubitem3Titleに設定される

