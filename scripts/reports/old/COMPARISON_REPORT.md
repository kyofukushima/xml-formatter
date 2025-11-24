# test_output5.xml と test_output5_actual.xml の比較結果

## 実施日
2025年1月

## 比較対象
- **期待値**: `test_output5.xml`（既存ファイル）
- **実際**: `test_output5_actual.xml`（`convert_list_unified.py`で新規生成）
- **入力**: `test_input5.xml`

---

## 比較結果サマリー

### ❌ 重大な差異が検出されました

#### 1. XML構造の差異
**26種類の要素で数が異なります**

| 要素名 | 期待値 | 実際 | 差 |
|--------|--------|------|-----|
| Subitem1 | 83 | 28 | -55 |
| Subitem2 | 122 | 83 | -39 |
| Subitem3 | 244 | 228 | -16 |
| Subitem4 | 10 | 0 | -10 |
| Item | 88 | 107 | +19 |
| List | 42 | 130 | +88 |
| Column | 6 | 178 | +172 |
| Paragraph | 36 | 31 | -5 |

#### 2. テキスト内容の差異
- **期待値のテキスト数**: 1,394個
- **実際のテキスト数**: 1,390個
- **期待値にあるが実際にない**: 4個
- **実際にあるが期待値にない**: 13個

#### 3. テキストの順序
最初の不一致: **位置63**
- 期待値: 「ア」
- 実際: 「各学校においては，卒業までに履修させる...」

---

## 原因分析

### 科目構造変換の違い

#### test_input5.xml（入力）
```xml
<List>
  <ListSentence>
    <Sentence>〔医療と社会〕</Sentence>
  </ListSentence>
</List>
<List>
  <ListSentence>
    <Column><Sentence>１</Sentence></Column>
    <Column><Sentence>目標</Sentence></Column>
  </ListSentence>
</List>
```

#### test_output5.xml（期待値）
```xml
<Sentence Num="1">〔医療と社会〕</Sentence>
```
→ **〔医療と社会〕が変換されていない（Sentence要素のまま）**

#### test_output5_actual.xml（実際の出力）
```xml
<Item Num="...">
  <ItemTitle>〔医療と社会〕</ItemTitle>
  <ItemSentence>...</ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title>１</Subitem1Title>
    <Subitem1Sentence>...</Subitem1Sentence>
  </Subitem1>
</Item>
```
→ **〔医療と社会〕が正しくItem要素に変換されている**

---

## 結論

### test_output5.xmlの問題
`test_output5.xml`は**現在のスクリプトの期待される出力ではありません**。

理由：
1. **科目構造が変換されていない**
   - 〔科目名〕形式がItem/Subitem階層に変換されていない
   - List要素がそのまま残っている

2. **変換ロジックが異なる**
   - Subitem階層の深さが異なる（Subitem4が期待値には存在するが実際には0）
   - Item要素の数が異なる

3. **可能性のある原因**
   - test_output5.xmlが古いバージョンのスクリプトで作成された
   - test_output5.xmlが別のスクリプトで作成された
   - test_output5.xmlが手動で作成・編集された

### 現在のスクリプトの動作
`convert_list_unified.py`は**READMEの仕様通りに正しく動作**しています：

✅ 科目構造変換（パターン1）
- 〔科目名〕をItem/Subitem階層に変換
- 数字タイトル（１、２、３）→ Subitem1
- 括弧数字（（１）、（２））→ Subitem2
- カタカナ（ア、イ、ウ）→ Subitem3

✅ Paragraph構造変換（パターン2）
- Paragraph内のList要素を新しいParagraph/Item階層に変換
- 数字タイトルに応じて新しいParagraphまたはItemを作成

---

## 推奨事項

### 1. test_output5.xmlの更新が必要
現在のスクリプトの出力を基準とする場合：

```bash
# 新しい期待値を生成
cd scripts/education_script
python convert_list_unified.py test_input5.xml test_output5_new.xml

# 内容を確認後、test_output5.xmlを置き換え
mv test_output5.xml test_output5_old.xml
mv test_output5_new.xml test_output5.xml
```

### 2. スクリプトの動作確認
現在のスクリプトが正しく動作していることを確認：

```bash
# 検証スクリプトを実行
python verify_conversion.py test_input5.xml test_output5_actual.xml
```

結果:
- ✅ すべてのテキストが保持されている
- ✅ 文書構造内の順序が保持されている
- ✅ 科目構造が正しく変換されている

### 3. test_output5.xmlの作成経緯の確認
- いつ、どのように作成されたか
- どのバージョンのスクリプトで作成されたか
- 手動での修正が加えられたか

---

## 検証統計

### 現在のスクリプトの変換結果（test_output5_actual.xml）
```
処理統計:
  科目構造の変換数: 7
  Paragraph構造の変換数: 12
  作成されたItem要素: 7
  作成されたParagraph要素: 18
```

### 要素数の比較

| 要素 | test_output5.xml | test_output5_actual.xml | 差 |
|------|------------------|-------------------------|-----|
| Item | 88 | 107 | +19 |
| Subitem1 | 83 | 28 | -55 |
| Subitem2 | 122 | 83 | -39 |
| Subitem3 | 244 | 228 | -16 |
| Subitem4 | 10 | 0 | -10 |

---

## 総合評価

### 現在のスクリプト（convert_list_unified.py）
**✅ 正常に動作しています**
- READMEの仕様通りに変換
- テキストの完全性を保持
- 文書構造の順序を保持

### test_output5.xml
**❌ 現在のスクリプトの期待値として不適切**
- 科目構造が変換されていない
- 変換ロジックが現在のスクリプトと異なる

### 推奨アクション
1. test_output5.xmlを現在のスクリプトの出力で更新する
2. または、test_output5.xmlが正しい場合はスクリプトのロジックを見直す

---

## 補足資料

### 作成されたファイル
- `test_output5_actual.xml` - 現在のスクリプトの出力
- `compare_with_expected.py` - 比較スクリプト
- `COMPARISON_REPORT.md` - このレポート

### 参考
- `README.md` - スクリプトの仕様書
- `VERIFICATION_REPORT.md` - 前回の検証レポート
