# Phase 1: 親ラベル依存性の分析

**報告日**: 2025年10月27日  
**重要度**: 🔴 **極めて高い**

---

## 🚨 ユーザーからの重要な指摘

> **「各階層で使用されるラベルの要素は、親階層で使用されている要素によって変化します」**

---

## 🔍 問題の確認

### ドキュメントに記載されている仕様

`修正ロジック分析.md` 3-2. 親要素がParagraphの場合：

| ラベルパターン | 判定条件 | 変換先 | 説明 |
|--------------|---------|--------|------|
| 数字 | **連続番号** | 新しい`Paragraph` | 前のParagraphNumと連続（１→２→３） |
| 数字 | **1から開始** | `Item` | 新しい系列の開始（１、２、３...） |
| 括弧数字 | - | `Item` | 項目の詳細展開 |

### 具体例

#### パターン1: 親Paragraphが「１」を使用
```xml
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>  ← 親が「１」を使用
  <ParagraphSentence>...</ParagraphSentence>
  <List>
    <Column><Sentence>２</Sentence></Column>  ← 「２」は連続番号
    <Column><Sentence>...</Sentence></Column>
  </List>
</Paragraph>

→ 「２」は新しいParagraphになる（連続番号だから）
```

#### パターン2: 親Paragraphが空
```xml
<Paragraph Num="1">
  <ParagraphNum></ParagraphNum>  ← 親が空
  <ParagraphSentence>...</ParagraphSentence>
  <List>
    <Column><Sentence>１</Sentence></Column>  ← 「１」は新しい系列
    <Column><Sentence>...</Sentence></Column>
  </List>
</Paragraph>

→ 「１」はItemになる（新しい系列の開始だから）
```

---

## ❌ 現在の実装の問題

### 実装状況

```python
def determine_element_type(self, label: str, parent_tag: str, current_depth: int = 0) -> str:
    """親要素とラベルから変換先の要素タイプを決定
    
    Args:
        label: ラベル文字列（「１」、「（１）」、「ア」等）
        parent_tag: 親要素のタグ名（'Paragraph', 'Item', 'Subitem1'等）
        current_depth: 現在のSubitemの深さ（0=Item, 1=Subitem1, ...）
    """
    level = self.get_hierarchy_level(label)
    
    # Paragraph/Article直下の場合
    if parent_tag in ['Paragraph', 'Article']:
        if level == 1:
            # 数字 → 新しいParagraph
            return 'Paragraph'  # ❌ 常にParagraphになる！
```

### 問題点

**親要素のラベルを考慮していない**

| 必要なパラメータ | 現在の実装 | 状態 |
|----------------|-----------|------|
| `label` | ✅ あり | 現在処理しているラベル |
| `parent_tag` | ✅ あり | 親要素のタグ名 |
| **`parent_label`** | **❌ なし** | **親要素が使用しているラベル** |

---

## 📊 影響範囲の分析

### 影響を受ける変換パターン

#### 1. Paragraph直下の数字ラベル
**現在の実装**: すべて新しいParagraphになる  
**正しい実装**: 
- 親ParagraphNumが「１」で、次が「２」 → 新しいParagraph ✅
- 親ParagraphNumが空で、次が「１」 → Item ✅

#### 2. Item直下のラベル
**現在の実装**: 階層レベルのみで判定  
**正しい実装**:
- 親Itemが「１」（数字）を使用している場合:
  - 「（１）」→ Subitem1
  - 「ア」→ Subitem1
- 親Itemが「（１）」（括弧数字）を使用している場合:
  - 「ア」→ Subitem1
  - 「（ア）」→ Subitem2

#### 3. 連続番号の判定
**現在の実装**: 判定していない  
**正しい実装**:
```python
def is_consecutive_number(parent_label: str, current_label: str) -> bool:
    """連続番号かどうかを判定
    
    例:
      is_consecutive_number("１", "２") → True
      is_consecutive_number("１", "３") → False（飛び番号）
      is_consecutive_number("", "１") → False（親が空）
    """
```

---

## 🔧 修正方針

### 必要な変更

#### 1. 関数シグネチャの変更
```python
# 修正前
def determine_element_type(self, label: str, parent_tag: str, current_depth: int = 0) -> str:

# 修正後
def determine_element_type(self, label: str, parent_tag: str, 
                          parent_label: Optional[str] = None,
                          current_depth: int = 0) -> str:
    """親要素とラベルから変換先の要素タイプを決定
    
    Args:
        label: ラベル文字列（「１」、「（１）」、「ア」等）
        parent_tag: 親要素のタグ名（'Paragraph', 'Item', 'Subitem1'等）
        parent_label: 親要素が使用しているラベル（★新規追加）
        current_depth: 現在のSubitemの深さ（0=Item, 1=Subitem1, ...）
    """
```

#### 2. 連続番号判定の追加
```python
def is_consecutive_number(self, parent_label: str, current_label: str) -> bool:
    """連続番号かどうかを判定"""
    if not parent_label or not current_label:
        return False
    
    # 全角数字を半角に変換
    parent_num = self._zenkaku_to_hankaku(parent_label)
    current_num = self._zenkaku_to_hankaku(current_label)
    
    try:
        parent_val = int(parent_num)
        current_val = int(current_num)
        return current_val == parent_val + 1
    except ValueError:
        return False
```

#### 3. Paragraph直下の数字判定の修正
```python
if parent_tag in ['Paragraph', 'Article']:
    if level == 1:
        # 数字の場合、連続番号かどうかを判定
        if parent_label and self.is_consecutive_number(parent_label, label):
            # 連続番号 → 新しいParagraph
            return 'Paragraph'
        else:
            # 1から開始 or 親が空 → Item
            return 'Item'
```

#### 4. 階層コンテキストへの親ラベル追加
```python
hierarchy_context = {
    'current_parent': None,
    'parent_tag': 'Paragraph',
    'parent_label': '',  # ★新規追加
    'counters': {...}
}
```

#### 5. 親ラベルの追跡
```python
# Itemを作成したとき
hierarchy_context['parent_label'] = label

# determine_element_type()を呼び出すとき
element_type = self.determine_element_type(
    label, 
    hierarchy_context['parent_tag'],
    hierarchy_context['parent_label']  # ★追加
)
```

---

## 📈 実装優先度

| 優先度 | 内容 | 理由 |
|--------|------|------|
| 🔴 **最高** | Paragraph直下の数字判定 | test_input5.xmlで頻出 |
| 🟡 中 | Item直下の判定 | 階層レベルで基本的には対応できている |
| 🟢 低 | Subitem直下の判定 | 現状でも比較的正しく動作 |

---

## ✅ 回答: 既知かどうか

### ドキュメント
✅ **ドキュメント（修正ロジック分析.md）には明確に記載されています**

### 実装
❌ **現在の実装では対応していません**

### 影響
🔴 **Phase 1の階層判定に重大な影響があります**

---

## 🎯 次のステップ

### 即座の対応
1. **`parent_label`パラメータの追加**: `determine_element_type()`に追加
2. **連続番号判定の実装**: `is_consecutive_number()`関数を追加
3. **階層コンテキストの拡張**: `parent_label`を追跡
4. **Paragraph直下の数字判定修正**: 連続番号判定を追加

### テスト
5. **単体テスト作成**: 連続番号判定のテスト
6. **統合テスト**: test_input5.xmlで検証

---

## 📋 実装例

### 完全な実装例
```python
def determine_element_type(self, label: str, parent_tag: str, 
                          parent_label: Optional[str] = None,
                          current_depth: int = 0) -> str:
    """親要素とラベルから変換先の要素タイプを決定
    
    Args:
        label: ラベル文字列（「１」、「（１）」、「ア」等）
        parent_tag: 親要素のタグ名（'Paragraph', 'Item', 'Subitem1'等）
        parent_label: 親要素が使用しているラベル
        current_depth: 現在のSubitemの深さ（0=Item, 1=Subitem1, ...）
    
    Returns:
        str: 変換先の要素タイプ（'Paragraph', 'Item', 'Subitem1'等）
    """
    level = self.get_hierarchy_level(label)
    
    if level == 0:
        return 'Item'
    
    # Paragraph/Article直下の場合
    if parent_tag in ['Paragraph', 'Article']:
        if level == 1:
            # 数字の場合、親ラベルとの関係で判定
            if parent_label and self.is_consecutive_number(parent_label, label):
                # 連続番号 → 新しいParagraph
                return 'Paragraph'
            else:
                # 新しい系列の開始 → Item
                return 'Item'
        elif level == 2:
            # 括弧数字 → Item
            return 'Item'
        # ... 以下略
    
    # Item直下の場合
    elif parent_tag == 'Item':
        # 親Itemのラベルに応じた判定も可能
        # （現状の階層レベル判定で基本的には正しい）
        if level == 3:
            return 'Subitem1'
        # ... 以下略
```

---

## 🚨 結論

**ユーザーのご指摘は完全に正しいです**

1. ✅ ドキュメントには記載されている
2. ❌ 現在の実装では対応していない
3. 🔴 Phase 1の階層判定に重大な影響がある
4. 🎯 `parent_label`パラメータの追加が必須

この修正なしでは、**Paragraph直下の数字ラベルの判定が正しく動作しません**。

---

**作成日**: 2025年10月27日  
**ファイル**: `/Users/fukushima/Documents/xml_anken/gyosei-xml/scripts/education_script/reports/Phase1_親ラベル依存性_分析.md`

