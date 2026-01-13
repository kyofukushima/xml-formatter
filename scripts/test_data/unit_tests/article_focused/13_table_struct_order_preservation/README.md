# 13_table_struct_order_preservation

## テスト内容

Article要素の分割処理において、TableStructの順序保持をテストします。Article要素が分割される際に、TableStructが正しい位置に配置されることを確認します。

## 期待される動作

- Article要素が「第２」のラベルで分割される
- 分割前のArticle（第１）には、最初のTableStruct（表１）が含まれる
- 分割後のArticle（第２）には、2つ目のTableStruct（表２）が含まれる
- TableStructの順序が正しく保持される（表１、表２の順序）

## 注意事項

- TableStructは、分割前のArticleと分割後のArticleの両方に正しく配置される必要があります
- TableStructの順序が失われないことを確認します
