# convert_subitem2_step1.py 単体テストデータ

`convert_subitem2_step1.py` の単体テスト用データ群です。各テストケースは以下の構造になっています：

- `input.xml`: テスト入力データ
- `expected.xml`: 期待される出力結果

## XML構造について

convert_subitem2_step1.pyはSubitem1要素内のSubitem2要素を処理するため、テストデータの構造は以下の通りです：

```
Item > Subitem1 > Subitem2
```

## テストケース一覧

### 01_no_split
**テスト内容**: 処理対象となる条件を満たさない場合
- Subitem1Sentenceの直後に通常のSubitem2（Subitem2Titleにテキストがある）がある
- コンテナSubitem2ではないため、処理対象とならない
- 出力結果は入力と同じ

### 02_split_by_column
**テスト内容**: ColumnありListによるSubitem2分割
- Subitem1Sentenceの直後にコンテナSubitem2がある
- Subitem2内にColumnありListが存在する
- ColumnありListの位置でSubitem2が2つに分割される
- 分割後はSubitem2番号が再採番される

### 03_split_by_subject_bracket
**テスト内容**: 科目名括弧によるSubitem2分割
- Subitem1Sentenceの直後にコンテナSubitem2がある
- Subitem2内に科目名括弧（〔医療と社会〕）が存在する
- 科目名括弧の位置でSubitem2が2つに分割される
- 分割後はSubitem2番号が再採番される

### 04_target_first_subitem2_only
**テスト内容**: Subitem1Sentence直後に通常Subitem2、その後にコンテナSubitem2がある場合
- 最初のSubitem2のみが処理対象となることを確認
- 最初のSubitem2が通常Subitem2のため、2番目のコンテナSubitem2は処理されない
- 出力結果は入力と同じ

## 実行方法

各テストケースの実行は以下のコマンドで行います：

```bash
cd scripts/test_data/unit_tests/convert_subitem2_step1/{テストケース名}
python ../../../../convert_subitem2_step1.py input.xml output.xml
```

出力結果 `output.xml` と `expected.xml` を比較してください。
