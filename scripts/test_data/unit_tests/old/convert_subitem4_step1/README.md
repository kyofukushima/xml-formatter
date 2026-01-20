# convert_subitem4_step1.py 単体テスト

Subitem4要素の補正処理（分割処理）のテストケースです。

## テストケース一覧

### 01_no_split
- **概要**: 分割対象がない場合
- **入力**: 通常のSubitem4（分割対象なし）
- **期待結果**: 変更なし

### 02_split_by_column
- **概要**: ColumnありListによる分割
- **入力**: コンテナSubitem4内にColumnありList
- **期待結果**: Subitem4が2つに分割される（ColumnありListが2番目のSubitem4に移動）

### 03_split_by_subject_bracket
- **概要**: 科目名括弧による分割
- **入力**: コンテナSubitem4内に科目名括弧を含むList
- **期待結果**: Subitem4が2つに分割される（科目名括弧が2番目のSubitem4Sentenceに設定）

