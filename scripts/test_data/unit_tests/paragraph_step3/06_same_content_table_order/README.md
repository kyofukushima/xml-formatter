# 06_same_content_table_order

## テスト内容

Paragraph要素の分割処理において、同じ内容のTableStructが複数ある場合でも、順序が正しく保持されることを確認するテストです。

## テストケース

- **入力ファイル**: `input.xml`
- **期待値ファイル**: `expected.xml`

## 検証ポイント

1. Paragraph要素が「２」のList要素で分割される
2. 分割前のParagraph要素内に、同じ内容のTableStructが2つ存在する
3. 分割後も、TableStructの順序が正しく保持される（最初のTableStructは最初のParagraphに、2つ目のTableStructは2つ目のParagraphに移動する）

## 問題点

同じ内容のTableStructが複数ある場合、順序が変わっても検知できない可能性があります。

## 改善案

1. TableStructの位置情報を含める（前後の要素の情報を含める）
2. TableStructの識別子に、前後の要素の情報を含める
3. より詳細な比較を行う
