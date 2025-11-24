# test_output5.xml の変換ロジック分析結果

## 分析日
2025年1月

## 対象ファイル
- **入力**: `test_input5.xml`
- **出力**: `test_output5.xml`

---

## 変換ロジックの全体像

### パターン1: Paragraph構造変換

ParagraphNumがある場合の変換ルール：

```
入力（List要素）                → 出力
─────────────────────────────────────────────────
数字（２、３、４、５）           → 新しいParagraph
  └─ 括弧数字（（１）、（２））   → Item（そのParagraph内）
       └─ カタカナ（ア、イ、ウ）  → Subitem1（そのItem内）
            └─ 括弧カタカナ（（ア）） → Subitem2
                 └─ 二重括弧（（（ア））） → Subitem3
                      └─ 小文字アルファベット（ａ、ｂ、ｃ） → Subitem4
長文（15文字以上）               → List（直前の要素内に保持）
```

#### 具体例：Article 1（第２節）

**入力構造**:
```xml
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>...</ParagraphSentence>
  <List>２ → 内容...</List>
  <List>（１）→ 内容...</List>
  <List>（２）→ 内容...</List>
  <List>長文...</List>
  <List>３ → 内容...</List>
  <List>（１）→ 内容...</List>
</Paragraph>
```

**出力構造**:
```xml
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>...</ParagraphSentence>
</Paragraph>
<Paragraph Num="2">
  <ParagraphNum>２</ParagraphNum>
  <ParagraphSentence>...</ParagraphSentence>
  <Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    ...
  </Item>
  <Item Num="2">
    <ItemTitle>（２）</ItemTitle>
    ...
  </Item>
  <List>長文...</List>
</Paragraph>
<Paragraph Num="3">
  <ParagraphNum>３</ParagraphNum>
  <ParagraphSentence>...</ParagraphSentence>
  <Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    ...
  </Item>
</Paragraph>
```

#### 具体例：Article 2（教育課程の編成）

**入力構造**:
```xml
<List>３ → 教育課程の編成における共通的事項</List>
<List>（１）→ 視覚障害者...の履修等</List>
<List>ア → 各教科・科目及び単位数等</List>
<List>（ア）→ 卒業までに履修させる単位数等</List>
<List>各学校においては，卒業までに...</List>  <!-- 長文 -->
<List>（イ）→ 各学科に共通する...</List>
<List>（（ア））→ 視覚障害者である生徒...</List>
<List>ａ → 国語のうち「現代の国語」...</List>
```

**出力構造**:
```xml
<Paragraph Num="3">
  <ParagraphNum>３</ParagraphNum>
  <ParagraphSentence>教育課程の編成における共通的事項</ParagraphSentence>
  <Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>視覚障害者...の履修等</ItemSentence>
    <Subitem1 Num="1">
      <Subitem1Title>ア</Subitem1Title>
      <Subitem1Sentence>各教科・科目及び単位数等</Subitem1Sentence>
      <Subitem2 Num="1">
        <Subitem2Title>（ア）</Subitem2Title>
        <Subitem2Sentence>卒業までに履修させる単位数等</Subitem2Sentence>
        <List>各学校においては，卒業までに...</List>
      </Subitem2>
      <Subitem2 Num="2">
        <Subitem2Title>（イ）</Subitem2Title>
        <Subitem2Sentence>各学科に共通する...</Subitem2Sentence>
        <Subitem3 Num="1">
          <Subitem3Title>（（ア））</Subitem3Title>
          <Subitem3Sentence>視覚障害者である生徒...</Subitem3Sentence>
          <Subitem4 Num="1">
            <Subitem4Title>ａ</Subitem4Title>
            <Subitem4Sentence>国語のうち「現代の国語」...</Subitem4Sentence>
          </Subitem4>
        </Subitem3>
      </Subitem2>
    </Subitem1>
  </Item>
</Paragraph>
```

---

### パターン2: 科目構造変換

〔科目名〕で始まるList要素群の変換ルール：

```
入力（List要素）                → 出力
─────────────────────────────────────────────────
〔科目名〕                      → Item
                                   └─ ItemTitle: (空)
                                   └─ ItemSentence/Sentence: 〔科目名〕
  └─ 数字（１、２、３）          → Subitem1
       └─ 括弧数字（（１）、（２）） → Subitem2
            └─ カタカナ（ア、イ、ウ） → Subitem3
長文                           → List（直前の要素内に保持）
〔指導項目〕                    → Subitem1（タイトルが空、Sentenceに〔指導項目〕）
```

#### 具体例：〔医療と社会〕

**入力構造**:
```xml
<List>〔医療と社会〕</List>
<List>１ → 目標</List>
<List>長文（目標の説明）...</List>
<List>（１）→ 施術を行うために...</List>
<List>（２）→ 医療と社会の関わり...</List>
<List>２ → 内容</List>
<List>長文（導入文）...</List>
<List>〔指導項目〕</List>
<List>（１）→ 医療と倫理</List>
<List>ア → 医療倫理の歴史</List>
<List>イ → 医療倫理の基本原則</List>
```

**出力構造**:
```xml
<Item Num="N">
  <ItemTitle></ItemTitle>
  <ItemSentence>
    <Sentence Num="1">〔医療と社会〕</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title>１</Subitem1Title>
    <Subitem1Sentence>目標</Subitem1Sentence>
    <List>長文（目標の説明）...</List>
  </Subitem1>
  <Subitem1 Num="2">
    <Subitem1Title></Subitem1Title>
    <Subitem1Sentence></Subitem1Sentence>
    <Subitem2 Num="1">
      <Subitem2Title>（１）</Subitem2Title>
      <Subitem2Sentence>施術を行うために...</Subitem2Sentence>
    </Subitem2>
    <Subitem2 Num="2">
      <Subitem2Title>（２）</Subitem2Title>
      <Subitem2Sentence>医療と社会の関わり...</Subitem2Sentence>
    </Subitem2>
  </Subitem1>
  <Subitem1 Num="3">
    <Subitem1Title>２</Subitem1Title>
    <Subitem1Sentence>内容</Subitem1Sentence>
    <List>長文（導入文）...</List>
  </Subitem1>
  <Subitem1 Num="4">
    <Subitem1Title></Subitem1Title>
    <Subitem1Sentence>
      <Sentence Num="1">〔指導項目〕</Sentence>
    </Subitem1Sentence>
    <Subitem2 Num="1">
      <Subitem2Title>（１）</Subitem2Title>
      <Subitem2Sentence>医療と倫理</Subitem2Sentence>
      <Subitem3 Num="1">
        <Subitem3Title>ア</Subitem3Title>
        <Subitem3Sentence>医療倫理の歴史</Subitem3Sentence>
      </Subitem3>
      <Subitem3 Num="2">
        <Subitem3Title>イ</Subitem3Title>
        <Subitem3Sentence>医療倫理の基本原則</Subitem3Sentence>
      </Subitem3>
    </Subitem2>
  </Subitem1>
</Item>
```

---

### パターン3: ParagraphNumが空の場合

ParagraphNumが空の場合の変換ルール：

```
入力（List要素）                → 出力
─────────────────────────────────────────────────
最初の長文                      → ParagraphSentence
数字（１、２、３）               → Item（同じParagraph内）
括弧数字（（１）、（２））        → Item（同じParagraph内）
長文                           → List（直前のItem内に保持）
```

#### 具体例：Article 0（第１節）

**入力構造**:
```xml
<Paragraph Num="1">
  <ParagraphNum></ParagraphNum>
  <List>高等部における教育については...</List>  <!-- 長文 -->
  <List>１ → 学校教育法第５１条に...</List>
  <List>２ → 生徒の障害による...</List>
</Paragraph>
```

**出力構造**:
```xml
<Paragraph Num="1">
  <ParagraphNum></ParagraphNum>
  <ParagraphSentence>高等部における教育については...</ParagraphSentence>
  <Item Num="1">
    <ItemTitle>１</ItemTitle>
    <ItemSentence>学校教育法第５１条に...</ItemSentence>
  </Item>
  <Item Num="2">
    <ItemTitle>２</ItemTitle>
    <ItemSentence>生徒の障害による...</ItemSentence>
  </Item>
</Paragraph>
```

---

## 判定ロジック

### 要素の判定

| 要素タイプ | 判定条件 | 例 |
|-----------|---------|-----|
| 科目タイトル | `〔XXX〕`形式（`〔指導項目〕`を除く） | 〔医療と社会〕 |
| 指導項目 | `〔指導項目〕` | 〔指導項目〕 |
| 数字タイトル | `１`、`２`、`３`、`1`、`2`、`3` 等 | １、２、３ |
| 括弧数字 | `（１）`、`（２）`、`(1)`、`(2)` 等 | （１）、（２） |
| カタカナ | `ア`、`イ`、`ウ`、`エ`、`オ` 等 | ア、イ、ウ |
| 括弧カタカナ | `（ア）`、`（イ）`、`（ウ）` 等 | （ア）、（イ） |
| 二重括弧 | `（（ア））`、`（（イ））` 等 | （（ア））、（（イ）） |
| 小文字アルファベット | `ａ`、`ｂ`、`ｃ`、`ｄ` 等 | ａ、ｂ、ｃ |
| 長文 | 15文字以上で、上記の記号で始まらない | 各学校においては... |

### 階層の決定

#### Paragraph構造内（ParagraphNumあり）

```
数字タイトル
  └─ 新しいParagraph
       └─ 括弧数字
            └─ Item
                 └─ カタカナ
                      └─ Subitem1
                           └─ 括弧カタカナ
                                └─ Subitem2
                                     └─ 二重括弧
                                          └─ Subitem3
                                               └─ 小文字アルファベット
                                                    └─ Subitem4
```

#### 科目構造内

```
〔科目名〕
  └─ Item（ItemSentence/Sentenceに科目名）
       └─ 数字タイトル
            └─ Subitem1
                 └─ 括弧数字
                      └─ Subitem2
                           └─ カタカナ
                                └─ Subitem3
```

**注意**: 科目構造では、括弧数字の前に数字タイトルがない場合、空タイトルのSubitem1が作成されます。

---

## 重要な変換パターン

### 空タイトルのSubitem

**パターンA**: 科目構造で括弧数字が連続する場合

入力:
```
〔科目名〕
（１）→ 内容A
（２）→ 内容B
```

出力:
```
Item
  └─ Subitem1（タイトル空）
       ├─ Subitem2（１）
       └─ Subitem2（２）
```

**パターンB**: 括弧カタカナの後に二重括弧が来る場合

入力:
```
（イ）→ 内容
（（ア））→ 内容A
（（イ））→ 内容B
```

出力:
```
Subitem2（イ）
Subitem2（タイトル空）
  ├─ Subitem3（（ア））
  └─ Subitem3（（イ））
```

### 〔指導項目〕の特別処理

〔指導項目〕は科目タイトルと同じ形式ですが、特別に処理されます：

- **配置**: 科目Item内のSubitem1として配置
- **タイトル**: Subitem1Titleは空
- **内容**: Subitem1Sentence/Sentenceに「〔指導項目〕」

---

## 長文（List）の保持

長文は、直前の要素内にList要素として保持されます：

- 直前がItem → Itemの子要素としてList
- 直前がSubitem1 → Subitem1の子要素としてList
- 直前がSubitem2 → Subitem2の子要素としてList

---

## 現在のスクリプトとの違い

### 主な差異

| 項目 | test_output5.xml | 現在のスクリプト |
|------|------------------|------------------|
| 科目名の配置 | ItemSentence/Sentence | ~~ItemTitle~~ → 修正済み |
| 科目構造の階層 | 数字→Subitem1、括弧数字→Subitem2、カタカナ→Subitem3 | 数字→Subitem1、括弧数字→Subitem2、カタカナ→Subitem3 ✅ |
| Paragraph構造の階層 | カタカナ→Subitem1、括弧カタカナ→Subitem2、二重括弧→Subitem3、小文字→Subitem4 | **カタカナをSubitem1として扱わない** ❌ |
| 空タイトルのSubitem | 複数のパターンで使用 | **限定的な使用** ⚠️ |

### 詳細な差異

#### 1. Paragraph構造でのカタカナの扱い

**test_output5.xml**:
```
Item（括弧数字）
  └─ Subitem1（カタカナ）← ここ
       └─ Subitem2（括弧カタカナ）
```

**現在のスクリプト**:
```
Item（括弧数字）
  └─ List（カタカナ + 内容）← 変換されない
```

#### 2. 空タイトルのSubitemの作成

**test_output5.xml**: 
- 括弧数字が連続する場合、空タイトルのSubitem1を作成
- 二重括弧の前に、空タイトルのSubitem2を作成する場合がある

**現在のスクリプト**: 
- 空タイトルの作成ロジックが不完全

---

## まとめ

test_output5.xmlの変換ロジックは、**5段階の階層構造**に対応しています：

1. **Paragraph**: 数字タイトル（２、３、４）で分割
2. **Item**: 括弧数字（（１）、（２））
3. **Subitem1**: カタカナ（ア、イ、ウ）
4. **Subitem2**: 括弧カタカナ（（ア）、（イ））
5. **Subitem3**: 二重括弧（（（ア））、（（イ））））
6. **Subitem4**: 小文字アルファベット（ａ、ｂ、ｃ）

科目構造では、階層が1つ浅くなります：

1. **Item**: 科目名（〔XXX〕）
2. **Subitem1**: 数字タイトル（１、２、３）
3. **Subitem2**: 括弧数字（（１）、（２））
4. **Subitem3**: カタカナ（ア、イ、ウ）

この複雑な階層構造を正確に再現するには、現在のスクリプトに以下の修正が必要です：

1. ✅ **科目名の配置**: ItemSentence/Sentenceに配置（修正済み）
2. ❌ **Paragraph構造でのカタカナの扱い**: Subitem1として変換する
3. ⚠️ **空タイトルのSubitemの作成**: 適切なパターンで空タイトルを作成
4. ❌ **括弧カタカナと二重括弧の扱い**: Subitem2とSubitem3として変換
5. ❌ **小文字アルファベットの扱い**: Subitem4として変換
