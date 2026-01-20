# 逆変換スクリプトについて

このプロジェクトには、XML変換の逆方向（Paragraph~subitem → List）を行うスクリプト群も用意されています。

## 逆変換スクリプトの場所

逆変換スクリプトは、正変換スクリプトと混同を避けるため、別フォルダ `scripts/reverse/` に配置されています。

## 逆変換スクリプト一覧

- `reverse/reverse_xml_converter.py` - 逆変換機能の共通モジュール
- `reverse/reverse_convert_item.py` - Paragraph内のItem要素をList要素に変換
- `reverse/reverse_convert_subitem1.py` - Item内のSubitem1要素をList要素に変換
- `reverse/reverse_convert_subitem2.py` - Subitem1内のSubitem2要素をList要素に変換
- `reverse/run_reverse_pipeline.sh` - 逆変換パイプライン実行スクリプト

## 逆変換仕様

- **タイトル要素（ItemTitle等）がある場合** → 2カラムのList要素（Column1: タイトル, Column2: 本文）
- **タイトル要素がない場合** → ColumnなしのList要素
- **List要素以外の要素** → 変更なし

## 使用方法

```bash
# 逆変換パイプライン実行
cd scripts/reverse
./run_reverse_pipeline.sh input_folder output_folder

# 個別スクリプト実行
python3 reverse_convert_item.py input.xml output.xml
```

詳細は `scripts/reverse/README.md` を参照してください。




