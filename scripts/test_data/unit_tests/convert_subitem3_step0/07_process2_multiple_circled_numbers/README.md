# 07_process2_multiple_circled_numbers

## 概要
複数の丸数字（①、②、③）をラベルとして扱うColumnありListを複数のSubitem3に変換するテストケース

## 入力
- Subitem2内に複数のColumnありList
- 各Listの1つ目のColumnに丸数字（①、②、③）が含まれる
- 各Listの2つ目のColumnに内容が含まれる

## 期待結果
- 各ColumnありListが個別のSubitem3要素に変換される
- 1つ目のListの「①」がSubitem3Titleに設定される
- 2つ目のListの「②」がSubitem3Titleに設定される
- 3つ目のListの「③」がSubitem3Titleに設定される
- 各Subitem3のNum属性が1、2、3と連番で設定される

