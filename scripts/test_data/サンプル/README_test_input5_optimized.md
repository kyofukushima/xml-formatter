# test_input5_optimized.xml について

## 概要
`test_input5_optimized.xml`は、元の`test_input5.xml`（実データから作成された教育関連の告示文XML）から、テスト用に最適化されたコンパクト版です。

## 最適化の結果

| 項目 | 元ファイル | 最適化版 | 削減率 |
|------|-----------|---------|--------|
| 要素数 | 4,078 | 166 | **95.9%削減** |
| 行数 | 6,678 | 263 | **96.1%削減** |

## 保持した構造

### 第1章 総則
- **第1節 教育目標**: 完全保持
  - 2カラムのList構造（番号付き項目）
  - Ruby（ふりがな）要素
  
- **第2節 教育課程の編成**: 第1款のみ保持
  - ParagraphSentence + List の組み合わせ
  - 複数階層の段落番号付きList構造（(1), (2), (3)など）
  - 長文のテキスト要素

### 第2章 各教科
- **第1節**: 第1-2款のみ保持
  - 各款から1つのArticleを抽出
  - 最大5個のList要素に制限

## 保持した検証用パターン

この最適化版には、以下のような重要なパターンが含まれています：

1. **2カラムのList構造**
   ```xml
   <List>
     <ListSentence>
       <Column Num="1"><Sentence>１</Sentence></Column>
       <Column Num="2"><Sentence>本文...</Sentence></Column>
     </ListSentence>
   </List>
   ```

2. **Ruby（ふりがな）要素**
   ```xml
   <Ruby>涵<Rt>かん</Rt></Ruby>
   ```

3. **ParagraphSentence + List の組み合わせ**
   ```xml
   <Paragraph>
     <ParagraphNum>１</ParagraphNum>
     <ParagraphSentence>...</ParagraphSentence>
     <List>...</List>
     <List>...</List>
   </Paragraph>
   ```

4. **階層的な番号体系**
   - 1, 2, 3...
   - (1), (2), (3)...
   - ①, ②, ③... (元ファイルに存在した場合)

## 使用方法

### テスト実行
```bash
# スキーマ検証
xmllint --noout --schema schema/kokuji20250320_asukoe.xsd \
  scripts/education_script/focused_converters/test_data/test_input5_optimized.xml

# Python スクリプトでの処理テスト
python3 scripts/your_converter.py \
  scripts/education_script/focused_converters/test_data/test_input5_optimized.xml
```

### 検証ポイント
- ✅ Listの再帰的処理が正しく動作するか
- ✅ Columnパターンの処理が適切か
- ✅ Ruby要素が正しく変換されるか
- ✅ ParagraphNumとListの組み合わせが正しく扱えるか
- ✅ 階層的な番号体系が保持されるか

## 注意事項

1. **スキーマエラー**: 元ファイル`test_input5.xml`に存在したスキーマエラーが、この最適化版にも引き継がれています。これは実データに基づく構造のため、意図的に保持しています。

2. **削りすぎ防止**: 約96%削減されていますが、以下の点に配慮しています：
   - 再帰処理の検証に必要な深さを維持
   - 異なるパターンの代表例を各1-2個ずつ保持
   - 特殊要素（Ruby、Column等）を確実に含める

3. **さらなる削減が必要な場合**: 第2章を完全に削除することで、さらに小さなテストデータにすることも可能です。

## 生成方法

最適化版は以下のスクリプトで生成されました：

```bash
python3 scripts/create_optimized_test_data.py
```

このスクリプトは：
- 第1章の代表的な構造を保持
- 第2章から各款の代表例を抽出
- 重複パターンを自動削減
- XML整形を実施

## 今後の展開

さらに特定のパターンに焦点を当てたテストデータが必要な場合は、`create_optimized_test_data.py`を参考に、カスタマイズしたバージョンを作成できます。
