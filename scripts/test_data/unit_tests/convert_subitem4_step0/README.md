# convert_subitem4_step0.py 単体テスト

Subitem3要素内のList要素をSubitem4要素に変換する処理のテストケースです。

## テストケース一覧

### 01_process1_branch1_column_list
- **概要**: ColumnありListをSubitem4に変換
- **入力**: Subitem3内にColumnありList（ラベル付き）
- **期待結果**: ColumnありListがSubitem4要素に変換される

### 02_process1_branch2_2_subject_bracket
- **概要**: 科目名括弧を含むColumnなしListをSubitem4に変換
- **入力**: Subitem3内に科目名括弧（〔医療と社会〕）を含むList
- **期待結果**: 科目名括弧がSubitem4Sentenceに設定される

### 03_process1_branch2_4_no_column_list
- **概要**: ColumnなしListをSubitem4内に保持
- **入力**: Subitem3内にColumnなしList
- **期待結果**: ColumnなしListがSubitem4内のListとして保持される

### 04_process2_split_and_aggregate
- **概要**: 複数のList要素の分割と集約
- **入力**: Subitem3内に複数のColumnありList
- **期待結果**: 各Listが別々のSubitem4に変換される

### 05_process1_branch1_column_list_3columns
- **概要**: Columnが3つ以上あるList要素をSubitem4内に保持
- **入力**: Subitem3内にColumnが3つあるList
- **期待結果**: Columnが3つ以上あるListは、Subitem4要素内にそのまま保持される

