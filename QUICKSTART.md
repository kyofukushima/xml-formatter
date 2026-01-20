# クイックスタートガイド

## 5分で開始できるセットアップ

### ステップ1: 環境確認

```bash
# Python バージョン確認
python3 --version

# lxml が未インストールなら追加
pip install lxml
```

### ステップ2: ディレクトリ準備

```bash
mkdir -p input output
chmod +x scripts/run_pipeline.sh
```

### ステップ3: 入力ファイルを配置

`input/` 配下に処理したい XML を置きます（複数可）。

```bash
cp your_file.xml input/
ls input/
```

### ステップ4: パイプラインを実行

```bash
# 連続実行（デフォルト）
./scripts/run_pipeline.sh ./input ./output

# ステップごとに確認
./scripts/run_pipeline.sh ./input ./output step
```

### ステップ5: 結果を確認

```bash
ls -lh output/
cat output/your_file-final.xml
```

---

## よくある質問と回答

### Q1: 複数のXMLを一度に処理できますか？

はい。`input/` 直下の `*.xml` をすべて順次処理します。

### Q2: ステップごとに確認したい

`step` モードを指定してください。各ステップ終了後に一時停止します。

```bash
./scripts/run_pipeline.sh ./input ./output step
```

### Q3: 処理が失敗した場合は？

1. XML構文チェック  
   ```bash
   xmllint --noout input/your_file.xml
   ```
2. 変換スクリプトの存在確認  
   ```bash
   ls scripts/*.py
   ```
3. lxml の確認  
   ```bash
   python3 -c "import lxml; print(lxml.__version__)"
   ```
4. 検証レポート確認  
   `output/intermediate_files/<入力名>/<入力名>-parse_validation.txt`  
   `output/intermediate_files/<入力名>/<入力名>-validation_report.txt`

### Q4: 元ファイルは上書きされますか？

されません。最終結果は `output/<入力名>-final.xml` に保存され、元のXMLはそのまま残ります。

---

## トラブルシューティング表

| 問題 | 原因 | 解決方法 |
|-----|------|---------|
| `No such file or directory` | スクリプトが見つからない | `scripts/` に全変換スクリプトがあるか確認 |
| `Permission denied` | 実行権限がない | `chmod +x scripts/run_pipeline.sh` |
| `ModuleNotFoundError: lxml` | lxml 未インストール | `pip install lxml` |
| `Input folder not found` | 入力フォルダなし | `mkdir input` |
| `No XML files found` | XMLが無い | `cp your_file.xml input/` |
| パース検証失敗 | XML構文エラー | `...-parse_validation.txt` を確認 |
| テキスト検証差分 | 内容差異 | `...-validation_report.txt` を確認 |

---

## パイプライン処理の概要

実行順（`scripts/run_pipeline.sh` が呼び出すスクリプト）:

1. `preprocess_non_first_sentence_to_list.py`
2. `convert_article_focused.py`
3. `convert_paragraph_step3.py`
4. `convert_paragraph_step4.py`
5. `convert_item_step0.py`
6. `convert_subitem1_step0.py`
7. `convert_subitem2_step0.py`
8. `convert_subitem3_step0.py`
9. `convert_subitem4_step0.py`
10. `convert_subitem5_step0.py`
11. `convert_subitem6_step0.py`
12. `convert_subitem7_step0.py`
13. `convert_subitem8_step0.py`
14. `convert_subitem9_step0.py`
15. `convert_subitem10_step0.py`

検証:
- 構文検証: `validate_xml.py`
- テキスト内容検証: `compare_xml_text_content.py`

出力:
- 最終ファイル: `output/<入力名>-final.xml`
- 中間・レポート: `output/intermediate_files/<入力名>/...`

---

## 高度な使用例

### カスタムディレクトリでの実行

```bash
./scripts/run_pipeline.sh /path/to/input /path/to/output all
```

### シェルスクリプトでの一括処理例

```bash
#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="./input"
OUTPUT_DIR="./output"

mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"
"$SCRIPT_DIR/run_pipeline.sh" "$INPUT_DIR" "$OUTPUT_DIR" all
echo "処理完了: $(date)" >> process.log
```

---

## パフォーマンスのヒント

- 大量ファイル時は同時実行数を絞るか、ファイルを分割して順次実行してください。
- 中間ファイルは `output/intermediate_files/` に集約されるため、ディスク残量を確認してください。

---

## デバッグ情報

### ログ出力付き実行

```bash
bash -x scripts/run_pipeline.sh ./input ./output all
```

### 個別スクリプトの確認

```bash
python3 scripts/convert_article_focused.py input/your_file.xml /tmp/out.xml 2>&1
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

**最終更新**: 2025年12月
