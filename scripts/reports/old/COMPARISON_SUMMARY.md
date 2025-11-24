# 変換ロジックの比較: test_output5.xml vs 現在のスクリプト

## 比較サマリー

| 機能 | test_output5.xml | 現在のスクリプト | 状態 |
|------|------------------|------------------|------|
| 科目名の配置 | ItemSentence/Sentence | ItemSentence/Sentence | ✅ 一致（修正済み） |
| 科目構造の階層深度 | 4段階（Item→Sub1→Sub2→Sub3） | 4段階 | ✅ 一致 |
| Paragraph構造の階層深度 | 5段階（Item→Sub1→Sub2→Sub3→Sub4） | **2段階（Item→Listのみ）** | ❌ **不一致** |
| 空タイトルのSubitem | 多数のパターンで使用 | 限定的 | ⚠️ 部分的不一致 |

---

## 詳細な比較

### 1. Paragraph構造変換

#### test_output5.xmlのロジック

```
Paragraph内のList要素の階層:

├─ 数字（２、３、４） → 新しいParagraph
│   └─ ParagraphNum: ２
│   └─ ParagraphSentence: 内容
│   └─ 括弧数字（（１）、（２）） → Item
│        └─ ItemTitle: （１）
│        └─ ItemSentence: 内容
│        └─ カタカナ（ア、イ、ウ） → Subitem1
│             └─ Subitem1Title: ア
│             └─ Subitem1Sentence: 内容
│             └─ 括弧カタカナ（（ア）、（イ）） → Subitem2
│                  └─ Subitem2Title: （ア）
│                  └─ Subitem2Sentence: 内容
│                  └─ 二重括弧（（（ア））） → Subitem3
│                       └─ Subitem3Title: （（ア））
│                       └─ Subitem3Sentence: 内容
│                       └─ 小文字アルファベット（ａ、ｂ） → Subitem4
│                            └─ Subitem4Title: ａ
│                            └─ Subitem4Sentence: 内容
└─ 長文 → List（直前の要素内）
```

#### 現在のスクリプトのロジック

```
Paragraph内のList要素の階層:

├─ 数字（２、３、４） → 新しいParagraph
│   └─ ParagraphNum: ２
│   └─ ParagraphSentence: 内容
│   └─ 括弧数字（（１）、（２）） → Item
│        └─ ItemTitle: （１）
│        └─ ItemSentence: 内容
│        └─ 長文 → List（そのまま）
│        
│   ❌ カタカナ、括弧カタカナ、二重括弧、小文字アルファベットは変換されない
│   
└─ 長文 → List（直前のItem内、またはそのまま）
```

**問題点**: 現在のスクリプトは、Paragraph構造内で**Subitem階層を作成しない**

---

### 2. 科目構造変換

#### test_output5.xmlのロジック

```
科目構造（〔XXX〕）の階層:

Item
└─ ItemTitle: (空)
└─ ItemSentence/Sentence: 〔科目名〕
└─ 数字（１、２、３） → Subitem1
     └─ Subitem1Title: １
     └─ Subitem1Sentence: 目標
     └─ 括弧数字（（１）、（２）） → Subitem2
          └─ Subitem2Title: （１）
          └─ Subitem2Sentence: 内容
          └─ カタカナ（ア、イ、ウ） → Subitem3
               └─ Subitem3Title: ア
               └─ Subitem3Sentence: 内容

特殊ケース:
- 括弧数字が連続する場合 → 空タイトルのSubitem1を作成
  └─ Subitem1: (空)
       ├─ Subitem2: （１）
       └─ Subitem2: （２）
       
- 〔指導項目〕 → 空タイトルのSubitem1
  └─ Subitem1Title: (空)
  └─ Subitem1Sentence/Sentence: 〔指導項目〕
```

#### 現在のスクリプトのロジック

```
科目構造（〔XXX〕）の階層:

Item
└─ ItemTitle: (空) ✅
└─ ItemSentence/Sentence: 〔科目名〕 ✅
└─ 数字（１、２、３） → Subitem1 ✅
     └─ Subitem1Title: １
     └─ Subitem1Sentence: 目標
     └─ 括弧数字（（１）、（２）） → Subitem2 ✅
          └─ Subitem2Title: （１）
          └─ Subitem2Sentence: 内容
          └─ カタカナ（ア、イ、ウ） → Subitem3 ✅
               └─ Subitem3Title: ア
               └─ Subitem3Sentence: 内容

特殊ケース:
- 〔指導項目〕 → 空タイトルのSubitem1 ✅
  └─ Subitem1Title: (空)
  └─ Subitem1Sentence/Sentence: 〔指導項目〕
  
⚠️ 括弧数字が連続する場合の空Subitem1作成ロジックが不明確
```

**状態**: 基本的な階層構造は一致しているが、空タイトルの作成ロジックに違いがある可能性

---

### 3. ParagraphNumが空の場合

#### test_output5.xmlのロジック

```
<Paragraph>
  <ParagraphNum></ParagraphNum>
  
  最初の長文 → ParagraphSentence
  数字（１、２） → Item
  括弧数字（（１）） → Item
```

#### 現在のスクリプトのロジック

```
<Paragraph>
  <ParagraphNum></ParagraphNum>
  
  最初の長文 → ParagraphSentence ✅
  空Itemを追加 → Item（空） ⚠️
  次の長文 → List（Paragraph内）⚠️
  数字（１、２） → Item ✅
  括弧数字（（１）） → Item ✅
```

**問題点**: 空Itemと余分なListの処理が異なる

---

## 最も重要な差異

### ❌ **クリティカル**: Paragraph構造でのSubitem階層の欠如

**test_output5.xml**:
```xml
<Paragraph Num="3">
  <Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <Subitem1 Num="1">
      <Subitem1Title>ア</Subitem1Title>
      <Subitem2 Num="1">
        <Subitem2Title>（ア）</Subitem2Title>
        <Subitem3 Num="1">
          <Subitem3Title>（（ア））</Subitem3Title>
          <Subitem4 Num="1">
            <Subitem4Title>ａ</Subitem4Title>
          </Subitem4>
        </Subitem3>
      </Subitem2>
    </Subitem1>
  </Item>
</Paragraph>
```

**現在のスクリプト**:
```xml
<Paragraph Num="3">
  <Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>...</ItemSentence>
    <List>ア → 内容...</List>  <!-- 変換されない -->
    <List>（ア）→ 内容...</List>  <!-- 変換されない -->
  </Item>
</Paragraph>
```

---

## 修正が必要な項目

### 優先度: 高

1. **Paragraph構造内でのSubitem階層の作成**
   - カタカナ（ア）→ Subitem1
   - 括弧カタカナ（（ア））→ Subitem2
   - 二重括弧（（（ア））））→ Subitem3
   - 小文字アルファベット（ａ）→ Subitem4

2. **判定ロジックの追加**
   - 括弧カタカナの判定：`（ア）`、`（イ）`
   - 二重括弧の判定：`（（ア））`、`（（イ））`
   - 小文字アルファベットの判定：`ａ`、`ｂ`、`ｃ`

### 優先度: 中

3. **空タイトルのSubitem作成ロジックの改善**
   - 括弧数字が連続する場合の処理
   - 二重括弧の前の空Subitem2の処理

4. **ParagraphNumが空の場合の処理改善**
   - 空Itemの処理
   - 余分なListの処理

### 優先度: 低

5. **エッジケースの処理**
   - 複雑な入れ子構造
   - 不規則なパターン

---

## 実装の方向性

### アプローチ1: 段階的な拡張（推奨）

現在のスクリプトに、段階的に機能を追加：

1. **フェーズ1**: Paragraph構造でのカタカナ判定とSubitem1作成
2. **フェーズ2**: 括弧カタカナ判定とSubitem2作成
3. **フェーズ3**: 二重括弧判定とSubitem3作成
4. **フェーズ4**: 小文字アルファベット判定とSubitem4作成
5. **フェーズ5**: 空タイトルのロジック改善

### アプローチ2: 完全な書き直し

test_output5.xmlのロジックに完全に合わせて再実装：

- メリット: 確実に一致する
- デメリット: 時間がかかる、テストが必要

---

## テスト戦略

1. **Unit Test**: 各判定ロジックの個別テスト
2. **Integration Test**: 変換パターンごとのテスト
3. **Regression Test**: test_output5.xmlとの完全一致テスト

---

## 次のステップ

1. ✅ 分析完了
2. ⬜ 優先度の確認（どこまで一致させるか）
3. ⬜ 実装方針の決定（段階的 vs 完全書き直し）
4. ⬜ 実装
5. ⬜ テスト
6. ⬜ ドキュメント更新

---

## 参考資料

- **詳細分析**: `CONVERSION_LOGIC_ANALYSIS.md`
- **現在のスクリプト**: `convert_list_unified.py`
- **期待値**: `test_output5.xml`
- **入力**: `test_input5.xml`
