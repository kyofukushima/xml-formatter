# test_input5.xml 変換結果の比較レポート

## 実行日時
2025年10月27日

## 比較対象
- **スクリプト出力**: `test_result5.xml` (convert_list_unified.py で生成)
- **期待される出力**: `test_output5.xml` (手動修正版)

## 主要な発見事項

### ✓ スクリプトの動作状況
- **XML構文**: test_result5.xmlは**構文的に正しい**XMLファイルです（xmllintチェック合格）
- **変換統計**:
  - 科目構造の変換数: 7
  - Paragraph構造の変換数: 12
  - 作成されたItem要素: 7
  - 作成されたParagraph要素: 18

### ⚠️ 期待される出力の問題
test_output5.xmlには**複数のXML構文エラー**があります：

1. **2735行目**: タグ不一致 (Subitem1を開いてSubitem2で閉じている)
2. **2839行目**: タグミス (`<Subitem3Num="4">` ではなく `<Subitem3 Num="4">` であるべき)
3. その他複数のタグ不一致エラー

これらのエラーにより、直接的な比較が不可能です。

## スクリプトの出力形式に関する重要な発見

### 科目構造（〔...〕形式）の扱い

**READMEに記載の期待される形式:**
```xml
<Item Num="1">
  <ItemTitle>〔臨床保健理療〕</ItemTitle>
  <ItemSentence><Sentence Num="1"></Sentence></ItemSentence>
  ...
</Item>
```

**スクリプトの実際の出力:**
```xml
<Item Num="7">
  <ItemTitle />  <!-- 空のタイトル -->
  <ItemSentence>
    <Sentence Num="1">〔医療と社会〕</Sentence>
  </ItemSentence>
  ...
</Item>
```

**根本原因:**
`convert_list_unified.py` の261-265行目で、科目タイトルをItemTitleではなく、ItemSentence内のSentenceとして配置するコードになっています：

```python
# 科目名の場合：ItemSentence/Sentenceに入れる（ItemTitleは空）
list_sentence = list_elem.find('.//ListSentence')
sentence_elem = list_sentence.find('.//Sentence') if list_sentence is not None else None
self.context['current_item'] = self.create_item_element_for_subject(sentence_elem, item_num)
```

これはREADMEの説明と矛盾しています。

## test_result5.xmlの構造分析

### 全体統計
- 総要素数: 3,218
- Article: 13個
- Paragraph: 31個
- Item: 107個
- Subitem1: 28個
- Subitem2: 83個
- Subitem3: 228個
- **List: 130個** (多くのList要素が未変換のまま残っている)

### 科目構造の確認
- 〔...〕形式のItemTitleは **0個**
- スクリプトは科目構造を変換していますが、〔...〕はItemSentence内に配置されています

### 未変換のList要素
- 第2条: 3個のList要素が残存
- 第3条: 94個のList要素が残存（最も多い）
- その他のArticleにも未変換のList要素が散在

これらのList要素は、スクリプトの判定ロジックに合致しなかったため、変換されずに残っています。

## 推奨事項

### 1. スクリプトの修正オプション

科目タイトルをItemTitleに配置するよう修正する場合：

**修正前 (261-265行目):**
```python
# 科目名の場合：ItemSentence/Sentenceに入れる（ItemTitleは空）
list_sentence = list_elem.find('.//ListSentence')
sentence_elem = list_sentence.find('.//Sentence') if list_sentence is not None else None
self.context['current_item'] = self.create_item_element_for_subject(sentence_elem, item_num)
```

**修正後の例:**
```python
# 科目名の場合：ItemTitleに入れる
list_sentence = list_elem.find('.//ListSentence')
sentence_elem = list_sentence.find('.//Sentence') if list_sentence is not None else None
subject_title = sentence  # 〔...〕のテキスト
self.context['current_item'] = self.create_item_element_with_title(subject_title, item_num)
```

ただし、`create_item_element_with_title`メソッドを新たに実装する必要があります。

### 2. READMEの更新オプション

現在のスクリプトの動作を正しいものとして、READMEを更新する：

```markdown
**変換後:**
```xml
<Item Num="1">
  <ItemTitle />  <!-- 空 -->
  <ItemSentence>
    <Sentence Num="1">〔臨床保健理療〕</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    ...
  </Subitem1>
</Item>
```

### 3. test_output5.xmlの修正

手動修正版のtest_output5.xmlに含まれる構文エラーを修正してから、再度比較を行う。

主なエラー箇所:
- 2735行目: `</Subitem2>` → 正しいタグに修正
- 2839行目: `<Subitem3Num="4">` → `<Subitem3 Num="4">`
- その他のタグ不一致を修正

### 4. 未変換List要素の確認

130個のList要素が未変換のまま残っています。これらの要素が：
- 意図的に残すべきものなのか
- スクリプトの判定ロジックを改善して変換すべきなのか

を確認する必要があります。

## 結論

1. **スクリプトは正常に動作しています**が、READMEの説明と実装に不一致があります
2. **test_output5.xmlには構文エラー**があるため、直接比較は不可能です
3. 科目タイトルの配置方法（ItemTitle vs ItemSentence）について、どちらが正しいか決定する必要があります
4. 多くのList要素が未変換のまま残っており、これらの処理方法を決定する必要があります

## 次のステップ

1. 科目タイトルの配置方法（ItemTitle vs ItemSentence）を決定
2. 必要に応じてスクリプトまたはREADMEを修正
3. test_output5.xmlの構文エラーを修正
4. 未変換のList要素について、変換すべきか判断し、必要に応じてスクリプトを改善
5. 修正後、再度比較を実施
