# Article特化型処理の結果分析

## 実施日
2025年10月28日

## 概要
Article要素に特化した階層限定型変換スクリプト（`convert_article_focused.py`）を実装し、`test_input5.xml`に対して実行した結果を分析しました。

---

## 1. 変換結果の統計

### 要素数の比較

| 要素名 | 入力 | 期待値 | 実際 | 差分 | 状態 |
|--------|------|--------|------|------|------|
| **Article** | 13 | 14 | 14 | 0 | ✅ **一致** |
| **Paragraph** | 13 | 37 | 113 | **+76** | ⚠️ **過剰** |
| **Item** | 0 | 86 | 0 | -86 | ✅ **正常**（別フェーズ） |
| **List** | 593 | 38 | 484 | +446 | 🔄 **部分変換** |

### 変換統計

- **処理したArticle**: 13個
- **分割したArticle**: 1個 ✅（期待値: 1個）
- **作成したParagraph**: 99個 ⚠️（期待値: 22個）
- **変換したList**: 108個 🔄（期待値: 部分的に変換）

---

## 2. 問題点の分析

### 問題1: Paragraph要素の過剰作成

**現象:**
- 期待値: 37個
- 実際: 113個
- 差分: +76個（約3倍）

**原因:**
現在のスクリプトは、Article内のすべての**数字ラベル**を持つList要素を新しいParagraphに変換しています。

しかし、`修正ロジック分析.md`のルール3-2によると：

| ラベルパターン | 判定条件 | 変換先 | 説明 |
|--------------|---------|--------|------|
| 数字 | **連続番号** | 新しい`Paragraph` | 前のParagraphNumと連続（１→２→３） |
| 数字 | **1から開始** | `Item` | 新しい系列の開始（１、２、３...） |
| 括弧数字 | - | `Item` | 項目の詳細展開 |

**具体例:**

```xml
<!-- Article内の最初のParagraphに「１」がある場合 -->
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>...</ParagraphSentence>
  <List>
    <ListSentence>
      <Column><Sentence>２</Sentence></Column>  <!-- 連続番号 → 新しいParagraph -->
      <Column><Sentence>...</Sentence></Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column><Sentence>（１）</Sentence></Column>  <!-- 括弧数字 → Item（別フェーズ） -->
      <Column><Sentence>...</Sentence></Column>
    </ListSentence>
  </List>
</Paragraph>
```

**現在の実装の問題:**
- `（１）`のような括弧数字も、数字として認識されてParagraphに変換されている可能性
- 連続性の判定が実装されていない（すべての数字を新しいParagraphにしている）

---

## 3. Article特化処理の正しいスコープ

### Article特化処理で行うべきこと

1. ✅ **Article要素の分割**
   - 「第○」パターンでArticleを分割
   - **実装済み**: 1個のArticle分割が正常に動作

2. ⚠️ **Article内のParagraph作成（連続番号のみ）**
   - 数字ラベル（１, ２, ３...）が**連続している場合のみ**
   - 新しいParagraphを作成
   - **問題あり**: 連続性の判定が未実装

### Article特化処理で行うべきでないこと

1. ❌ **Item要素の作成**
   - 括弧数字（（１）, （２）...）
   - 1から開始する数字系列
   - これらは**Item特化処理**（別フェーズ）で処理

2. ❌ **Subitem要素の作成**
   - カタカナ、括弧カタカナなど
   - これらも**Subitem特化処理**（別フェーズ）で処理

---

## 4. 修正方針

### 修正案1: 連続番号判定の実装

**追加が必要な機能:**
```python
def is_continuous_paragraph_num(self, current_label: str, previous_para_nums: List[str]) -> bool:
    """
    現在のラベルが前のParagraphNumと連続しているかを判定
    
    Args:
        current_label: 現在のラベル（例: "２"）
        previous_para_nums: 前のParagraphNumのリスト（例: ["１"]）
    
    Returns:
        bool: 連続している場合True
    """
    if not previous_para_nums:
        # 最初のParagraphの場合、"１"または"1"ならTrue
        return self.normalize_number(current_label) == 1
    
    last_num = self.normalize_number(previous_para_nums[-1])
    current_num = self.normalize_number(current_label)
    
    # 連続性を確認（last_num + 1 == current_num）
    return current_num == last_num + 1

def normalize_number(self, label: str) -> int:
    """
    全角・半角数字を統一して整数に変換
    
    Args:
        label: ラベル文字列（例: "１", "2"）
    
    Returns:
        int: 整数値
    """
    # 全角数字を半角に変換
    label = label.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
    return int(label)
```

**適用箇所:**
`convert_lists_to_paragraphs_in_article`メソッド内で、数字ラベルを検出した際に：
1. 前のParagraphNumのリストを維持
2. `is_continuous_paragraph_num`で連続性を判定
3. 連続している場合のみ新しいParagraphを作成
4. 連続していない場合はList要素として保持（Item特化処理で処理）

### 修正案2: 括弧数字の除外

**追加が必要な機能:**
```python
def is_pure_number_label(self, label: str) -> bool:
    """
    純粋な数字ラベルかを判定（括弧なし）
    
    Args:
        label: ラベル文字列
    
    Returns:
        bool: 純粋な数字ならTrue、括弧付きならFalse
    """
    if not label:
        return False
    
    label = label.strip()
    
    # 括弧付き数字パターン
    if re.match(r'^[（(][0-9０-９]+[）)]$', label):
        return False  # 括弧付きはItem候補なので除外
    
    # 純粋な数字パターン
    return re.match(r'^[0-9０-９]+$', label) is not None
```

**適用箇所:**
`is_paragraph_label`メソッドを置き換え、または内部で呼び出し。

---

## 5. 推奨される実装順序

### Phase 1: Article分割のみ（現状維持）
- ✅ 「第○」パターンでArticle分割
- ✅ 正常に動作中

### Phase 2: 連続Paragraph作成の精緻化（次のステップ）
1. `is_pure_number_label`の実装
2. `is_continuous_paragraph_num`の実装
3. `convert_lists_to_paragraphs_in_article`の修正
4. テスト実行と結果検証

### Phase 3: Item特化処理との連携
- Article特化処理で作成されたParagraphを入力として
- Item特化処理で括弧数字や1から開始する系列を処理

---

## 6. テスト戦略

### テストケース1: Article分割

**入力:**
```xml
<Article>
  <ArticleTitle>第１</ArticleTitle>
  <Paragraph>
    <List>
      <Column><Sentence>第２</Sentence></Column>
      <Column><Sentence>各科目</Sentence></Column>
    </List>
  </Paragraph>
</Article>
```

**期待される出力:**
```xml
<Article Num="1">
  <ArticleTitle>第１</ArticleTitle>
  ...
</Article>
<Article Num="2">
  <ArticleTitle>第２</ArticleTitle>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>各科目</Sentence>
    </ParagraphSentence>
  </Paragraph>
</Article>
```

**結果:** ✅ **成功**

### テストケース2: 連続Paragraph作成

**入力:**
```xml
<Article>
  <Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>...</ParagraphSentence>
    <List>
      <Column><Sentence>２</Sentence></Column>
      <Column><Sentence>学校の教育活動を...</Sentence></Column>
    </List>
  </Paragraph>
</Article>
```

**期待される出力:**
```xml
<Article>
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
</Article>
```

**結果:** ⚠️ **現在は成功するが、過剰変換の可能性**

### テストケース3: 括弧数字の保持

**入力:**
```xml
<Article>
  <Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>...</ParagraphSentence>
    <List>
      <Column><Sentence>（１）</Sentence></Column>
      <Column><Sentence>基礎的・基本的な知識...</Sentence></Column>
    </List>
  </Paragraph>
</Article>
```

**期待される出力:**
```xml
<Article>
  <Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>...</ParagraphSentence>
    <List>
      <Column><Sentence>（１）</Sentence></Column>
      <Column><Sentence>基礎的・基本的な知識...</Sentence></Column>
    </List>
  </Paragraph>
</Article>
```

**結果:** ❌ **現在はParagraphに変換されている可能性**（要検証）

---

## 7. 次のアクションアイテム

### 優先度: 高

1. **連続番号判定の実装**
   - `is_continuous_paragraph_num`メソッドの追加
   - `normalize_number`メソッドの追加
   - 前のParagraphNumリストの維持

2. **括弧数字の除外**
   - `is_pure_number_label`メソッドの追加
   - `is_paragraph_label`メソッドの修正

3. **テストケース3の検証**
   - 括弧数字が保持されているか確認
   - 過剰変換の具体的な箇所を特定

### 優先度: 中

4. **詳細なログ出力**
   - どのList要素が変換されたか
   - どのList要素が保持されたか
   - 判定理由のログ

5. **統合テスト**
   - Article特化 + Item特化の連続実行
   - 最終的な要素数の確認

---

## 8. 結論

### 成功した点

✅ **Article要素の分割**: 期待通り1個のArticleが分割され、14個のArticleが作成されました。

✅ **基本的な変換ロジック**: 数字ラベルを持つList要素からParagraphを作成する基本機能は動作しています。

### 改善が必要な点

⚠️ **Paragraph要素の過剰作成**: 連続性判定の欠如により、76個余分なParagraphが作成されています。

⚠️ **括弧数字の処理**: 括弧数字（（１）, （２）...）がParagraphに変換されている可能性があります。これらはItem特化処理で扱うべきです。

### 推奨される次のステップ

1. **連続番号判定の実装** → Paragraph過剰作成の解消
2. **括弧数字の除外** → Article/Item処理の明確な分離
3. **統合テスト** → Article特化 + Item特化の連続実行で全体動作確認

---

**作成日**: 2025年10月28日  
**スクリプト**: `convert_article_focused.py`  
**入力ファイル**: `test_input5.xml`  
**出力ファイル**: `test_input5_article_converted.xml`

