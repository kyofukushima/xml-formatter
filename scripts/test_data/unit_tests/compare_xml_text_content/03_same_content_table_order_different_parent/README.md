# 03_same_content_table_order_different_parent

## テスト内容

同じ内容のTableStructが異なる親要素に配置されている場合でも、位置の違いを検知できることを確認するテストです。

## テストケース

### テストケース1: 同じ内容のTableStructが同じ位置に配置されている場合

- **入力ファイル**: `input_original.xml` と `input_final_correct.xml`
- **期待値**: 検証成功（位置が正しい）

### テストケース2: 同じ内容のTableStructの位置が変更されている場合

- **入力ファイル**: `input_original.xml` と `input_final_incorrect.xml`
- **期待値**: 検証失敗（位置の違いを検知）

## 問題点

現在の`get_table_sequence`関数は、TableStructの最初の10個のテキストを結合した文字列で識別しているため、同じ内容のTableStructが複数ある場合、位置が変わっても検知できません。

このテストケースでは、TableStructTitleがないため、内容が完全に同じTableStructが2つあります。位置が変更された場合（間にList要素が追加された場合）、検知できる必要があります。

## 改善案

1. TableStructの位置情報を含める（前後の要素の情報を含める）
2. TableStructの識別子に、前後の要素の情報を含める
3. より詳細な比較を行う
