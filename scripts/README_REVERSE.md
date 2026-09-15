# 逆変換スクリプトについて

このプロジェクトには、XML変換の逆方向（Item〜Subitem10 → List）を行うスクリプト群も用意されています。

## 逆変換スクリプトの場所

逆変換スクリプトの**現行版はプロジェクト直下の `reverse_app/` フォルダ**にあります。Webアプリの「逆変換」ページは `reverse_app/` のスクリプトを `utils/reverse_pipeline.py` 経由で実行します。

`scripts/reverse/` にも同名のスクリプトがありますが、これは旧配置のコピーで、親要素の個別選択など最近の機能は反映されていません。Webアプリからも参照されないため、仕様変更やテストは `reverse_app/` に対して行ってください。

## 逆変換スクリプト一覧（reverse_app/）

- `reverse_xml_converter.py` - 逆変換機能の共通モジュール（CLIオプションの定義を含む）
- `reverse_convert_item.py` - Paragraph/Class/AppdxTable/TableColumn/Remarks/NewProvision内のItem要素をList要素に変換
- `reverse_convert_subitem1.py` 〜 `reverse_convert_subitem10.py` - 各階層のSubitem要素をList要素に変換
- `run_reverse_pipeline.sh` - 逆変換パイプライン実行スクリプト（内側の階層から外側へ順次実行）
- `verify_reverse_order.py` - 逆変換前後でテキストの登場順が保持されているかを検証

## 逆変換仕様（概要）

- **タイトル要素（ItemTitle等）がある場合** → 2カラムのList要素（Column1: タイトル, Column2: 本文）
- **タイトル要素がない場合** → ColumnなしのList要素
- **List要素以外の要素（TableStruct等）** → 変更なし
- **Item逆変換の親要素** → デフォルトですべて対象。`--no-include-appdxtable` 等で個別に除外可能
- **文頭全角スペース** → 正変換で補填した場合は、`scripts/postprocess_fullwidth_space.py --mode remove` で除去してから逆変換する（Webアプリではチェックボックスで指定）

## 使用方法

```bash
# 逆変換パイプライン実行
cd reverse_app
./run_reverse_pipeline.sh input_folder output_folder

# 個別スクリプト実行
python3 reverse_convert_item.py input.xml output.xml
python3 reverse_convert_item.py input.xml output.xml --no-include-appdxtable

# 順序検証
python3 verify_reverse_order.py 元のファイル.xml 逆変換後.xml
```

詳細は `reverse_app/README.md` を参照してください。
