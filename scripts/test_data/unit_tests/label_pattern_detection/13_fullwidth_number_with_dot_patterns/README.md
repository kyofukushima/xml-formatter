# 13_fullwidth_number_with_dot_patterns

## テスト内容

全角数字 + 全角ドット（．）パターンの検証テストです。各パターンは1個ずつ含まれます。

## 含まれるパターン

- **全角数字 + ．**: `２．`, `１．`, `１０．` (各1個)
- **ドット区切り数字パターンとの区別**: `４．３．２．１`, `４．３．２`, `４．１` (各1個)

## 期待される動作

各パターンがItemレベルとして扱われます。全角数字の後に全角ドット（`．`）が続くパターンが正しく認識されることを確認します。

また、ドット区切り数字パターン（`dot_separated_number_*`）と正しく区別されることを確認します。

## 階層構造

```
Item Num="1": ２．
Item Num="2": １．
Item Num="3": １０．
Item Num="4": ４．３．２．１ (dot_separated_number_triple)
Item Num="5": ４．３．２ (dot_separated_number_double)
Item Num="6": ４．１ (dot_separated_number_single)
```

## 優先順位の確認

- `dot_separated_number_triple` (`４．３．２．１`) が最も優先される
- `dot_separated_number_double` (`４．３．２`) が次に優先される
- `dot_separated_number_single` (`４．１`) が次に優先される
- `fullwidth_number_with_dot` (`２．`, `１．`, `１０．`) が最後に評価される

これにより、より長いパターンが先にマッチし、正しく区別されます。

## 注意事項

- 全角数字は全角数字（`０-９`）を対象とします
- ドットは全角ドット（`．`）または半角ドット（`.`）を使用します
- このパターンは `dot_separated_number_*` パターンより後に評価されるため、優先順位が正しく設定されている必要があります
