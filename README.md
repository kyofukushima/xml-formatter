# XML マークアップ処理パイプライン使用ガイド

## 概要

このツールセットは、複数のPythonスクリプトを順序立てて実行し、XMLファイルをマークアップ（要素の整形・変換）するためのパイプラインです。入力フォルダ内のXMLファイルを処理し、整形されたXMLを出力フォルダに保存します。

---

## セットアップ

### 必要な環境
- **Python 3.7以上**
- **lxml** ライブラリ

### インストール手順

1. **lxml のインストール**

```bash
pip install lxml
```

2. **ファイル構成**

以下のファイルが同じディレクトリに存在することを確認してください：

```
project_directory/
├── run_pipeline.sh           # メインのシェルスクリプト
├── convert_article_focused.py
├── convert_paragraph_step1.py
├── convert_paragraph_step2.py
├── convert_paragraph_step3.py
├── convert_paragraph_step4.py
├── convert_item_step0.py
├── convert_item_step1.py
├── convert_subject_item.py
├── convert_subitem1_step0.py
├── convert_subitem1_step1.py
├── convert_subitem2_step0.py
├── convert_subitem2_step1.py
├── input/                    # 入力XMLファイルを格納するフォルダ
└── output/                   # 整形されたXMLが出力されるフォルダ
```

3. **実行権限の付与（初回のみ）**

```bash
chmod +x run_pipeline.sh
```

---

## 使用方法

### 基本的な実行

#### 方法1: 単一ファイルを直接指定

```bash
./run_pipeline.sh input/your_file.xml
```

#### 方法2: フォルダ内の全ファイルを処理

```bash
for file in input/*.xml; do
  ./run_pipeline.sh "$file" all
done
```

その後、出力ファイルを output フォルダに移動：

```bash
mv input/*-convert_*.xml output/
```

### 実行モード

#### Mode 1: `all` (デフォルト)

パイプラインを最初から最後まで連続実行します。

```bash
./run_pipeline.sh input/file.xml all
```

#### Mode 2: `step`

各ステップ実行後に一時停止します。確認しながら実行したい場合に使用：

```bash
./run_pipeline.sh input/file.xml step
```

---

## 処理フロー

パイプラインは以下の順序で処理を実行します：

| 順序 | スクリプト | 処理内容 |
|-----|---------|---------|
| 1 | `convert_article_focused.py` | Article 要素の処理 |
| 2 | `convert_paragraph_step1.py` | Paragraph 分割ステップ1 |
| 3 | `convert_paragraph_step2.py` | Paragraph 分割ステップ2 |
| 4 | `convert_paragraph_step3.py` | Paragraph 処理ステップ3 |
| 5 | `convert_paragraph_step4.py` | Paragraph 処理ステップ4 |
| 6 | `convert_item_step0.py` | Item 変換ステップ0 |
| 7 | `convert_item_step1.py` | Item 修正ステップ1 |
| 8 | `convert_subject_item.py` | Subject Item 変換 |
| 9 | `convert_subitem1_step0.py` | Subitem1 変換ステップ0 |
| 10 | `convert_subitem1_step1.py` | Subitem1 修正ステップ1 |
| 11 | `convert_subitem2_step0.py` | Subitem2 変換ステップ0 |
| 12 | `convert_subitem2_step1.py` | Subitem2 修正ステップ1 |
| 13 | `convert_subitem3_step0.py` | Subitem3 変換ステップ0 |
| 14 | `convert_subitem3_step1.py` | Subitem3 修正ステップ1 |
| 15 | `convert_subitem4_step0.py` | Subitem4 変換ステップ0 |
| 16 | `convert_subitem4_step1.py` | Subitem4 修正ステップ1 |
| 17 | `convert_subitem5_step0.py` | Subitem5 変換ステップ0 |
| 18 | `convert_subitem5_step1.py` | Subitem5 修正ステップ1 |

---

## 出力ファイル

### 出力ファイル名の規則

実行後、入力フォルダには中間ファイルが生成されます：

```
input/
├── your_file.xml                        # 元のファイル
├── your_file-convert_article_focused.xml
├── your_file-convert_paragraph_step1.xml
├── your_file-convert_paragraph_step2.xml
├── your_file-convert_paragraph_step3.xml
├── your_file-convert_paragraph_step4.xml
├── your_file-convert_item_step0.xml
├── your_file-convert_item_step1.xml
├── your_file-convert_subject_item.xml
├── your_file-convert_subitem1_step0.xml
├── your_file-convert_subitem1_step1.xml
├── your_file-convert_subitem2_step0.xml
├── your_file-convert_subitem2_step1.xml
├── your_file-convert_subitem3_step0.xml
├── your_file-convert_subitem3_step1.xml
├── your_file-convert_subitem4_step0.xml
├── your_file-convert_subitem4_step1.xml
├── your_file-convert_subitem5_step0.xml
└── your_file-convert_subitem5_step1.xml  # 最終出力
```

### 最終出力ファイルの取得

最終出力ファイル（`*-convert_subitem2_step1.xml`）をoutputフォルダに移動：

```bash
mv input/your_file-convert_subitem2_step1.xml output/your_file-final.xml
```

---

## スクリプトの修正内容

元のシェルスクリプトには以下の問題がありました。本ガイドで提供される修正版では、以下の改善を実施しています：

1. **フォルダ構造の完全なサポート**
   - 入力フォルダと出力フォルダを柔軟に指定可能

2. **エラーハンドリングの強化**
   - 入力ファイルが存在しない場合の適切なエラー処理
   - スクリプト実行失敗時の明確なエラーメッセージ

3. **中間ファイルの整理機能**
   - 最終出力のみを抽出し、出力フォルダに保存するオプション

---

## トラブルシューティング

### Q: `python3: command not found`

**A:** Pythonがインストールされていません。以下をインストールしてください：

- **Linux/Mac**: `brew install python3` または `apt-get install python3`
- **Windows**: [python.org](https://www.python.org) からダウンロード

### Q: `Permission denied: ./run_pipeline.sh`

**A:** スクリプトに実行権限がありません。以下を実行：

```bash
chmod +x run_pipeline.sh
```

### Q: `ModuleNotFoundError: No module named 'lxml'`

**A:** lxml ライブラリがインストールされていません：

```bash
pip install lxml
```

### Q: `Error: Input file not found`

**A:** 入力ファイルのパスが正しいか確認してください：

```bash
ls -la input/  # ファイル一覧を確認
```

### Q: スクリプトが途中で止まる

**A:** エラーメッセージを確認してください。XML形式が正しいか、またはスクリプトのロジックに合致しているか確認が必要です。

---

## 高度な使用例

### 複数ファイルの一括処理スクリプト

`batch_process.sh` という名前で以下を作成：

```bash
#!/bin/bash

INPUT_DIR="input"
OUTPUT_DIR="output"
SCRIPT_DIR="."

mkdir -p "$OUTPUT_DIR"

for file in "$INPUT_DIR"/*.xml; do
  if [ -f "$file" ]; then
    filename=$(basename "$file")
    echo "Processing $filename..."
    "$SCRIPT_DIR/run_pipeline.sh" "$file" all
    
    # 最終出力ファイルをoutputディレクトリに移動
    basename_no_ext="${filename%.xml}"
    final_file="$INPUT_DIR/${basename_no_ext}-convert_subitem2_step1.xml"
    
    if [ -f "$final_file" ]; then
      cp "$final_file" "$OUTPUT_DIR/${basename_no_ext}-final.xml"
      echo "Saved to $OUTPUT_DIR/${basename_no_ext}-final.xml"
    fi
  fi
done

echo "All files processed!"
```

実行：

```bash
chmod +x batch_process.sh
./batch_process.sh
```

---

## サポート

質問や問題が発生した場合は、以下の情報を確認してください：

- Python バージョン: `python3 --version`
- lxml バージョン: `pip list | grep lxml`
- XMLファイルの形式が正しいこと

---

## ライセンス

このツールセットの利用条件は、提供元の指定に従ってください。

---

**最終更新**: 2025年11月11日
