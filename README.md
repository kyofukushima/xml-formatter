# XML パイプライン処理ガイド

## 概要

`scripts/run_pipeline.sh` は、入力フォルダ内の全XMLファイルを順次変換し、出力フォルダに最終結果と検証レポートを保存するパイプラインスクリプトです。構造変換に加え、XML構文チェックとテキスト内容の整合性検証を自動で行います。

---

## セットアップ

### 必要な環境
- Python 3.7 以上
- lxml ライブラリ（各変換スクリプトで使用）

### 事前準備

```bash
pip install lxml
chmod +x scripts/run_pipeline.sh
mkdir -p input output
```

---

## 使い方

### コマンド

```bash
./scripts/run_pipeline.sh <input_folder> <output_folder> [mode]
```

- `<input_folder>`: 処理対象のXMLを置くフォルダ（配下の `*.xml` をすべて処理）
- `<output_folder>`: 最終出力とレポートの保存先
- `[mode]`: `all`（デフォルト・連続実行） / `step`（各ステップ後に一時停止）

#### 例

```bash
# 連続実行
./scripts/run_pipeline.sh ./input ./output

# ステップごとに確認しながら
./scripts/run_pipeline.sh ./input ./output step
```

---

## 処理フロー（実行順）

パイプラインは以下の順序で変換を行います。

| 順序 | スクリプト | 主な処理内容 |
|---|---|---|
| 1 | `preprocess_non_first_sentence_to_list.py` | 2個目以降のSentenceをListに変換 |
| 2 | `convert_article_focused.py` | Article 要素の分割と調整 |
| 3 | `convert_paragraph_step3.py` | Paragraph 処理（step3） |
| 4 | `convert_paragraph_step4.py` | Paragraph 処理（step4） |
| 5 | `convert_item_step0.py` | Item 変換 |
| 6 | `convert_subitem1_step0.py` | Subitem1 変換 |
| 7 | `convert_subitem2_step0.py` | Subitem2 変換 |
| 8 | `convert_subitem3_step0.py` | Subitem3 変換 |
| 9 | `convert_subitem4_step0.py` | Subitem4 変換 |
| 10 | `convert_subitem5_step0.py` | Subitem5 変換 |
| 11 | `convert_subitem6_step0.py` | Subitem6 変換 |
| 12 | `convert_subitem7_step0.py` | Subitem7 変換 |
| 13 | `convert_subitem8_step0.py` | Subitem8 変換 |
| 14 | `convert_subitem9_step0.py` | Subitem9 変換 |
| 15 | `convert_subitem10_step0.py` | Subitem10 変換（最終） |

### 検証
- **構文検証**: `validate_xml.py` が最初に実行され、結果は `intermediate_files/<元ファイル名>/...-parse_validation.txt` に保存されます。
- **テキスト内容検証**: パイプライン完了後に `compare_xml_text_content.py` を実行し、元XMLとのテキスト一致を確認します（レポート: `...-validation_report.txt`）。

### 文頭全角スペース補填（オプション）

告示データ整備方針に基づき、段落冒頭の1字下げを全角スペースで再現する後処理を用意しています（`scripts/postprocess_fullwidth_space.py`）。Webアプリのサイドバーにあるチェックボックスで適用の有無を事前に指定できます。また、専用の設定ページ（`pages/04_🔤_全角スペース補填設定.py`）では、各オプションのXML例（補填前→補填後）を確認しながら設定できます。例の「補填後」は実際の補填処理をサンプルXMLに適用した結果を表示するため、例示と実動作は常に一致します。設定はサイドバーと共有されます。

- **対象**: ①Title要素が空のItem/Subitem1～10のSentence冒頭、②`LineBreak="true"`のColumn内Sentence冒頭、③List内Sentence冒頭（サブオプション、デフォルト対象外）
- **除外**: 上記①②③に該当しても、次のSentenceには補填しません。
  - テキストを一切含まないSentence（空行防止用の空要素、`QuoteStruct`/`Fig`等の数式画像のみのSentence）、および冒頭が`ArithFormula`/`QuoteStruct`/`Fig`で始まるSentence（算式の表示行）
  - 変数定義行・数式行（「Ｅ：…」「ｎ：…」等の記号定義の羅列、「ＥＭ＝αＭ×Ａ…」等のテキストで書かれた数式）。コンテナ全体のテキスト（`Sub`/`Sup`の添え字を展開して連結）が「短い記号列＋『：』または『＝』」で始まる形状で判定します。先行文脈に「（この|これらの）式において」の説明文が見つからないものは、判定根拠が形状のみのため実行ログに「要確認」として行番号付きで出力されます。`--include-vardef`指定でこの除外を無効化できます。
  - 「（」で始まるSentence（「（注）…」等の括弧書き。**`--exclude-paren`指定時のみ除外**。括弧書きを字下げ対象とするかは告示ごとの官報体裁に依存するため選択式です。Webアプリではサイドバーのチェックボックス「「（」で始まるSentenceは対象外にする」で切り替え）
- **検証との関係**: テキスト内容検証は補填**前**の中間ファイル（`intermediate_files/<元ファイル名>/*_before_fullwidth_space.xml`）に対して実行されます。
- **逆変換との整合**: 逆変換ページの「逆変換前に文頭全角スペースを除去する」チェックボックスを有効にすると、補填された全角スペースを除去してから逆変換します。除去時は旧仕様で変数定義行に補填されたスペースも除去できるよう、変数定義行の除外を適用しません。
- **単体テスト**: `scripts/test_data/unit_tests/postprocess_fullwidth_space/run_tests.py`

```bash
# CLIでの個別実行
python3 scripts/postprocess_fullwidth_space.py input.xml output.xml               # 補填
python3 scripts/postprocess_fullwidth_space.py input.xml output.xml --mode remove # 除去
python3 scripts/postprocess_fullwidth_space.py input.xml output.xml --include-list
python3 scripts/postprocess_fullwidth_space.py input.xml output.xml --include-vardef # 変数定義行・数式行も補填
python3 scripts/postprocess_fullwidth_space.py input.xml output.xml --exclude-paren  # 「（」始まりは対象外
```

### 列記Listの保護（オプション）

告示データ整備方針（パターン20D: スペースを使った列記）に基づき、列記を表すList要素を変換対象から除外するオプションを用意しています。Webアプリのサイドバーにあるチェックボックス「列記のList（Column構成）を変換せず保持する」で切り替えます（デフォルトOFF＝従来動作）。

- **判定基準**: Columnが2つ以上のListについて、1つ目のColumnがラベル（番号等）かつ2つ目が非ラベル（テキスト）の「番号+見出し」構成の場合のみ変換します。1つ目と2つ目の種別が同一（テキスト同士・ラベル同士）の場合は列記とみなし、変換せずListのまま残します。
- **Columnが1つのListは対象外**: 従来どおり変換されます。
- **後方互換**: OFFのままなら従来と完全に同じ動作です。従来データの変換結果が変わるため、告示データ整備方針に沿ったデータを処理する場合のみONにしてください。
- **対応スクリプト**: `convert_item_step0.py`、`convert_subitem1～10_step0.py`（`--preserve-enumeration`フラグ）
- **単体テスト**: `scripts/test_data/unit_tests/preserve_enumeration/run_tests.py`

```bash
# CLIでの個別実行
python3 scripts/convert_item_step0.py input.xml output.xml --preserve-enumeration
```

### LineBreak付きColumnを含むListの保護（オプション）

告示データ整備方針①（同一項番内の段落分けを`LineBreak="true"`のColumnで表現）に基づくデータを守るためのオプションです。Webアプリのサイドバーにあるチェックボックス「LineBreak付きColumnを含むListを変換せず保持する」で切り替えます（デフォルトOFF＝従来動作）。

- **背景**: 変換分岐のうち「ラベル+テキスト」（分岐1）と「Column1つ」（分岐1-0）はColumnラッパーを捨てて中のSentenceだけを抽出するため、Columnに付いた`LineBreak="true"`（改行表示の指示）が失われます。テキスト内容検証は文字だけを比較するため、この消失は検知されません。
- **動作**: ONの場合、`LineBreak="true"`のColumnを1つでも含むListは変換せずListのまま残します（Column数を問わず適用）。
- **後方互換**: OFFのままなら従来と完全に同じ動作です。
- **対応スクリプト**: `convert_item_step0.py`、`convert_subitem1～10_step0.py`（`--preserve-linebreak-list`フラグ。`--preserve-enumeration`と併用可）
- **単体テスト**: `scripts/test_data/unit_tests/preserve_linebreak_list/run_tests.py`

```bash
# CLIでの個別実行
python3 scripts/convert_item_step0.py input.xml output.xml --preserve-linebreak-list
# 列記保護と併用
python3 scripts/convert_item_step0.py input.xml output.xml --preserve-enumeration --preserve-linebreak-list
```

---

## 出力とファイル配置

```
output/
├── <入力名>-final.xml                 # 最終出力
└── intermediate_files/
    └── <入力名>/
        ├── <入力名>-<各ステップ>.xml        # 中間XML
        ├── <入力名>-parse_validation.txt    # 構文検証レポート
        └── <入力名>-validation_report.txt   # テキスト検証レポート
```

- 最終ファイルは常に `<入力名>-final.xml` として `<output_folder>` にコピーされます。
- 中間ファイルと検証レポートは出力フォルダ配下の `intermediate_files/` にまとめて保存されます。

---

## 開発・運用・保守

このプロジェクトの開発フローやコントリビューション方法については、[CONTRIBUTING.md](./CONTRIBUTING.md)を参照してください。

### 主な開発フロー

1. **機能ブランチを作成**: `git checkout -b feature/機能名`
2. **変更をコミット**: 適切なコミットメッセージでコミット
3. **プルリクエストを作成**: GitHubでPRを作成してレビュー依頼
4. **マージ**: レビュー承認後、mainブランチにマージ

詳細は[CONTRIBUTING.md](./CONTRIBUTING.md)を参照してください。

---

## トラブルシューティング

- `入力フォルダにXMLファイルが見つかりません`: `<input_folder>` 直下に `*.xml` があるか確認してください。
- `スクリプトが見つかりません`: `scripts/` 配下に全変換スクリプトがあるか確認してください。
- テキスト検証で `要確認` が出る: `intermediate_files/<入力名>/<入力名>-validation_report.txt` を確認し、欠落や差分をレビューしてください。

---

**最終更新**: 2025年12月
