# ItemCaption要素の保持テスト

## テスト内容

このテストケースは、Item要素にItemCaption要素が存在する場合（将来の拡張に備えて）、変換処理後もItemCaption要素が正しく保持されることを確認します。

## 入力

- Item要素にItemCaption要素が存在
- ItemSentenceの後にList要素が存在
- List要素はColumnありのラベル付きList

## 期待される動作

1. List要素がSubitem1要素に変換される
2. ItemCaption要素が保持される（削除されない）
3. ItemCaption要素が正しい順序で配置される（ItemTitleの前）

## 検証ポイント

- ItemCaption要素が出力XMLに存在する
- ItemCaption要素の内容が正しい
- ItemCaption要素がItemTitleの前に配置されている

## 注意

現在のスキーマにはItemCaption要素は定義されていませんが、将来の拡張に備えたテストケースです。

