# convert_subitem1_step1.py 単体テストデータ

`convert_subitem1_step1.py` の単体テスト用データ群です。各テストケースは以下の構造になっています：

- `input.xml`: テスト入力データ
- `expected.xml`: 期待される出力結果

## テストケース一覧

### 01_no_split
**テスト内容**: 処理対象となる条件を満たさない場合
- ItemSentenceの直後に通常のSubitem1（Subitem1Titleにテキストがある）がある
- コンテナSubitem1ではないため、処理対象とならない
- 出力結果は入力と同じ

### 02_split_by_column
**テスト内容**: ColumnありListによるSubitem1分割
- ItemSentenceの直後にコンテナSubitem1がある
- Subitem1内にColumnありListが存在する
- ColumnありListの位置でSubitem1が2つに分割される
- 分割後はSubitem1番号が再採番される

### 03_split_by_subject_bracket
**テスト内容**: 科目名括弧がスキップされることを確認
- ItemSentenceの直後にコンテナSubitem1がある
- Subitem1内に科目名括弧（〔医療と社会〕）が存在する
- 仕様により科目名括弧はスキップ対象のため、分割されない
- 出力結果は入力と同じ

### 04_target_first_subitem1_only
**テスト内容**: 通常Subitem1とコンテナSubitem1が混在する場合
- ItemSentenceの直後に通常のSubitem1（Subitem1Titleにテキストがある）がある
- その後にコンテナSubitem1（Subitem1Titleが空）がある
- 通常のSubitem1は処理対象とならず、コンテナSubitem1のみが処理される
- 出力結果は入力と同じ

### 05_split_by_instruction
**テスト内容**: 指導項目括弧がスキップされることを確認
- ItemSentenceの直後にコンテナSubitem1がある
- Subitem1内に指導項目括弧（〔指導項目〕）が存在する
- 仕様により指導項目はスキップ対象のため、分割されない
- 出力結果は入力と同じ

### 06_split_by_grade1
**テスト内容**: 学年（１つ）括弧がスキップされることを確認
- ItemSentenceの直後にコンテナSubitem1がある
- Subitem1内に学年（１つ）括弧（〔第１学年〕）が存在する
- 仕様により学年（１つ）はスキップ対象のため、分割されない
- 出力結果は入力と同じ

### 07_split_by_grade2
**テスト内容**: 学年（２つ）括弧がスキップされることを確認
- ItemSentenceの直後にコンテナSubitem1がある
- Subitem1内に学年（２つ）括弧（〔第１学年及び第２学年〕）が存在する
- 仕様により学年（２つ）はスキップ対象のため、分割されない
- 出力結果は入力と同じ

## 実行方法

各テストケースの実行は以下のコマンドで行います：

```bash
cd scripts/test_data/unit_tests/convert_subitem1_step1/{テストケース名}
python ../../../../convert_subitem1_step1.py input.xml output.xml
```

出力結果 `output.xml` と `expected.xml` を比較してください。
