# Paragraph処理 実装ガイドライン

このドキュメントは、Paragraph関連の処理を実装する際の参考資料です。

## 項目ラベル定義

項目ラベルの詳細な定義については、[common/label_definitions.md](common/label_definitions.md) を参照してください。

---

## 実装アルゴリズム

### 階層判定アルゴリズム（擬似コード）

```python
def determine_hierarchy_action(current_level, new_label):
    """
    現在の階層レベルと新しいラベルから、実行すべきアクションを決定
    
    Args:
        current_level (int): 現在の階層レベル (1-7)
        new_label (str): 到達した項目ラベル
    
    Returns:
        dict: {
            'action': 'create_child' | 'create_sibling' | 'close_and_create',
            'target_level': int,
            'empty_levels': List[int]  # 空で作成する中間階層
        }
    """
    new_level = get_hierarchy_level(new_label)
    
    if new_level > current_level:
        # 深い階層への移行
        if new_level - current_level == 1:
            # 直接の子要素
            return {
                'action': 'create_child',
                'target_level': new_level,
                'empty_levels': []
            }
        else:
            # レベル差が2以上 → 空の中間要素を作成
            empty_levels = list(range(current_level + 1, new_level))
            return {
                'action': 'create_child_with_intermediates',
                'target_level': new_level,
                'empty_levels': empty_levels
            }
    
    elif new_level == current_level:
        # 同じ階層 → 兄弟要素
        return {
            'action': 'create_sibling',
            'target_level': new_level,
            'empty_levels': []
        }
    
    else:  # new_level < current_level
        # 浅い階層への戻り
        close_levels = list(range(new_level + 1, current_level + 1))
        return {
            'action': 'close_and_create',
            'target_level': new_level,
            'close_levels': close_levels
        }
```

### ラベル分離アルゴリズム（擬似コード）

```python
def split_label_and_text(sentence_text):
    """
    Sentence要素内の「ラベル＋スペース＋テキスト」を分離
    
    Args:
        sentence_text (str): Sentence要素のテキスト
    
    Returns:
        Tuple[Optional[str], Optional[str]]: (ラベル, 残りのテキスト)
    """
    # 優先順位順にパターンマッチング
    patterns = [
        r'^〔.+〕$',  # 括弧科目名
        r'^第[0-9０-９一二三四五六七八九十百千]+[\s　]+(.+)$',  # 第○パターン
        r'^[（(]{2}[ア-ヴ]+[）)]{2}[\s　]+(.+)$',  # 二重括弧カタカナ
        r'^[（(][a-zａ-ｚ]+[）)][\s　]+(.+)$',  # 括弧アルファベット
        r'^[（(][ア-ヴ]+[）)][\s　]+(.+)$',  # 括弧カタカナ
        r'^[（(][0-9０-９]+[）)][\s　]+(.+)$',  # 括弧数字
        r'^[ア-ヴ]+[\s　]+(.+)$',  # カタカナ
        r'^[a-zA-Zａ-ｚＡ-Ｚ]+[\s　]+(.+)$',  # アルファベット
        r'^[0-9０-９]+[\s　]+(.+)$',  # 数字
    ]
    
    for pattern in patterns:
        match = re.match(pattern, sentence_text)
        if match:
            # ラベル部分を抽出（スペースの前まで）
            label = sentence_text.split('[\s　]')[0]
            # 残りのテキストを抽出
            text = match.group(1) if match.groups() else None
            return (label, text)
    
    # マッチしない場合
    return (None, sentence_text)
```

### 要素作成フロー

```
1. List要素を走査
   ↓
2. ラベル判定
   - Column構造あり → Column[0]からラベル抽出
   - Column構造なし → Sentenceテキストから分離
   ↓
3. 階層レベル判定
   - get_hierarchy_level(label)
   ↓
4. アクション決定
   - determine_hierarchy_action(current_level, label)
   ↓
5. 要素作成
   - 深い階層: create_child_element()
   - 同じ階層: create_sibling_element()
   - 浅い階層: close_elements() + create_element()
   ↓
6. Title/Sentence挿入
   - ラベル → Title要素
   - テキスト → Sentence要素
   ↓
7. Num属性振り直し
   - 親要素ごとにリセット
```

---

## 注意事項とエッジケース

### 注意事項

1. **ラベルの判定は優先順位順に行う**（[common/label_definitions.md](common/label_definitions.md)参照）
2. **全角・半角の両方に対応**する
3. **括弧の種類**（全角括弧「（）」と半角括弧「()」）の両方に対応する
4. **階層レベルの飛び越し**（例: 数字 → 括弧カタカナ）に対応し、必要に応じて空の中間要素を作成する
5. **Num属性は親要素が変わるたびにリセット**する

### エッジケース

#### ケース1: 連続する同じラベル

**入力:**
```xml
<List><Sentence>１</Sentence> + <Sentence>項目1</Sentence></List>
<List><Sentence>１</Sentence> + <Sentence>項目2</Sentence></List>
```

**処理:**
- 同じラベル「１」が連続する場合
- 1つ目は新規作成、2つ目も兄弟要素として作成（Num="1", Num="2"）

#### ケース2: ParagraphNumが空で最初がItem相当ラベル

**シナリオ:**
- ParagraphNum: 空
- 最初のList: （１）項目1

**処理:**
- ParagraphNumは空のまま
- ParagraphSentenceは作成しない
- 直接Item要素を作成

#### ケース3: TableStruct/FigStruct要素の処理

**注意:**
- TableStruct、FigStruct要素は通常の階層処理の対象外
- これらの要素内のList要素は変換しない
- 元の構造をそのまま保持

#### ケース4: 空のTitle/Sentenceの扱い

**ルール:**
- Title要素: 空文字列を許可（括弧科目名パターン等）
- Sentence要素: 空文字列を許可（中間階層の空要素）
- ただし、両方が空の場合は要素自体を作成しない場合もある

---

## 実装時の推奨事項

### 段階的実装

1. **Phase 1: 基本パターン**
   - 数字、括弧数字、カタカナのみ対応
   - 階層レベル1-3のみ

2. **Phase 2: 拡張パターン**
   - 括弧カタカナ、アルファベット追加
   - 階層レベル4-7対応

3. **Phase 3: 特殊パターン**
   - 括弧科目名
   - 第○パターン
   - 空の中間要素自動作成

4. **Phase 4: エッジケース**
   - 全角・半角混在
   - 括弧の種類混在
   - 階層レベルの飛び越し

### テストケース

各パターンごとに以下のテストケースを作成：

1. **正常系**
   - 標準的な階層構造
   - 連続する同じレベルのラベル

2. **異常系**
   - 階層レベルの飛び越し（2段階以上）
   - 浅い階層への急な戻り

3. **エッジケース**
   - 空のParagraphNum
   - 括弧科目名
   - TableStruct/FigStruct内のList

---

## 主要な処理パターン

### 階層判定の3パターン

1. **同じ階層レベル**
   - 兄弟要素として作成
   - Num属性を連番で付与

2. **深い階層レベル（下位）**
   - 子要素として作成
   - レベル差が2以上の場合、空の中間要素を自動作成

3. **浅い階層レベル（上位）**
   - 該当レベルまですべての要素を閉じる
   - 新しい要素を作成
   - カウンタをリセット

### 変換の4パターン

1. **Column構造** → Title + Sentence
2. **ラベル+スペース+テキスト** → Title + Sentence  
3. **通常テキスト続き** → List要素として子要素化
4. **深い階層移行** → Subitem要素作成

---

## 実装の推奨順序

### Phase 1: ラベルユーティリティ（基盤）

```python
# utils/label_utils.py
- detect_label_pattern(label) → str
- get_hierarchy_level(label) → int
- split_label_and_text(text) → Tuple[str, str]
- determine_hierarchy_action(current, new) → dict
```

**目的:** すべての特化スクリプトで共通利用

### Phase 2: Article特化スクリプト（完了済み）

```
✅ convert_article_focused.py
- 第○パターンの検出
- Article分割処理
- Num属性振り直し（親要素ごと）
```

### Phase 3: Paragraph特化スクリプト

```
convert_paragraph_step1.py ✅ 完了
- ParagraphNum補完

convert_paragraph_step2.py ✅ 完了
- ParagraphSentence作成

convert_paragraph_step3.py ✅ 完了
- ListからItemへの変換
- Paragraph分割

convert_paragraph_step4.py ✅ 完了
- ParagraphSentence分割
```

### Phase 4: Item特化スクリプト

```
convert_item_focused.py
- 括弧数字ラベルの検出
- Item作成
- 後続List要素の子要素化
- 括弧科目名パターン対応
```

**対象:**
- Column構造の処理
- ラベル+スペース+テキストの処理
- 通常テキスト続きの処理
- 括弧科目名パターンの処理

### Phase 5: Subitem特化スクリプト

```
convert_subitem_focused.py
- カタカナ、括弧カタカナ、二重括弧カタカナ
- アルファベット（全半角、括弧付き）
- 深い階層（Subitem1～10）
- 空の中間要素自動作成
```

**対象:**
- 階層レベル3-7の処理
- 空の中間要素作成

### Phase 6: 統合テスト

```
- Article → Paragraph → Item → Subitem の順に連続実行
- test_input5.xml → test_output5.xml との比較
- エッジケースのテスト
```

---

## 参照ドキュメント

| ドキュメント | 説明 | 関連内容 |
|-------------|------|---------|
| **common/label_definitions.md** | 項目ラベルの定義 | 14種類のパターン、階層レベル、優先順位 |
| **logic2_1_ParagraphNum.md** | 処理1の詳細 | ParagraphNum補完 |
| **logic2_2_Paragraph_text.md** | 処理2の詳細 | ParagraphSentence作成 |
| **logic2_3_Paragraph_textitem.md** | 処理3の詳細 | Item変換・Paragraph分割 |
| **logic2_4_ParagraphSplitSentence.md** | 処理4の詳細 | ParagraphSentence分割 |
| **kokuji_markup_policy.md** | マークアップポリシー | パターン1-22 |
| **kokuji20250320.xsd** | XMLスキーマ定義 | 要素定義 |

---

**文書作成日:** 2025年11月7日  
**用途:** Paragraph処理実装時の参考資料  
**対象読者:** 開発者
