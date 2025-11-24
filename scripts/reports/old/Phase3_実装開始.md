# Phase 3実装開始

**開始日**: 2025年10月27日  
**目標**: 角括弧科目名パターン（〔科目名〕）の完全実装

---

## 🎯 Phase 3の目的

### 対象パターン
**角括弧科目名パターン** - 14個

```
〔医療と社会〕
〔指導項目〕
〔人体の構造と機能〕
...
```

これらは、数字や括弧がないが、階層要素として扱われる特殊なパターンです。

---

## 📋 実装内容

### 1. パターン検出
```python
def is_bracketed_subject(text: str) -> bool:
    """角括弧科目名パターンを判定"""
    return bool(re.match(r'^〔.+〕$', text.strip()))
```

### 2. 階層決定ロジック
- 後続の`List+Column`要素のラベルから階層を逆算
- 例: 後続が「１」（レベル1）→ 科目名はItem
- 例: 後続が「（１）」（レベル2）→ 科目名はSubitem1

### 3. 要素作成
```xml
<Item Num="1">
  <ItemTitle></ItemTitle>  <!-- 空のTitle -->
  <ItemSentence>
    <Sentence>〔医療と社会〕</Sentence>
  </ItemSentence>
  <!-- 後続のList+Column要素が子要素として続く -->
</Item>
```

---

## 🔧 実装場所

### convert_paragraph_structure()内
- 1166行目付近（パターンC: Column構造なしList）
- 既存の`is_subject_title()`の処理を拡張

### 必要な変更
1. **〔...〕パターンの検出**: 正規表現で判定
2. **先読み機能**: 次のList要素のラベルを確認
3. **階層逆算**: 後続ラベルから要素タイプを決定
4. **空要素作成**: 空Title + 〔科目名〕Sentence

---

## 📊 実装の優先順位

### Phase 3.1: パターン検出（推定: 15分）
- `is_bracketed_subject()`メソッドの追加
- 既存のパターン判定に統合

### Phase 3.2: 階層逆算ロジック（推定: 30分）
- 先読み機能の活用
- 後続ラベルから階層を決定

### Phase 3.3: 要素作成と統合（推定: 30分）
- 空Title要素の作成
- 子要素の正しい配置

### Phase 3.4: テストと検証（推定: 15-30分）
- 14個のパターンで動作確認
- デバッグと修正

---

## ✅ 実装開始

次のステップ：
1. `is_bracketed_subject()`メソッドを追加
2. パターンC（Column構造なしList）に角括弧判定を追加
3. 先読みで後続ラベルを取得
4. 階層逆算ロジックを実装
5. 空要素作成と配置

---

**作成日**: 2025年10月27日  
**ファイル**: `/Users/fukushima/Documents/xml_anken/gyosei-xml/scripts/education_script/reports/Phase3_実装開始.md`

