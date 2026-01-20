# Article要素特化型変換スクリプトのテストケース

このディレクトリには、`convert_article_focused.py`のテストケースが含まれています。

## テストケース構造

各テストケースは独立したディレクトリに配置され、以下のファイルを含みます：

- `input.xml`: 変換前のXMLファイル
- `expected.xml`: 期待される変換結果のXMLファイル
- `output.xml`: テスト実行時に生成される出力ファイル（比較用）

## テストケース一覧

| ディレクトリ | テスト内容 | 説明 |
|------------|-----------|------|
| 01_pattern1_empty_title | ArticleTitleが空の場合 | ArticleTitleが空の場合は分割せず、そのまま保持される |
| 02_pattern2_split | 基本的な分割パターン | ArticleTitleが「第１」で、直接子要素としてList内に「第２」が出現する場合の分割 |
| 03_pattern3_no_title | ArticleTitleが存在しない場合 | ArticleTitleが存在しない場合、空のArticleTitleが追加される |
| 04_pattern4_multiple_split | 複数回の分割 | 第１→第２→第３と複数回分割される場合（再帰的処理の確認） |
| 05_pattern5_zenkaku_numbers | 全角数字パターン | 全角数字（第１、第２）でも正しく分割される |
| 06_pattern6_kanji_numbers | 漢数字パターン | 漢数字（第一、第二）でも正しく分割される |
| 07_pattern7_split_in_paragraph | Paragraph内のList要素に分割点がある場合 | Paragraph内のList要素でも正しく分割される |
| 08_pattern8_no_split_point | ArticleTitleが「第○」パターンだが分割点がない場合 | 分割されず、そのまま保持される |
| 09_pattern9_non_boundary_title | ArticleTitleが「第○」パターンでない場合 | ArticleTitleが「第1条」など「第○」パターンでないため分割されない |
| 10_pattern10_multiple_paragraphs | 複数のParagraphがある場合の分割 | 2番目のParagraph内の分割点で正しく分割される |
| 11_pattern11_multiple_lists_in_paragraph | 分割点の前後に複数のList要素がある場合 | 分割点より前のList要素は前半のArticleに、後のList要素は後半のArticleに正しく配置される |
| 12_pattern12_same_title_no_split | 同じタイトルが出現しても分割しない場合 | ArticleTitleと同じラベルが出現しても分割されない（現在のタイトルと異なる場合のみ分割） |

## テストの実行方法

### 単体テストスクリプトを使用する方法（推奨）

`run_tests.py`を使用してすべてのテストケースを一括実行できます：

```bash
cd /Users/fukushima/Documents/xml_anken/education_xml/scripts/test_data/unit_tests/article_focused
python run_tests.py
```

このスクリプトは以下の処理を行います：
1. `01_`, `02_`, ... で始まるディレクトリを検索
2. 各テストケースの`input.xml`に対して`convert_article_focused.py`を実行
3. 出力結果（`output.xml`）を`expected.xml`と比較
4. 差分を表示

### 個別にテストケースを実行する方法

各テストケースに対して、以下のコマンドでスクリプトを実行できます：

```bash
cd /Users/fukushima/Documents/xml_anken/education_xml/scripts
python convert_article_focused.py test_data/unit_tests/article_focused/01_pattern1_empty_title/input.xml test_data/unit_tests/article_focused/01_pattern1_empty_title/output.xml
```

## 期待値ファイルの更新

テストケースの期待値を更新する場合：

1. テストケースを実行して出力を確認
2. 正しい出力が得られたら、それを期待値ファイルとして保存：

```bash
cd /Users/fukushima/Documents/xml_anken/education_xml/scripts/test_data/unit_tests/article_focused/01_pattern1_empty_title
cp output.xml expected.xml
```

## 期待される動作のまとめ

| パターン | ArticleTitle | 分割点 | 動作 |
|---------|-------------|--------|------|
| パターン1 | 空 | - | 分割しない |
| パターン2 | 「第○」 | あり（異なる「第○」） | 分割する |
| パターン3 | なし | - | 空のArticleTitleを追加 |
| パターン4 | 「第１」 | 「第２」「第３」 | 3つに分割（再帰的） |
| パターン5 | 「第１」 | 「第２」（全角） | 分割する |
| パターン6 | 「第一」 | 「第二」（漢数字） | 分割する |
| パターン7 | 「第１」 | Paragraph内List | 分割する |
| パターン8 | 「第１」 | なし | 分割しない |
| パターン9 | 「第1条」 | 「第２」 | 分割しない（パターン不一致） |
| パターン10 | 「第１」 | 複数Paragraph内 | 分割する |
| パターン11 | 「第１」 | 複数List内 | 分割する |
| パターン12 | 「第１」 | 「第１」（同じ） | 分割しない |
