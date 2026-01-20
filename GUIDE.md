# XML構造変換スクリプト ガイドブック

## 目次

1. [プロジェクト概要](#プロジェクト概要)
2. [セットアップ](#セットアップ)
3. [基本的な使い方](#基本的な使い方)
4. [処理フローと各スクリプトの役割](#処理フローと各スクリプトの役割)
5. [検証機能](#検証機能)
6. [出力ファイルの構成](#出力ファイルの構成)
7. [トラブルシューティング](#トラブルシューティング)
8. [高度な使い方](#高度な使い方)

---

## プロジェクト概要

このプロジェクトは、教育課程関連のXMLファイルを構造化するためのパイプライン処理システムです。複数の変換スクリプトを順次実行することで、XMLファイル内の階層構造（Article、Paragraph、Item、Subitem1〜Subitem10）を自動的に整形します。

### 主な機能

- **階層構造の自動変換**: List要素を適切な階層要素（Item、Subitem1〜10）に変換
- **ラベル認識**: 括弧付き数字、カタカナ、アルファベット、学年・科目ラベルなどを自動認識
- **構造の正規化**: 段落番号の補完、Article要素の分割など
- **検証機能**: XML構文チェックとテキスト内容の整合性検証

---

## セットアップ

### 必要な環境

- **Python**: 3.7以上
- **ライブラリ**: lxml

### インストール手順

```bash
# 1. Pythonのバージョン確認
python3 --version

# 2. lxmlライブラリのインストール
pip install lxml

# 3. スクリプトに実行権限を付与
chmod +x scripts/run_pipeline.sh

# 4. 入力・出力ディレクトリの作成（任意）
mkdir -p input output
```

---

## 基本的な使い方

### パイプラインの実行

最も簡単な使い方は、パイプラインスクリプトを使用することです。

```bash
./scripts/run_pipeline.sh <入力フォルダ> <出力フォルダ> [モード]
```

#### 引数の説明

- **入力フォルダ**: 処理対象のXMLファイルを格納するフォルダ（配下の`*.xml`をすべて処理）
- **出力フォルダ**: 処理結果を保存するフォルダ
- **モード**（オプション）:
  - `all`（デフォルト）: すべてのステップを連続実行
  - `step`: 各ステップ終了後に一時停止して確認可能

#### 実行例

```bash
# 連続実行（推奨）
./scripts/run_pipeline.sh ./input ./output

# ステップごとに確認しながら実行
./scripts/run_pipeline.sh ./input ./output step
```

### 個別スクリプトの実行

特定の変換ステップのみを実行したい場合は、個別のPythonスクリプトを直接実行できます。

```bash
python3 scripts/preprocess_non_first_sentence_to_list.py <入力ファイル> <出力ファイル>
python3 scripts/convert_article_focused.py <入力ファイル> <出力ファイル>
# ... など
```

---

## 処理フローと各スクリプトの役割

パイプラインは以下の順序で15個の変換スクリプトを実行します。

### 処理順序と各スクリプトの説明

| 順序 | スクリプト名 | 主な処理内容 |
|------|------------|------------|
| 1 | `preprocess_non_first_sentence_to_list.py` | **前処理**: 2個目以降のSentence要素内のラベル（「（１）　本文」形式）を検出し、List要素に変換 |
| 2 | `convert_article_focused.py` | **Article要素の分割**: 「第１」「第２」などの見出しを検出し、1つのArticleを複数に分割 |
| 3 | `convert_paragraph_step3.py` | **Paragraph処理（step3）**: Paragraph要素内の構造を調整 |
| 4 | `convert_paragraph_step4.py` | **Paragraph処理（step4）**: Paragraph要素内の構造を調整 |
| 5 | `convert_item_step0.py` | **Item変換（step0）**: Paragraph内のList要素をItem要素に変換 |
| 6 | `convert_subitem1_step0.py` | **Subitem1変換（step0）**: Item内のList要素をSubitem1要素に変換 |
| 7 | `convert_subitem2_step0.py` | **Subitem2変換（step0）**: Subitem1内のList要素をSubitem2要素に変換 |
| 8 | `convert_subitem3_step0.py` | **Subitem3変換（step0）**: Subitem2内のList要素をSubitem3要素に変換 |
| 9 | `convert_subitem4_step0.py` | **Subitem4変換（step0）**: Subitem3内のList要素をSubitem4要素に変換 |
| 10 | `convert_subitem5_step0.py` | **Subitem5変換（step0）**: Subitem4内のList要素をSubitem5要素に変換 |
| 11 | `convert_subitem6_step0.py` | **Subitem6変換（step0）**: Subitem5内のList要素をSubitem6要素に変換 |
| 12 | `convert_subitem7_step0.py` | **Subitem7変換（step0）**: Subitem6内のList要素をSubitem7要素に変換 |
| 13 | `convert_subitem8_step0.py` | **Subitem8変換（step0）**: Subitem7内のList要素をSubitem8要素に変換 |
| 14 | `convert_subitem9_step0.py` | **Subitem9変換（step0）**: Subitem8内のList要素をSubitem9要素に変換 |
| 15 | `convert_subitem10_step0.py` | **Subitem10変換（step0）**: Subitem9内のList要素をSubitem10要素に変換（最終） |

### 各ステップの詳細説明

#### 1. 前処理（preprocess_non_first_sentence_to_list.py）

**目的**: Sentence要素内の「ラベル＋全角スペース＋本文」形式を検出し、List要素に変換します。

**処理内容**:
- Paragraph、Item、Subitem1〜5要素内の2個目以降のSentence要素を対象
- 「（１）　本文内容」のような形式を検出
- Columnが2つのList要素に変換（1列目: ラベル、2列目: 本文）

**例**:
```xml
<!-- 変換前 -->
<ParagraphSentence>
  <Sentence Num="1">（１）　最初の内容</Sentence>
</ParagraphSentence>
<ParagraphSentence>
  <Sentence Num="1">（２）　2個目の内容</Sentence>
</ParagraphSentence>

<!-- 変換後 -->
<ParagraphSentence>
  <Sentence Num="1">（１）　最初の内容</Sentence>
</ParagraphSentence>
<List>
  <ListSentence>
    <Column Num="1"><Sentence Num="1">（２）</Sentence></Column>
    <Column Num="2"><Sentence Num="1">2個目の内容</Sentence></Column>
  </ListSentence>
</List>
```

#### 2. Article要素の分割（convert_article_focused.py）

**目的**: 1つのArticle要素に複数の条が含まれている場合、見出しを検出して分割します。

**処理内容**:
- ArticleTitleが「第１」「第２」などの形式を検出
- List要素内に「第２」「第３」などの見出しが出現したら、その位置で分割
- 分割後、各Articleに適切な番号を付与

**例**:
```xml
<!-- 変換前 -->
<Article Num="999999999">
  <ArticleTitle>第１</ArticleTitle>
  <Paragraph>...</Paragraph>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>第２</Sentence></Column>
      <Column Num="2"><Sentence>第2条の内容</Sentence></Column>
    </ListSentence>
  </List>
</Article>

<!-- 変換後 -->
<Article Num="1">
  <ArticleTitle>第１</ArticleTitle>
  <Paragraph>...</Paragraph>
</Article>
<Article Num="2">
  <ArticleTitle>第２</ArticleTitle>
  <Paragraph>...</Paragraph>
</Article>
```

#### 3-4. Paragraph処理（convert_paragraph_step3.py, convert_paragraph_step4.py）

**目的**: Paragraph要素内の構造を調整し、後続の処理に備えます。

**処理内容**:
- ParagraphNumの補完
- Paragraph内のList要素の配置を調整

#### 5. Item変換（convert_item_step0.py）

**目的**: Paragraph内のList要素をItem要素に変換します。

**処理内容**:
- Columnが2つ以上で、1列目がラベル（「（１）」「（ア）」など）の場合、Item要素に変換
- ColumnなしList（学年・科目名など）も適切に処理
- 同じ階層のラベルは同じItemにまとめ、異なるラベルは分割

**認識するラベル例**:
- 括弧付き数字: `（１）`, `（一）`, `(1)`
- 括弧付きカタカナ: `（ア）`, `（イ）`
- 括弧付きアルファベット: `（a）`, `（A）`
- 学年ラベル: `〔第１学年〕`, `〔第１学年及び第２学年〕`
- 科目名ラベル: `〔医療と社会〕`

#### 6-15. Subitem変換（convert_subitem1_step0.py 〜 convert_subitem10_step0.py）

**目的**: 各階層のList要素を下位のSubitem要素に変換します。

**処理内容**:
- Item内のList → Subitem1
- Subitem1内のList → Subitem2
- Subitem2内のList → Subitem3
- Subitem3内のList → Subitem4
- Subitem4内のList → Subitem5
- Subitem5内のList → Subitem6
- Subitem6内のList → Subitem7
- Subitem7内のList → Subitem8
- Subitem8内のList → Subitem9
- Subitem9内のList → Subitem10（最終階層）

**階層判定のルール**:
- 同じ種類のラベル（例: すべて「（ア）」）は同じSubitemにまとめる
- 異なる種類のラベル（例: 「（ア）」と「（イ）」）は分割する
- 学年・科目名ラベルは特殊処理
- 各階層でラベルパターンに応じて適切に分割・入れ子化

---

## 検証機能

パイプラインは処理前後で2種類の検証を自動実行します。

### 1. 構文検証（validate_xml.py）

**実行タイミング**: 各XMLファイルの処理開始前

**処理内容**:
- XMLファイルが正しい形式（well-formed）かチェック
- パースエラーがある場合は処理をスキップ

**出力ファイル**: `output/intermediate_files/<ファイル名>/<ファイル名>-parse_validation.txt`

**出力例**:
```
SUCCESS: XML file 'input.xml' is well-formed.
```

### 2. テキスト内容検証（compare_xml_text_content.py）

**実行タイミング**: パイプライン処理完了後

**処理内容**:
- 元のXMLファイルと最終出力XMLファイルのテキスト内容を比較
- テキストの欠落がないか確認（構造変更は無視）

**出力ファイル**: `output/intermediate_files/<ファイル名>/<ファイル名>-validation_report.txt`

**出力例**:
```
✅ Success: All text content from original file is present in final file.
```

---

## 出力ファイルの構成

パイプライン実行後、以下のような構造でファイルが出力されます。

```
output/
├── <入力ファイル名>-final.xml          # 最終出力XMLファイル
└── intermediate_files/
    └── <入力ファイル名>/
        ├── <入力ファイル名>-preprocess_non_first_sentence_to_list.xml
        ├── <入力ファイル名>-convert_article_focused.xml
        ├── <入力ファイル名>-convert_paragraph_step3.xml
        ├── <入力ファイル名>-convert_paragraph_step4.xml
        ├── <入力ファイル名>-convert_item_step0.xml
        ├── <入力ファイル名>-convert_subitem1_step0.xml
        ├── ...（各ステップの中間ファイル）
        ├── <入力ファイル名>-convert_subitem10_step0.xml
        ├── <入力ファイル名>-parse_validation.txt        # 構文検証レポート
        └── <入力ファイル名>-validation_report.txt       # テキスト検証レポート
```

### ファイルの説明

- **`<入力ファイル名>-final.xml`**: すべての変換処理が完了した最終的なXMLファイル
- **中間ファイル**: 各変換ステップの出力結果（デバッグや途中確認に使用）
- **検証レポート**: 処理結果の検証情報

---

## トラブルシューティング

### よくあるエラーと解決方法

#### 1. `python3: command not found`

**原因**: Pythonがインストールされていない、またはパスが通っていない

**解決方法**:
```bash
# Pythonのインストール確認
which python3

# インストールされていない場合（macOS）
brew install python3

# インストールされていない場合（Linux）
sudo apt-get install python3
```

#### 2. `ModuleNotFoundError: No module named 'lxml'`

**原因**: lxmlライブラリがインストールされていない

**解決方法**:
```bash
pip install lxml
# または
pip3 install lxml
```

#### 3. `Permission denied: ./run_pipeline.sh`

**原因**: スクリプトに実行権限がない

**解決方法**:
```bash
chmod +x scripts/run_pipeline.sh
```

#### 4. `入力フォルダにXMLファイルが見つかりません`

**原因**: 入力フォルダに`.xml`ファイルがない

**解決方法**:
```bash
# ファイルの存在確認
ls -la input/*.xml

# ファイルを配置
cp your_file.xml input/
```

#### 5. パース検証でエラーが検出された

**原因**: XMLファイルの構文エラー

**解決方法**:
1. 検証レポートを確認: `output/intermediate_files/<ファイル名>/<ファイル名>-parse_validation.txt`
2. XMLファイルの構文を修正
3. 再度パイプラインを実行

#### 6. テキスト検証で欠落が検出された

**原因**: 変換処理中にテキストが失われた可能性

**解決方法**:
1. 検証レポートを確認: `output/intermediate_files/<ファイル名>/<ファイル名>-validation_report.txt`
2. 欠落したテキストを確認
3. 必要に応じて変換ロジックを確認・修正

---

## 高度な使い方

### カスタムディレクトリでの実行

```bash
./scripts/run_pipeline.sh /path/to/input /path/to/output all
```

### デバッグモードでの実行

各ステップの詳細な出力を確認したい場合:

```bash
# シェルのデバッグモードで実行
bash -x scripts/run_pipeline.sh ./input ./output all
```

### 個別スクリプトのテスト

特定の変換スクリプトのみをテストしたい場合:

```bash
# 例: Article変換のみ実行
python3 scripts/convert_article_focused.py input/test.xml /tmp/output.xml

# エラー出力も確認
python3 scripts/convert_article_focused.py input/test.xml /tmp/output.xml 2>&1
```

### バッチ処理スクリプトの作成

複数のXMLファイルを順次処理するスクリプト例:

```bash
#!/bin/bash

INPUT_DIR="./input"
OUTPUT_DIR="./output"
SCRIPT_DIR="./scripts"

mkdir -p "$OUTPUT_DIR"

for file in "$INPUT_DIR"/*.xml; do
  if [ -f "$file" ]; then
    filename=$(basename "$file")
    echo "処理中: $filename"
    "$SCRIPT_DIR/run_pipeline.sh" "$INPUT_DIR" "$OUTPUT_DIR" all
  fi
done

echo "すべてのファイルの処理が完了しました"
```

### 設定ファイルのカスタマイズ

ラベルの認識ルールは `scripts/config/label_config.json` で設定できます。詳細は `scripts/utils/README.md` を参照してください。

---

## 補足情報

### 関連ドキュメント

- **README.md**: 基本的な使用方法
- **QUICKSTART.md**: 5分で始めるクイックスタートガイド
- **処理ロジック.md**: 処理の詳細なロジック説明
- **docs/**: 各種技術ドキュメント

### サポート

問題が解決しない場合は、以下の情報を収集してサポートまでご連絡ください:

1. **エラーメッセージ全文**
2. **環境情報**:
   ```bash
   python3 --version
   pip list | grep lxml
   uname -a
   ```
3. **使用コマンド**
4. **入力XMLファイルのサンプル**（プライバシーに配慮）

---

**最終更新**: 2025年12月








