# ParagraphCaption要素の保持テスト

## テスト内容

このテストケースは、Paragraph要素にParagraphCaption要素が存在する場合、変換処理後もParagraphCaption要素が正しく保持されることを確認します。

## 入力

- Paragraph要素にParagraphCaption要素が存在
- ParagraphSentenceの後にList要素が存在
- List要素はColumnありのラベル付きList

## 期待される動作

1. List要素がItem要素に変換される
2. ParagraphCaption要素が保持される（削除されない）
3. ParagraphCaption要素が正しい順序で配置される（ParagraphNumの前）

## 検証ポイント

- ParagraphCaption要素が出力XMLに存在する
- ParagraphCaption要素の内容が正しい
- ParagraphCaption要素がParagraphNumの前に配置されている

