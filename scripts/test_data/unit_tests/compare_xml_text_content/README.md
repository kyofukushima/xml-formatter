# compare_xml_text_content.py 単体テスト

## 概要

`compare_xml_text_content.py`の単体テストです。同じ内容のTableStructが複数ある場合でも、順序の違いを検知できることを確認します。

## テストケース

### 01_same_content_table_order

TableStructTitleがある場合の順序検証テストです。

- **テストケース1**: 順序が正しい場合 → 検証成功
- **テストケース2**: 順序が間違っている場合 → 検証失敗（期待通り）

### 02_same_content_table_order_no_title

TableStructTitleがない場合の順序検証テストです。**現在の実装では検知できません**。

- **テストケース1**: 順序が正しい場合 → 検証成功
- **テストケース2**: 順序が間違っている場合 → 検証失敗（期待通り）**← 現在は失敗していない（問題あり）**

### 03_same_content_table_order_different_parent

同じ内容のTableStructが異なる位置に配置されている場合の検証テストです。**現在の実装では検知できません**。

- **テストケース1**: 位置が正しい場合 → 検証成功
- **テストケース2**: 位置が間違っている場合 → 検証失敗（期待通り）**← 現在は失敗していない（問題あり）**

## 実行方法

```bash
cd scripts/test_data/unit_tests/compare_xml_text_content
python3 run_tests.py
```

## 問題点

現在の`get_table_sequence`関数は、TableStructの最初の10個のテキストを結合した文字列で識別しているため、同じ内容のTableStructが複数ある場合、順序が変わっても検知できません。

## 改善案

1. TableStructの位置情報を含める（前後の要素の情報を含める）
2. TableStructの識別子に、前後の要素の情報を含める
3. より詳細な比較を行う
