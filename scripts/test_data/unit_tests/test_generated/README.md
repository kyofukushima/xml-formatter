# テストケース自動生成スクリプト

`generate_subitem_tests.py`を使用して、`convert_item_step0`のテストケースをベースとして、`convert_subitem1_step0`から`convert_subitem10_step0`までのテストケースを自動作成できます。

## 使用方法

### 基本的な使用方法

```bash
cd scripts/test_data/unit_tests
python generate_subitem_tests.py
```

このコマンドを実行すると、`convert_item_step0`の全てのテストケースをベースとして、`convert_subitem1_step0`から`convert_subitem10_step0`までのテストケースが`test_generated`ディレクトリに生成されます。

### オプション

- `--output-dir OUTPUT_DIR`: 出力ディレクトリを指定（デフォルト: `test_generated`）
- `--test-case TEST_CASE_NAME`: 特定のテストケースのみ生成
- `--subitem-levels LEVELS`: 生成するsubitemレベルを指定（例: `1-10`, `1,2,3`）

### 使用例

```bash
# 全てのテストケースを生成
python generate_subitem_tests.py

# 特定のテストケースのみ生成
python generate_subitem_tests.py --test-case 26_column_list_non_label_first_column

# subitem1とsubitem2のみ生成
python generate_subitem_tests.py --subitem-levels 1,2

# 出力ディレクトリを指定
python generate_subitem_tests.py --output-dir my_tests
```

## 生成されるファイル

各テストケースについて、以下のファイルが生成されます：

- `input.xml`: 変換前のXML（親要素が追加され、List要素が配置される）
- `expected.xml`: 期待される変換結果（Item要素がSubitem要素に変換される）
- `README.md`: 元のテストケースのREADMEがコピーされる

## 注意事項

- 既存のテストケースは変更されません。新しいディレクトリに生成されます。
- 生成されたテストケースは、実際のテスト実行前に確認することを推奨します。
- XMLの形式（XML宣言、エンコーディングなど）は、既存のテストケースと若干異なる場合がありますが、内容は同じです。










