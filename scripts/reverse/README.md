# 逆変換スクリプト

このフォルダには、Paragraph~subitem要素をList要素に逆変換するスクリプト群が含まれています。

## スクリプト一覧

- `reverse_xml_converter.py` - 逆変換機能の共通モジュール
- `reverse_convert_item.py` - Paragraph内のItem要素をList要素に変換
- `reverse_convert_subitem1.py` - Item内のSubitem1要素をList要素に変換
- `reverse_convert_subitem2.py` - Subitem1内のSubitem2要素をList要素に変換
- `reverse_convert_subitem3.py` - Subitem2内のSubitem3要素をList要素に変換
- `reverse_convert_subitem4.py` - Subitem3内のSubitem4要素をList要素に変換
- `reverse_convert_subitem5.py` - Subitem4内のSubitem5要素をList要素に変換
- `reverse_convert_subitem6.py` - Subitem5内のSubitem6要素をList要素に変換
- `reverse_convert_subitem7.py` - Subitem6内のSubitem7要素をList要素に変換
- `reverse_convert_subitem8.py` - Subitem7内のSubitem8要素をList要素に変換
- `reverse_convert_subitem9.py` - Subitem8内のSubitem9要素をList要素に変換
- `reverse_convert_subitem10.py` - Subitem9内のSubitem10要素をList要素に変換
- `run_reverse_pipeline.sh` - 逆変換パイプライン実行スクリプト

## 変換仕様

- **タイトル要素（ItemTitle/Subitem1Title/.../Subitem10Title）がある場合**
  - 2カラムのList要素に変換
  - Column1: タイトル内容
  - Column2: 本文内容（ItemSentence/Subitem1Sentence/.../Subitem10Sentence）

- **タイトル要素がない場合**
  - ColumnのないList要素に変換
  - ListSentence内のSentenceに本文内容

- **List要素以外の要素** → 変更されずにスルー

## 使用方法

### 個別スクリプト実行

```bash
# Item逆変換
python3 reverse_convert_item.py input.xml output.xml

# Subitem1逆変換
python3 reverse_convert_subitem1.py input.xml output.xml

# Subitem2逆変換
python3 reverse_convert_subitem2.py input.xml output.xml

# Subitem10逆変換
python3 reverse_convert_subitem10.py input.xml output.xml
```

### パイプライン実行（全階層逆変換）

```bash
# 連続実行
./run_reverse_pipeline.sh input_folder output_folder

# ステップ実行（各ステップで確認）
./run_reverse_pipeline.sh input_folder output_folder step
```

## 実行順序

逆変換は以下の順序で実行してください（内側から外側へ）：
1. `reverse_convert_subitem10.py` - Subitem10 → List
2. `reverse_convert_subitem9.py` - Subitem9 → List
3. `reverse_convert_subitem8.py` - Subitem8 → List
4. `reverse_convert_subitem7.py` - Subitem7 → List
5. `reverse_convert_subitem6.py` - Subitem6 → List
6. `reverse_convert_subitem5.py` - Subitem5 → List
7. `reverse_convert_subitem4.py` - Subitem4 → List
8. `reverse_convert_subitem3.py` - Subitem3 → List
9. `reverse_convert_subitem2.py` - Subitem2 → List
10. `reverse_convert_subitem1.py` - Subitem1 → List
11. `reverse_convert_item.py` - Item → List

パイプラインスクリプトはこの順序で自動実行します。

## 注意事項

- 逆変換スクリプトは正変換スクリプト（`../`）とは別のフォルダに配置されています
- 既存のList要素は変更されません
- XML構造の完全性を保ちつつ逆変換を行います
