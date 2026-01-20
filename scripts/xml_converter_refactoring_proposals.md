# xml_converter.py 追加リファクタリング提案

## 分析日時
2024年12月

## 概要
既存の分析レポート（xml_converter_analysis.md）で指摘された問題に加えて、さらに詳細なコード分析を行い、追加のリファクタリング候補を特定しました。

---

## 1. 高優先度リファクタリング

### 1.1 `process_elements_recursive`関数の分割（最重要）✅ 完了

**問題の深刻度: 高**

~~現在、`process_elements_recursive`関数は約465行（654-1118行目）の巨大な関数です。以下のように分割することを強く推奨します。~~

**✅ 対応完了** (2024年12月)

以下の対応を実施しました：
- `ProcessingMode` Enumクラスの作成
- `ProcessingState`クラスの導入（状態管理）
- `process_first_child_mode()`関数の作成
- `process_normal_mode_list_element()`関数の作成
- `get_title_text()`, `has_following_alphabet_label_list()`, `should_append_alphabet_label_as_child()`, `rebuild_parent_element()`などのヘルパー関数の追加
- メイン関数を約43行に簡潔化

**実施前**: 約465行の巨大な関数  
**実施後**: メイン関数約43行 + 複数の専用関数に分割

**残課題**: `process_normal_mode_list_element()`関数が約330行とまだ長いため、さらなる分割が推奨されます（下記1.5参照）。

#### 提案1: 処理モードごとの関数分割

```python
def process_elements_recursive(parent_elem, config: ConversionConfig, stats) -> bool:
    """親要素内のList要素を再帰的に子要素に変換（メイン関数）"""
    parent_sentence = parent_elem.find(f'{config.parent_tag}Sentence')
    if parent_sentence is None:
        return False

    siblings = list(parent_sentence.itersiblings())
    if not siblings:
        return False

    processor = ElementProcessor(config, stats, parent_elem)
    made_changes = processor.process_children(siblings)
    
    # 親要素の再構築
    processor.rebuild_parent(parent_elem, parent_sentence)
    
    return made_changes


class ElementProcessor:
    """要素処理を管理するクラス"""
    def __init__(self, config: ConversionConfig, stats, parent_elem):
        self.config = config
        self.stats = stats
        self.parent_elem = parent_elem
        self.current_mode = ProcessingMode.LOOKING_FOR_FIRST_CHILD
        self.last_child = None
        self.seen_label_texts = set()
        self.new_children = []
        self.made_changes = False
    
    def process_children(self, children_to_process):
        """子要素リストを処理"""
        for child_idx, child in enumerate(children_to_process):
            if self.current_mode == ProcessingMode.LOOKING_FOR_FIRST_CHILD:
                self._process_first_child_mode(child, child_idx, children_to_process)
            elif self.current_mode == ProcessingMode.NORMAL_PROCESSING:
                self._process_normal_mode(child, child_idx, children_to_process)
            else:
                self.new_children.append(child)
        return self.made_changes
    
    def _process_first_child_mode(self, child, child_idx, children_to_process):
        """最初の子要素モードの処理"""
        # 現在の処理を関数化
        pass
    
    def _process_normal_mode(self, child, child_idx, children_to_process):
        """通常モードの処理"""
        # 現在の処理を関数化
        pass
```

**推定工数**: ~~3-5日~~ ✅ 完了

#### ~~提案2: 処理タイプごとの関数分割~~ ✅ 実施済み

```python
def process_list_element_first_mode(child, config, stats, parent_elem, seen_label_texts):
    """最初のモードでのList要素処理"""
    # 現在の683-731行目の処理を関数化
    pass

def process_list_element_normal_mode(child, last_child, config, stats, parent_elem, 
                                     seen_label_texts, children_to_process, child_idx):
    """通常モードでのList要素処理"""
    # 現在の744-1082行目の処理を関数化
    pass

def handle_no_column_list(child, config, stats, parent_elem, last_child):
    """ColumnなしListの処理"""
    # ColumnなしListの処理を統一
    pass

def handle_column_list(child, col_count, col1_text, has_label, config, stats, 
                       parent_elem, last_child, seen_label_texts):
    """ColumnありListの処理"""
    # ColumnありListの処理を統一
    pass

def handle_multi_column_list(child, col_count, col1_text, config, stats, 
                              parent_elem, last_child, seen_label_texts):
    """Columnが3つ以上のListの処理"""
    # 複数Column処理を統一
    pass
```

**推定工数**: ~~2-3日~~ ✅ 完了

---

### 1.2 タイトルテキスト取得の重複削減 ✅ 完了

**問題の深刻度: 中**

~~`current_title_text`の取得パターンが8箇所以上で重複しています。~~

**✅ 対応完了** (2024年12月)

`get_title_text()`関数を作成し、すべての箇所で使用するように統一しました。

**現状**:
```python
# 840行目、909行目、1030行目などで重複
current_title_text = "".join(last_child.find(config.title_tag).itertext()).strip() if last_child.find(config.title_tag) is not None else ""
```

**提案**:
```python
def get_title_text(element, config: ConversionConfig) -> str:
    """
    要素のタイトルテキストを取得（共通化関数）
    
    Args:
        element: 要素
        config: 変換設定
    
    Returns:
        タイトルテキスト（要素がNoneまたはタイトルが存在しない場合は空文字列）
    """
    if element is None:
        return ""
    title_elem = element.find(config.title_tag)
    if title_elem is None:
        return ""
    return "".join(title_elem.itertext()).strip()
```

**修正箇所**: ~~8箇所以上~~ ✅ 完了
**推定工数**: ~~0.5日~~ ✅ 完了

---

### 1.3 アルファベットラベル処理ロジックの統一 ✅ 完了

**問題の深刻度: 中**

~~アルファベットラベル付きListを子要素として取り込む処理が複数箇所で重複しています（840-874行目、908-931行目など）。~~

**✅ 対応完了** (2024年12月)

`should_append_alphabet_label_as_child()`関数を作成し、アルファベットラベル処理ロジックを統一しました。

**提案**:
```python
def should_append_alphabet_label_as_child(last_child, child, col1_text, config: ConversionConfig) -> bool:
    """
    アルファベットラベル付きListを子要素として取り込むべきか判定
    
    Args:
        last_child: 最後に処理した子要素
        child: 現在処理中のList要素
        col1_text: Column1のテキスト
        config: 変換設定
    
    Returns:
        子要素として取り込むべき場合True
    """
    if last_child is None:
        return False
    
    current_title_text = get_title_text(last_child, config)
    list_label_id = detect_label_id(col1_text)
    
    if not is_alphabet_label(list_label_id):
        return False
    
    # Paragraphの場合の処理
    if config.parent_tag == 'Paragraph' and not current_title_text:
        return True
    
    # Itemの場合の処理
    if config.parent_tag == 'Item' and current_title_text:
        current_title_label_id = detect_label_id(current_title_text)
        is_current_title_label = current_title_label_id is not None
        
        if is_alphabet_label(current_title_label_id):
            return current_title_text == col1_text
        else:
            return not is_current_title_label or current_title_text == col1_text
    
    return False
```

**修正箇所**: ~~3箇所以上~~ ✅ 完了
**推定工数**: ~~1日~~ ✅ 完了

---

### 1.4 後続要素のアルファベットラベルチェック処理の関数化 ✅ 完了

**問題の深刻度: 中**

~~780-796行目の「後続の要素を確認してアルファベットラベル付きListがあるかチェック」処理を関数化します。~~

**✅ 対応完了** (2024年12月)

`has_following_alphabet_label_list()`関数を作成し、後続要素のアルファベットラベルチェック処理を関数化しました。

**提案**:
```python
def has_following_alphabet_label_list(children_to_process, current_idx):
    """
    後続の要素にアルファベットラベル付きListがあるかチェック
    
    Args:
        children_to_process: 処理対象の子要素リスト
        current_idx: 現在のインデックス
    
    Returns:
        アルファベットラベル付きListがある場合True
    """
    if current_idx + 1 >= len(children_to_process):
        return False
    
    next_child = children_to_process[current_idx + 1]
    if not is_list_element(next_child):
        return False
    
    next_col1_sentence, _, _ = get_list_columns(next_child)
    next_col1_text = get_column_text(next_col1_sentence)
    if not next_col1_text:
        return False
    
    # detect_label_idを使用してアルファベットラベルかチェック
    next_list_label_id = detect_label_id(next_col1_text)
    if is_alphabet_label(next_list_label_id):
        return True
    
    # 正規表現パターンでもチェック（detect_label_idが失敗した場合のフォールバック）
    return bool(re.match(r'^[（(]?[ａ-ｚA-ZＡ-Ｚ]+[）)]$', next_col1_text))
```

**修正箇所**: ~~1箇所~~ ✅ 完了
**推定工数**: ~~0.5日~~ ✅ 完了

---

### 1.5 `process_normal_mode_list_element`関数のさらなる分割 ✅ 完了

**問題の深刻度: 高**

~~`process_normal_mode_list_element()`関数は約330行とまだ長く、複雑な条件分岐が含まれています。特に以下の処理パターンが重複しています：~~

**✅ 対応完了** (2024年12月)

以下の対応を実施しました：

1. **共通処理の関数化**
   - `handle_labeled_list_with_same_hierarchy()`関数の作成（26行）
   - `handle_labeled_list_with_different_hierarchy()`関数の作成（83行）

2. **Column数による処理分岐の関数化**
   - `handle_no_column_list_in_normal_mode()`関数の作成（46行）
   - `handle_multi_column_labeled_list()`関数の作成（27行）
   - `handle_multi_column_non_labeled_list()`関数の作成（24行）
   - `handle_two_column_labeled_list()`関数の作成（71行）
   - `handle_two_column_non_labeled_list()`関数の作成（34行）

**実施前**: 約330行の巨大な関数  
**実施後**: メイン関数約150行 + 7つの専用関数に分割

**改善効果**:
- 可読性の向上: 各関数が単一責任を持つように分割
- 保守性の向上: 処理ロジックが独立した関数に分離され、変更が容易に
- テスト容易性の向上: 各関数を個別にテスト可能
- コードの重複削減: 共通処理を関数化し、重複を削減

**推定工数**: ~~2-3日~~ ✅ 完了

---

## 2. 中優先度リファクタリング

### 2.1 状態管理クラスの導入 ✅ 完了

**問題の深刻度: 中**

~~`process_elements_recursive`内で管理されている状態をクラスとしてカプセル化します。~~

**✅ 対応完了** (2024年12月)

`ProcessingState`クラスを作成し、処理状態をカプセル化しました。

**提案**:
```python
class ProcessingState:
    """処理状態を管理するクラス"""
    def __init__(self):
        self.mode = ProcessingMode.LOOKING_FOR_FIRST_CHILD
        self.last_child = None
        self.seen_label_texts = set()
        self.new_children = []
        self.made_changes = False
    
    def add_seen_label(self, label_text: str):
        """出現したラベルを記録"""
        self.seen_label_texts.add(label_text)
    
    def has_seen_label(self, label_text: str) -> bool:
        """ラベルが既に出現したかチェック"""
        return label_text in self.seen_label_texts
    
    def append_child(self, child):
        """新しい子要素を追加"""
        self.new_children.append(child)
        self.made_changes = True
    
    def append_to_last_child(self, child):
        """最後の子要素に追加"""
        if self.last_child is not None:
            self.last_child.append(child)
            self.made_changes = True
        else:
            self.append_child(child)
```

**推定工数**: ~~1日~~ ✅ 完了

---

### 2.2 マジックナンバー/文字列の定数化 ✅ 完了

**問題の深刻度: 低-中**

~~以下のマジックナンバー/文字列を定数化します。~~

**✅ 対応完了** (2024年12月)

以下の定数を追加しました：
- `DOT_SEPARATED_NUMBER_LABEL_IDS`: ドット区切り数字ラベルIDのリスト
- `STRUCT_ELEMENT_TAGS`: Struct要素のタグリスト
- `MIN_COLUMNS_FOR_MULTI_COLUMN_PROCESSING`: 既に定義済み

**現状の問題**:
- ~~`col_count >= 2` (780行目など)~~ → `config.column_condition_min`を使用
- ~~`col_count > 2` (複数箇所)~~ → `MIN_COLUMNS_FOR_MULTI_COLUMN_PROCESSING`を使用
- ~~`'dot_separated_number_single'`, `'dot_separated_number_double'` (1037行目)~~ → `DOT_SEPARATED_NUMBER_LABEL_IDS`を使用
- ~~`'TableStruct'`, `'FigStruct'`, `'StyleStruct'` (1084行目)~~ → `STRUCT_ELEMENT_TAGS`を使用

**提案**:
```python
# 定数定義セクションに追加
MIN_COLUMNS_FOR_TWO_COLUMN_PROCESSING = 2
MIN_COLUMNS_FOR_MULTI_COLUMN_PROCESSING = 3  # 既に定義済み

DOT_SEPARATED_NUMBER_LABEL_IDS = [
    'dot_separated_number_single',
    'dot_separated_number_double'
]

STRUCT_ELEMENT_TAGS = ['TableStruct', 'FigStruct', 'StyleStruct']
```

**修正箇所**: ~~10箇所以上~~ ✅ 完了
**推定工数**: ~~0.5日~~ ✅ 完了

---

### 2.3 重複するラベル重複チェック処理の統一

**問題の深刻度: 中**

ラベル重複チェック処理が複数箇所で重複しています（763行目、923行目、968行目、1039行目など）。

**現状**:
```python
# 763行目（process_first_child_mode内）
if has_label and state.has_seen_label(col1_text):

# 923行目（process_normal_mode_list_element内）
if has_label and state.has_seen_label(col1_text) and not is_instruction:

# 968行目（process_normal_mode_list_element内）
if has_label and state.has_seen_label(col1_text) and not is_instruction_for_check:

# 1039行目（process_normal_mode_list_element内）
if has_label and state.has_seen_label(col1_text) and not is_instruction_for_check2:
```

**提案**:
```python
def should_skip_duplicate_label(child, col1_text, has_label, seen_label_texts, 
                                 is_instruction: bool = False) -> bool:
    """
    重複ラベルの場合にスキップすべきか判定
    
    Args:
        child: List要素
        col1_text: Column1のテキスト
        has_label: ラベルかどうか
        seen_label_texts: 既に出現したラベルのセット
        is_instruction: 指導項目かどうか
    
    Returns:
        スキップすべき場合True
    """
    # 指導項目の場合は重複チェックをスキップ
    if is_instruction:
        return False
    
    return has_label and col1_text in seen_label_texts
```

**修正箇所**: 4箇所
**推定工数**: 0.5日

---

### 2.4 要素タイプ判定の統一

**問題の深刻度: 低**

`get_element_type()`を使用すべき箇所で直接判定している場合があります。

**現状**:
```python
# 1002行目など
is_column_list_converted_item = bool(title_text)
is_bracket_item = (element_type in ['subject_name', 'instruction', 'grade', 'grade_single', 'grade_double'])
```

**提案**:
```python
def is_column_list_converted_element(element, config: ConversionConfig) -> bool:
    """ColumnありListから変換された要素かどうかを判定"""
    title_text = get_title_text(element, config)
    return bool(title_text)

def is_bracket_converted_element(element_type: str) -> bool:
    """括弧付き見出し系から変換された要素かどうかを判定"""
    BRACKET_ELEMENT_TYPES = ['subject_name', 'instruction', 'grade', 'grade_single', 'grade_double']
    return element_type in BRACKET_ELEMENT_TYPES
```

**推定工数**: 0.5日

---

### 2.5 Column数による処理分岐の統一 ✅ 完了

**問題の深刻度: 中**

~~`process_normal_mode_list_element()`関数内で、Column数による処理分岐が複雑に絡み合っています。~~

**✅ 対応完了** (2024年12月)

1.5のリファクタリングと同時に実施しました。以下の関数を作成し、Column数による処理分岐を統一しました：

- `handle_no_column_list_in_normal_mode()`: ColumnなしListの処理
- `handle_multi_column_labeled_list()`: Columnが3つ以上で最初がラベルのListの処理
- `handle_multi_column_non_labeled_list()`: Columnが3つ以上で最初がラベルではないListの処理
- `handle_two_column_labeled_list()`: Columnが2つで最初がラベルのListの処理
- `handle_two_column_non_labeled_list()`: Columnが2つで最初がラベルでない、またはColumnが1つ以下のListの処理

**推定工数**: ~~1-2日~~ ✅ 完了

---

## 3. 低優先度リファクタリング

### 3.1 エラーハンドリングの強化

**問題の深刻度: 低**

一部の関数で`None`チェックが不足している可能性があります。

**提案**:
- `get_title_text()`などの関数で適切な`None`チェックを追加
- 型ヒントの追加（`Optional`の明示的な使用）

**推定工数**: 1日

---

### 3.2 コメントの改善

**問題の深刻度: 低**

複雑な条件分岐にコメントを追加します。

**提案**:
- テストケース番号（例: テスト21、テスト30、テスト27）への参照をコメントに追加
- 複雑な条件分岐の意図を説明するコメントを追加
- 特に`process_normal_mode_list_element()`内のColumn数による分岐にコメントを追加

**推定工数**: 1日

---

### 3.3 処理モードのEnum化 ✅ 完了

**問題の深刻度: 低**

~~処理モードを定数からEnumに変更します。~~

**✅ 対応完了** (2024年12月)

`ProcessingMode` Enumクラスを作成し、処理モードをEnum化しました。

---

## 4. リファクタリング優先順位まとめ

### 優先度の再評価（2024年12月）

今回の`process_normal_mode_list_element`関数の分割完了に伴い、残りのリファクタリング項目の優先度を再評価しました。

**優先度の判断基準**:
- **高優先度**: コードの構造に大きな影響を与える、または複雑性を大幅に削減する項目
- **中優先度**: コードの可読性・保守性を向上させるが、構造的な影響は限定的な項目
- **低優先度**: コードの品質向上に寄与するが、機能的な改善ではない項目

**再評価の結果**:
- 高優先度の項目はすべて完了 ✅
- 残りの項目は中優先度2項目、低優先度2項目のみ
- 残り工数は約3日と大幅に削減

### ✅ 完了済み項目

1. ✅ **`process_elements_recursive`関数の分割** - ~~推定工数: 3-5日~~ ✅ 完了
   - メイン関数を約43行に簡潔化
   - `process_first_child_mode()`と`process_normal_mode_list_element()`に分割

2. ✅ **タイトルテキスト取得の重複削減** - ~~推定工数: 0.5日~~ ✅ 完了
   - `get_title_text()`関数を作成

3. ✅ **アルファベットラベル処理ロジックの統一** - ~~推定工数: 1日~~ ✅ 完了
   - `should_append_alphabet_label_as_child()`関数を作成

4. ✅ **後続要素のアルファベットラベルチェック処理の関数化** - ~~推定工数: 0.5日~~ ✅ 完了
   - `has_following_alphabet_label_list()`関数を作成

5. ✅ **状態管理クラスの導入** - ~~推定工数: 1日~~ ✅ 完了
   - `ProcessingState`クラスを作成

6. ✅ **マジックナンバー/文字列の定数化** - ~~推定工数: 0.5日~~ ✅ 完了
   - `DOT_SEPARATED_NUMBER_LABEL_IDS`, `STRUCT_ELEMENT_TAGS`などを追加

7. ✅ **処理モードのEnum化** - ~~推定工数: 0.5日~~ ✅ 完了
   - `ProcessingMode` Enumクラスを作成

8. ✅ **`process_normal_mode_list_element`関数のさらなる分割** - ~~推定工数: 2-3日~~ ✅ 完了
   - 約330行から約150行に短縮
   - 7つの専用関数に分割（`handle_labeled_list_with_same_hierarchy`, `handle_labeled_list_with_different_hierarchy`, `handle_no_column_list_in_normal_mode`, `handle_multi_column_labeled_list`, `handle_multi_column_non_labeled_list`, `handle_two_column_labeled_list`, `handle_two_column_non_labeled_list`）

9. ✅ **Column数による処理分岐の統一** - ~~推定工数: 1-2日~~ ✅ 完了
   - 1.5のリファクタリングと同時に実施

### 優先度: 中（中期的に対応推奨）

10. **重複するラベル重複チェック処理の統一** - 推定工数: 0.5日
    - **現状**: 4箇所で重複しているラベル重複チェック処理（789行目、1267行目、1312行目、1353行目）
    - **問題点**: 各箇所で微妙に異なる実装（`is_instruction`チェックの有無、戻り値の違いなど）
    - **提案**: `should_skip_duplicate_label()`関数の作成を検討
    - **優先度の根拠**: 重複コードの削減により保守性が向上するが、現状でも動作に問題はない

11. **要素タイプ判定の統一** - 推定工数: 0.5日
    - **現状**: `is_column_list_converted_item`と`is_bracket_item`が1箇所で使用されている（1039行目、1043行目）
    - **問題点**: インラインでの判定により可読性が低下している可能性
    - **提案**: `is_column_list_converted_element()`などの関数を作成
    - **優先度の根拠**: 可読性の向上に寄与するが、影響範囲が限定的

### 優先度: 低（長期的に対応推奨）

12. **エラーハンドリングの強化** - 推定工数: 1日
    - **現状**: 一部の関数で`None`チェックが不足している可能性がある
    - **提案**: `get_title_text()`などの関数で適切な`None`チェックを追加、型ヒントの追加（`Optional`の明示的な使用）
    - **優先度の根拠**: コードの堅牢性向上に寄与するが、現状でも大きな問題は発生していない

13. **コメントの改善** - 推定工数: 1日
    - **現状**: 複雑な条件分岐にコメントが不足している箇所がある
    - **提案**: テストケース番号（例: テスト21、テスト30、テスト27）への参照をコメントに追加、複雑な条件分岐の意図を説明するコメントを追加
    - **優先度の根拠**: 可読性の向上に寄与するが、機能的な改善ではない

---

## 5. リファクタリング実施時の注意点

### 5.1 テストの重要性

- 既存のテストケースが多数存在する可能性があるため、リファクタリング後は全テストの実行が必須
- リファクタリング前後で出力が同一であることを確認

### 5.2 段階的な実施

- 一度にすべてを変更せず、優先度の高い項目から段階的に実施
- 各リファクタリング後にテストを実行し、問題がないことを確認

### 5.3 バージョン管理

- リファクタリング前のコードをブランチとして保存
- 各リファクタリングを小さなコミットに分割

---

## 6. 期待される効果

### 6.1 コード品質の向上

- **可読性**: 関数の分割により、各関数の責務が明確になる
- **保守性**: 重複コードの削減により、修正箇所が明確になる
- **テスト容易性**: 小さな関数により、単体テストが容易になる

### 6.2 開発効率の向上

- **バグ修正**: 問題箇所の特定が容易になる
- **機能追加**: 新しい機能の追加が容易になる
- **コードレビュー**: 変更内容の理解が容易になる

### 6.3 パフォーマンス

- 大きなパフォーマンス改善は期待できないが、コードの最適化の機会が増える

---

## 7. 実施状況サマリー

### 完了したリファクタリング（2024年12月）

✅ **完了項目数**: 9項目
- `process_elements_recursive`関数の分割
- タイトルテキスト取得の重複削減
- アルファベットラベル処理ロジックの統一
- 後続要素のアルファベットラベルチェック処理の関数化
- 状態管理クラスの導入
- マジックナンバー/文字列の定数化
- 処理モードのEnum化
- **`process_normal_mode_list_element`関数のさらなる分割**（新規完了）
- **Column数による処理分岐の統一**（新規完了）

### 残りのリファクタリング項目

**中優先度**: 2項目
- 重複するラベル重複チェック処理の統一（推定工数: 0.5日）
- 要素タイプ判定の統一（推定工数: 0.5日）

**低優先度**: 2項目
- エラーハンドリングの強化（推定工数: 1日）
- コメントの改善（推定工数: 1日）

**合計残り工数**: 約3日

### リファクタリング進捗状況

- **完了率**: 9/13項目（約69%）
- **高優先度項目**: 100%完了 ✅
- **中優先度項目**: 1/3項目完了（約33%）
- **低優先度項目**: 0/2項目完了（0%）

---

## 8. 結論

`xml_converter.py`の主要なリファクタリングは完了しました。特に以下の改善により、コードの可読性と保守性が大幅に向上しました：

1. **`process_elements_recursive`関数の分割**: 約465行から約43行に短縮
2. **`process_normal_mode_list_element`関数の分割**: 約330行から約150行に短縮し、7つの専用関数に分割
3. **共通処理の関数化**: 重複コードを削減し、保守性を向上

**完了したリファクタリングの効果**:
- ✅ **可読性の向上**: 各関数が単一責任を持つように分割され、コードの理解が容易に
- ✅ **保守性の向上**: 処理ロジックが独立した関数に分離され、変更が容易に
- ✅ **テスト容易性の向上**: 小さな関数により、単体テストが容易に
- ✅ **コードの重複削減**: 共通処理を関数化し、重複を削減

**次のステップ**（優先度順）:
1. **重複するラベル重複チェック処理の統一**（中優先度、推定工数: 0.5日）
   - 4箇所で重複しているラベル重複チェック処理を統一
   - `should_skip_duplicate_label()`関数の作成を検討

2. **要素タイプ判定の統一**（中優先度、推定工数: 0.5日）
   - `is_column_list_converted_element()`などの関数を作成
   - より明確な関数名での統一を検討

3. **エラーハンドリングの強化**（低優先度、推定工数: 1日）
   - `None`チェックの追加
   - 型ヒントの改善

4. **コメントの改善**（低優先度、推定工数: 1日）
   - テストケース番号への参照を追加
   - 複雑な条件分岐の意図を説明

**推奨アプローチ**:
1. 中優先度の項目から順に実施（残り工数: 約1日）
2. 各リファクタリング後にテストを実行
3. 段階的に実施し、リスクを最小化

**現状の評価**:
- 高優先度のリファクタリングはすべて完了 ✅
- コードの主要な構造改善は完了し、残りは細かな改善項目のみ
- 残りのリファクタリングを実施することで、コードの品質と保守性がさらに向上することが期待されます
