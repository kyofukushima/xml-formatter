# エラーテストケース: 順序変更

## テスト目的
逆変換スクリプトが、要素の順序変更（List要素、TableStruct、FigStructの順序）を検出できるかを検証します。

## テスト内容
- **input.xml**: 正常な階層構造のXML（Item → TableStruct → Subitem1 → Subitem2 → FigStruct → Subitem1-2）
- **expected.xml**: 正しい順序で変換されたList要素の並び（List → TableStruct → List → List → FigStruct → List）
- **error.xml**: 順序が変更された変換後のXML（List → List → FigStruct → TableStruct → List → List）

## 検証フロー
1. `input.xml`を逆変換パイプラインで処理 → `output.xml`を生成
2. `output.xml`と`expected.xml`を比較 → 一致すれば正常な変換結果
3. `output.xml`と`error.xml`を比較 → 不一致を検出できればエラー検出成功

## 検証項目
1. 正常な変換結果が得られるか（output.xml == expected.xml）
2. 順序変更を検出できるか（output.xml != error.xml）
3. TableStructとFigStructの順序も含めて検出できるか
