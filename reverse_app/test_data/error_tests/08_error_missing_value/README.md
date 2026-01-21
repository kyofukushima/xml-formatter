# エラーテストケース: 値の欠落

## テスト目的
逆変換スクリプトが、変換後のファイルと値が欠落したファイルを比較して、値の欠落を検出できるかを検証します。

## テスト内容
- **input.xml**: 正常な階層構造のXML（Item → Subitem1 → Subitem2）
- **expected.xml**: 正常な変換後のXML（すべての要素が正しく変換されたList要素の並び）
- **error.xml**: 値が欠落した変換後のXML（Subitem2のList要素が欠落している）
- **output.xml**: 実際の変換結果（input.xmlを逆変換パイプラインで処理した結果）

## 検証フロー
1. `input.xml`を逆変換パイプラインで処理 → `output.xml`を生成
2. `output.xml`と`expected.xml`を比較 → 一致すれば正常な変換結果
3. `output.xml`と`error.xml`を比較 → 不一致を検出できればエラー検出成功

## 検証項目
1. 正常な変換結果が得られるか（output.xml == expected.xml）
2. 値の欠落を検出できるか（output.xml != error.xml）
3. 差分が正しく表示されるか
