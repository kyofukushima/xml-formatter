# Paragraph処理ドキュメント構成

このディレクトリには、Paragraph要素の処理に関するドキュメントが格納されています。

## 📁 ドキュメント構造

### 共通定義

| ファイル | 内容 | 参照元 |
|---------|------|--------|
| **common/label_definitions.md** | 項目ラベルの定義（14種類のパターン、階層レベル、優先順位） | すべてのロジックドキュメント |

### Paragraph処理の詳細ドキュメント

実装の実行順序に従って、以下のドキュメントを参照してください：

| ステップ | ファイル | 対応スクリプト | 処理内容 |
|---------|---------|---------------|---------|
| **Step 1** | logic2_1_ParagraphNum.md | convert_paragraph_step1.py | ParagraphNum補完 |
| **Step 2** | logic2_2_Paragraph_text.md | convert_paragraph_step2.py | ParagraphSentence作成 |
| **Step 3** | logic2_3_Paragraph_textitem.md | convert_paragraph_step2.py<br>convert_paragraph_step3.py | Item変換・Paragraph分割 |
| **Step 4** | logic2_4_ParagraphSplitSentence.md | convert_paragraph_step4.py | ParagraphSentence分割 |

### 実装ガイドライン

| ファイル | 内容 | 対象読者 |
|---------|------|---------|
| **logic2_implementation_guide.md** | 実装アルゴリズム、注意事項、推奨事項 | 開発者 |

## 🔄 処理フロー

```
入力XML
  ↓
[Step 1] ParagraphNum補完
  ├─ logic2_1_ParagraphNum.md
  └─ convert_paragraph_step1.py
  ↓
[Step 2] ParagraphSentence作成
  ├─ logic2_2_Paragraph_text.md
  └─ convert_paragraph_step2.py
  ↓
[Step 3] Item変換・Paragraph分割
  ├─ logic2_3_Paragraph_textitem.md
  ├─ convert_paragraph_step2.py
  └─ convert_paragraph_step3.py
  ↓
[Step 4] ParagraphSentence分割
  ├─ logic2_4_ParagraphSplitSentence.md
  └─ convert_paragraph_step4.py
  ↓
出力XML
```

## 📝 前提条件

すべてのParagraph処理の前に、Article処理が完了している必要があります：
- **Article処理**: `logic1_Article.md` + `convert_article_focused.py`

## 🗂️ 旧ドキュメント

以下のファイルは参考資料として `old/` フォルダに移動されました：

| ファイル | 内容 | 理由 |
|---------|------|------|
| **old/logic2_Paragraph.markdown** | 包括的マスター仕様書（処理1〜7） | 内容が重複・分散化のため |

このマスター仕様書の内容は以下に再編成されました：
- **処理1〜4** → logic2_1〜2_4の各詳細ドキュメント
- **項目ラベル定義** → common/label_definitions.md
- **実装アルゴリズム・推奨事項** → logic2_implementation_guide.md

## 🚀 使い方

### 1. 新しい処理を実装する場合

1. `common/label_definitions.md` で項目ラベルの定義を確認
2. `logic2_implementation_guide.md` で実装アルゴリズムと注意事項を確認
3. 該当するステップのドキュメント（logic2_1〜2_4）を参照
4. 対応するスクリプトを実行または修正

### 2. 既存の処理を理解する場合

1. 処理フローから該当するステップを特定
2. ステップのドキュメントを読む
3. 必要に応じて実装ガイドラインを参照

### 3. テストを実行する場合

```bash
# Step 1: ParagraphNum補完
python3 convert_paragraph_step1.py input.xml

# Step 2: ParagraphSentence作成
python3 convert_paragraph_step2.py input_step1.xml

# Step 3: Item変換・Paragraph分割
python3 convert_paragraph_step3.py input_step2.xml

# Step 4: ParagraphSentence分割
python3 convert_paragraph_step4.py input_step3.xml
```

## 📞 参照

- **プロジェクト全体のドキュメント**: `docs/kokuji_markup_policy.md`
- **XMLスキーマ定義**: `schema/kokuji20250320_asukoe.xsd`
- **その他のロジックドキュメント**: 
  - `logic1_Article.md` (Article処理)
  - `logic3_*.md` (Item処理)
  - `logic4_*.md` (Subitem1処理)
  - `logic5_*.md` (Subitem2処理)
  - `logic6_*.md` (Subitem3処理)

---

**最終更新日**: 2025年11月7日  
**整理内容**: 重複排除、共通部分外部化、誤記載修正、実装ガイドライン分離
