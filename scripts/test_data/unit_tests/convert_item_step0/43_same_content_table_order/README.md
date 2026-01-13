# 43_same_content_table_order

## テスト内容

Item要素の変換処理において、同じ内容のTableStructが複数ある場合でも、順序が正しく保持されることを確認するテストです。

## テストケース

- **入力ファイル**: `input.xml`
- **期待値ファイル**: `expected.xml`

## 検証ポイント

1. Paragraph要素内のList要素がItem要素に変換される
2. 変換前のParagraph要素内に、同じ内容のTableStructが2つ存在する
3. 変換後も、TableStructの順序が正しく保持される（最初のTableStructはParagraph要素内に残り、2つ目のTableStructはItem要素内に移動する）

## 問題点

同じ内容のTableStructが複数ある場合、順序が変わっても検知できない可能性があります。

## 改善案

1. TableStructの位置情報を含める（前後の要素の情報を含める）
2. TableStructの識別子に、前後の要素の情報を含める
3. より詳細な比較を行う
