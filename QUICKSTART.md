# クイックスタートガイド

## 5分で開始できるセットアップ

### ステップ1: 環境確認

```bash
# Python バージョン確認
python3 --version

# lxml ライブラリのインストール（必要な場合）
pip install lxml
```

### ステップ2: ディレクトリ構造の準備

```bash
# プロジェクトディレクトリを作成
mkdir xml_pipeline_project
cd xml_pipeline_project

# 必要なフォルダを作成
mkdir input
mkdir output

# すべてのスクリプトをこのディレクトリに配置
# ├── run_pipeline_fixed.sh
# ├── convert_*.py (すべてのスクリプト)
# ├── input/
# └── output/
```

### ステップ3: 入力ファイルを配置

処理対象のXMLファイルを `input/` フォルダに配置します。

```bash
cp your_file.xml input/
ls input/  # 確認
```

### ステップ4: パイプラインスクリプトに実行権限を付与

```bash
chmod +x run_pipeline_fixed.sh
```

### ステップ5: パイプラインを実行

```bash
# 基本的な実行
./run_pipeline_fixed.sh ./input ./output

# または明示的にモードを指定
./run_pipeline_fixed.sh ./input ./output all
```

### ステップ6: 結果を確認

```bash
ls -lh output/
cat output/your_file-final.xml
```

---

## よくある質問と回答

### Q1: 複数のXMLファイルを一度に処理できますか？

はい。`input/` フォルダ内のすべてのXMLファイルが自動的に処理されます。

```bash
# input/ フォルダに複数のXMLファイルを配置
cp file1.xml input/
cp file2.xml input/
cp file3.xml input/

# すべて一度に処理
./run_pipeline_fixed.sh ./input ./output all

# 結果は output/ フォルダに保存されます
ls output/
```

### Q2: ステップバイステップで確認しながら実行したいのですが？

`step` モードを使用してください。各ステップ実行後に一時停止します。

```bash
./run_pipeline_fixed.sh ./input ./output step
```

### Q3: 処理が失敗した場合はどうすればよいですか？

エラーメッセージを確認してください。以下の確認項目があります：

1. **XMLファイル形式が正しいか**
   ```bash
   xmllint --noout input/your_file.xml
   ```

2. **Pythonスクリプトがすべて存在するか**
   ```bash
   ls -la *.py
   ```

3. **lxml がインストールされているか**
   ```bash
   python3 -c "import lxml; print(lxml.__version__)"
   ```

### Q4: 元のファイルは上書きされていませんか？

いいえ。元のXMLファイルは保護されており、処理結果は `output/` フォルダに別ファイルとして保存されます。

### Q5: 中間ファイルを保存したいのですが？

デフォルトでは中間ファイルは一時ディレクトリに保存され、最終結果のみ出力されます。中間ファイルも保存したい場合は、以下のようにスクリプトを修正できます：

```bash
# スクリプトの "temp_dir=$(mktemp -d)" の部分を以下に変更：
# temp_dir="$OUTPUT_FOLDER/_intermediate_${filename_no_ext}"
# mkdir -p "$temp_dir"
```

---

## トラブルシューティング表

| 問題 | 原因 | 解決方法 |
|-----|------|---------|
| `No such file or directory` | スクリプトが見つからない | スクリプトが全てディレクトリに存在するか確認 |
| `Permission denied` | 実行権限がない | `chmod +x run_pipeline_fixed.sh` を実行 |
| `ModuleNotFoundError: lxml` | lxml がインストールされていない | `pip install lxml` を実行 |
| `Input folder not found` | 入力フォルダが存在しない | `mkdir input` でフォルダを作成 |
| `No XML files found` | XMLファイルがない | `cp your_file.xml input/` でファイルを配置 |
| Python スクリプト実行エラー | XMLファイル形式が異なる | XMLファイルが法令XML形式であるか確認 |

---

## パイプライン処理の詳細

### 各ステップの役割

```
原始XML
   ↓
[1] convert_article_focused.py
   記事（Article）要素の解析と整形
   ↓
[2-5] convert_paragraph_step*.py
   段落（Paragraph）の分割と整形（4ステップ）
   ↓
[6-7] convert_item_step*.py
   項目（Item）への変換と修正（2ステップ）
   ↓
[8] convert_subject_item.py
   主題項目（Subject Item）への変換
   ↓
[9-10] convert_subitem1_step*.py
   副項目1（Subitem1）への変換と修正（2ステップ）
   ↓
[11-12] convert_subitem2_step*.py
   副項目2（Subitem2）への変換と修正（2ステップ）
   ↓
整形済みXML（最終出力）
```

### 出力ファイル名の規則

入力: `law_article.xml`
出力: `law_article-final.xml`

---

## 高度な使用例

### カスタムディレクトリでの実行

```bash
./run_pipeline_fixed.sh /path/to/input /path/to/output all
```

### シェルスクリプトでの自動処理

`process_all.sh` を作成：

```bash
#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="./input"
OUTPUT_DIR="./output"

# 入力ディレクトリが存在しなければ作成
mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"

# パイプラインを実行
"$SCRIPT_DIR/run_pipeline_fixed.sh" "$INPUT_DIR" "$OUTPUT_DIR" all

# ログファイルに結果を記録（オプション）
echo "処理完了: $(date)" >> process.log
```

実行：

```bash
chmod +x process_all.sh
./process_all.sh
```

---

## パフォーマンス最適化

### 大量ファイルの処理

大量のXMLファイルを処理する場合、メモリ効率を考慮してください：

```bash
# 同時実行数を制限する場合
for file in input/*.xml; do
  ./run_pipeline_fixed.sh ./input ./output all &
  # 最大3プロセスまで同時実行
  if [ $(jobs -r -p | wc -l) -ge 3 ]; then
    wait -n
  fi
done
wait
```

---

## デバッグ情報

### ログ出力付き実行

Bashスクリプトのデバッグモードを有効にして実行：

```bash
bash -x run_pipeline_fixed.sh ./input ./output all
```

### Pythonスクリプトの詳細出力

各Pythonスクリプトのエラー出力を確認：

```bash
python3 convert_article_focused.py input/your_file.xml output/test.xml 2>&1
```

---

## 技術サポート

問題が解決しない場合は、以下の情報を収集してサポートまでご連絡ください：

1. **エラーメッセージ全文**
2. **環境情報**
   ```bash
   python3 --version
   pip list | grep lxml
   uname -a  # Linux/Mac
   ```
3. **使用コマンド**
4. **入力XMLファイルのサンプル**（プライバシーに配慮）

---

**最終更新**: 2025年11月11日
