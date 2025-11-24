# convert_item_step1.py 単体テストデータ

`convert_item_step1.py` の単体テスト用データ群です。各テストケースは以下の構造になっています：

- `input.xml`: テスト入力データ
- `expected.xml`: 期待される出力結果

## テストケース一覧

### 01_no_split
**テスト内容**: 処理対象となる条件を満たさない場合
- ParagraphSentenceの直後に通常のItem（ItemTitleにテキストがある）がある
- コンテナItemではないため、処理対象とならない
- 出力結果は入力と同じ

### 02_split_by_column
**テスト内容**: ColumnありListによる分割
- ParagraphSentenceの直後にコンテナItemがある
- Item内にColumnありListが存在する
- ColumnありListの位置でItemが2つに分割される
- 分割後はItem番号が再採番される

### 03_split_by_subject_bracket
**テスト内容**: 科目名括弧による分割
- ParagraphSentenceの直後にコンテナItemがある
- Item内に科目名括弧（〔医療と社会〕）が存在する
- 科目名括弧の位置でItemが2つに分割される
- 分割後はItem番号が再採番される

### 04_target_first_item_only
**テスト内容**: 最初のItemのみが処理対象となることを確認
- ParagraphSentenceの直後に通常のItemがある
- その後にコンテナItemがある
- 仕様書により最初のItemのみが処理対象となるため、2番目のItemは処理されない
- 出力結果は入力と同じ

## 実行方法

各テストケースの実行は以下のコマンドで行います：

```bash
cd scripts/test_data/unit_tests/convert_item_step1/{テストケース名}
python ../../../../convert_item_step1.py input.xml output.xml
```

出力結果 `output.xml` と `expected.xml` を比較してください。
