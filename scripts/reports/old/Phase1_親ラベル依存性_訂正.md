# Phase 1: 親ラベル依存性の訂正

**訂正日**: 2025年10月27日  
**重要度**: 🔴 **訂正が必要**

---

## 🙏 誤りの訂正

前回のレポート「Phase1_親ラベル依存性_分析.md」で示した例に**重大な誤り**がありました。

---

## ❌ 誤った例（前回）

```
ケース2: 親が空の場合

<Paragraph>
  <ParagraphNum></ParagraphNum>  ← 親が空
  <List><Column>１</Column></List>  ← 新しい系列
</Paragraph>

期待: 「１」→ Item ✅
現在: 「１」→ 新しいParagraph ❌ **間違い！**
```

---

## ✅ 正しい理解（訂正後）

### 実際の例（test_input5.xml 48-62行目）

**入力**:
```xml
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>  ← 親が「１」
  <ParagraphSentence>...</ParagraphSentence>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>２</Sentence></Column>  ← 連続番号
      <Column Num="2"><Sentence>学校の教育活動を...</Sentence></Column>
    </ListSentence>
  </List>
</Paragraph>
```

**出力（test_output5.xml 38-48行目）**:
```xml
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>...</ParagraphSentence>
</Paragraph>
<Paragraph Num="2">
  <ParagraphNum>２</ParagraphNum>
  <ParagraphSentence>
    <Sentence>学校の教育活動を...</Sentence>
  </ParagraphSentence>
</Paragraph>
```

### 結論
✅ **「１」→「２」は連続番号なので、新しいParagraphが正しい**

ユーザーのご指摘通り、**新しいParagraph要素で問題ありません**。

---

## 🔍 本当に問題になるケースの確認

親ラベル依存性が問題になるのは以下のケースです：

### ケースA: 連続番号（新しいParagraph）
```xml
<Paragraph>
  <ParagraphNum>１</ParagraphNum>  ← 親が「１」
  <List><Column>２</Column></List>  ← 連続番号
</Paragraph>

→ 「２」は新しいParagraph ✅
```

### ケースB: 非連続番号または親が空（Item）
```xml
<Paragraph>
  <ParagraphNum></ParagraphNum>  ← 親が空
  <List><Column>１</Column></List>  ← 新しい系列の開始
</Paragraph>

→ 「１」はItem ✅
```

または

```xml
<Paragraph>
  <ParagraphNum>１</ParagraphNum>  ← 親が「１」
  <List><Column>１</Column></List>  ← 同じ番号（非連続）
</Paragraph>

→ 「１」はItem ✅
```

---

## 📊 test_input5.xmlでの実態調査

### 調査項目
1. **親ParagraphNumが空で、List内に数字ラベルがあるケース**
2. **親ParagraphNumと同じ数字がList内にあるケース**
3. **連続番号のケース**

これらの分布を確認する必要があります。

---

## 🔧 修正の必要性の再評価

### 現在の実装の動作

```python
if parent_tag in ['Paragraph', 'Article']:
    if level == 1:
        # 数字 → 新しいParagraph
        return 'Paragraph'
```

**現在の実装**: すべての数字ラベルが新しいParagraphになる

### 問題が発生するケース

| 入力パターン | 現在の実装 | 正しい動作 | 一致？ |
|------------|-----------|-----------|--------|
| 親「１」+ List「２」 | Paragraph | Paragraph | ✅ 正しい |
| 親「空」+ List「１」 | Paragraph | Item | ❌ **間違い** |
| 親「１」+ List「１」 | Paragraph | Item | ❌ **間違い** |
| 親「１」+ List「３」 | Paragraph | Item? | ❌ **要確認** |

---

## 🎯 次のステップ

### 1. 実態調査
test_input5.xmlで以下を確認：
- 親ParagraphNumが空のケースは存在するか？
- その場合にList内に数字ラベルがあるか？

### 2. 調査結果に基づく対応
- **存在しない場合**: 現在の実装で問題なし（修正不要）
- **存在する場合**: `parent_label`パラメータの追加が必要

---

## 📝 暫定結論

1. ✅ ユーザーの指摘は正しい：「１」→「２」は新しいParagraphで正しい
2. ❌ 私の例が間違っていた：親が空ではなく、親が「１」だった
3. ⏳ **実態調査が必要**: 本当に問題になるケースがtest_input5.xmlに存在するか？

---

## 🔍 実態調査の実行

test_input5.xmlで以下のパターンを検索します：
1. `<ParagraphNum></ParagraphNum>`または`<ParagraphNum/>`
2. その後にList要素で数字ラベルが続くパターン

---

**作成日**: 2025年10月27日  
**ファイル**: `/Users/fukushima/Documents/xml_anken/gyosei-xml/scripts/education_script/reports/Phase1_親ラベル依存性_訂正.md`

