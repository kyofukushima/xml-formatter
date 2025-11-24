# Phase 2実装開始

**開始日**: 2025年10月27日  
**目標**: 複雑パターン処理（先読み+空要素挿入）の実装

---

## 🎯 Phase 2の目的

### 対象パターン
**ラベル+テキスト後にColumn構造なしListが続く場合** - 44個

#### パターンA: 深い階層なし（26個）
```xml
（ア）タイトル    ← Column構造あり
補足テキスト      ← Column構造なし
（イ）次のタイトル ← Column構造あり（同レベル）

→ 補足テキストを（ア）の中に配置
```

#### パターンB: 深い階層あり（18個）
```xml
（イ）タイトル    ← Column構造あり（レベル4）
補足テキスト      ← Column構造なし
（（ア））深い階層 ← Column構造あり（レベル5、2レベル深い）

→ 補足テキストを配置し、空の中間要素を挿入
```

---

## 📋 実装内容

### 1. 先読み機能の活用
すでに実装済みの関数を活用：
```python
def lookahead_next_list(self, list_elements: List[ET.Element], 
                       current_index: int) -> Optional[ET.Element]
```

### 2. 空要素判定の実装
すでに実装済みの関数を活用：
```python
def needs_intermediate_element(self, current_label: str, next_label: str) -> bool:
    """
    空の中間要素が必要かを判定
    2レベル以上深くなる場合はTrue
    """
    current_level = self.get_hierarchy_level(current_label)
    next_level = self.get_hierarchy_level(next_label)
    return next_level > current_level + 1
```

### 3. 処理フロー

```python
# Column構造ありのListを処理した後
if columns and len(columns) >= 2:
    # 要素を作成
    new_elem = create_element(label, content)
    
    # ★ Phase 2: 次のListを先読み
    next_list = lookahead_next_list(list_elements, current_index)
    
    if next_list is not None:
        next_columns = extract_columns(next_list)
        
        if not next_columns:
            # Column構造なし = 補足テキスト
            # 現在の要素内にListとして追加
            list_elem = create_list_element(next_list)
            new_elem.append(list_elem)
            
            # さらに次のListを先読み
            next_next_list = lookahead_next_list(list_elements, current_index + 1)
            if next_next_list is not None:
                next_next_columns = extract_columns(next_next_list)
                if next_next_columns:
                    next_next_label = next_next_columns[0][0]
                    
                    # 空要素が必要か判定
                    if needs_intermediate_element(label, next_next_label):
                        # 空の中間要素を作成
                        empty_elem = create_empty_intermediate_element()
                        # 適切な場所に挿入
```

---

## 🔧 実装場所

### convert_paragraph_structure()内
- 926-1059行目付近（Column構造ありの処理）
- 既存の処理に統合

### 必要な変更
1. **リストのインデックス管理**: 現在処理中のListのインデックスを追跡
2. **スキップ機能**: 補足テキストとして処理したListをスキップ
3. **空要素作成**: 適切な階層に空の中間要素を挿入

---

## 📊 実装の優先順位

### Phase 2.1: パターンAの実装（推定: 30分）
- Column構造なしのListを前の要素内に追加
- スキップ機能の実装

### Phase 2.2: パターンBの実装（推定: 45分）
- 空要素判定の統合
- 空の中間要素の作成と挿入

### Phase 2.3: テストと検証（推定: 15-30分）
- 軽量テストでの動作確認
- デバッグと修正

---

## ✅ 実装開始

次のステップ：
1. convert_paragraph_structure()をリスト処理からインデックス処理に変更
2. Column構造ありの処理後に先読みを追加
3. パターンAの実装
4. パターンBの実装

---

**作成日**: 2025年10月27日  
**ファイル**: `/Users/fukushima/Documents/xml_anken/gyosei-xml/scripts/education_script/reports/Phase2_実装開始.md`

