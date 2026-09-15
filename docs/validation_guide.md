# XML検証ガイド

このドキュメントでは、XMLファイルが整形式（well-formed）であるか、スキーマ定義（XSD）に準拠しているか、および変換前後で内容が保たれているかを確認するための検証コマンドについて説明します。

---

## 1. XMLの整形式チェック

XMLファイルが構文的に正しいか（タグが正しく閉じられているかなど）を検証します。このプロジェクトでは、そのためのPythonスクリプトが用意されています。

### コマンド

```bash
python3 scripts/validate_xml.py [検証したいXMLファイル]
```

### 実行例

`input`フォルダ内の特定のXMLファイルを検証する場合：

```bash
python3 scripts/validate_xml.py input/H29null[2400]062_H29null[2400]062_H300401_1.xml
```

### 出力

-   **成功した場合**:
    ```
    SUCCESS: XML file '[ファイルパス]' is well-formed.
    ```

-   **失敗した場合**:
    エラー内容、行番号、列番号が出力されます。
    ```
    ERROR: XML parsing failed for file '[ファイルパス]'.
    Error message: mismatched tag: line 890, column 16
    ```

---

## 2. XMLスキーマ（XSD）検証

XMLファイルが、指定されたスキーマ定義（`.xsd`ファイル）のルール（要素の順序、属性、データ型など）に従っているかを検証します。これには`xmllint`コマンドラインツールを使用します。

### コマンド

```bash
xmllint --noout --schema [スキーマファイル.xsd] [検証したいXMLファイル.xml]
```

-   `--noout`: 検証エラーのみを表示し、XMLファイルの内容は出力しません。
-   `--schema`: 使用するスキーマファイルを指定します。

### 実行例

このプロジェクトの`kokuji20250320_asukoe.xsd`スキーマを使用してXMLファイルを検証する場合：

```bash
xmllint --noout --schema schema/kokuji20250320_asukoe.xsd input/H29null[2400]062_H29null[2400]062_H300401_1.xml
```

### 出力

-   **成功した場合**:
    コマンドは何もメッセージを出力せずに終了します。

-   **失敗した場合**:
    スキーマに違反している箇所の詳細なエラーメッセージが出力されます。
    ```
    [ファイルパス]:[行番号]: element [要素名]: Schemas validity error : Element '[要素名]': This element is not expected.
    ```

---

### 補足: validate_kokuji_schema.py

告示XSD（`schema/kokuji*_asukoe.xsd`）は `LawBody` に `xs:any` を含むため、libxml2（`xmllint` および lxml）では UPA 検査に引っかかりスキーマを構築できないことがあります。その場合は、検証時のみ `xs:any` を `SupplProvision` 参照に差し替えて読み込む専用スクリプトを使ってください。

```bash
python3 scripts/validate_kokuji_schema.py schema/kokuji20250320_asukoe.xsd output/xxx-final.xml [他のXML...]
```

---

## 3. 変換前後の内容検証（compare_xml_text_content.py）

変換パイプラインの出力が元ファイルの内容を保っているかを検証します。パイプライン（`run_pipeline.sh` およびWebアプリのホーム）では自動実行され、Webアプリの「納品前検証」ページでは任意の2ファイルに対して単独実行できます。

### コマンド

```bash
python3 scripts/compare_xml_text_content.py [変換前XML] [変換後XML] [--report_file レポート先] [--ignore-spaces]
```

-   `--report_file`: レポートの保存先（既定: `xml_comparison_report.txt`）
-   `--ignore-spaces`: 全角・半角スペースの有無を無視して比較します。文頭全角スペース補填を適用した後のファイルを検証する場合に指定してください。

### 検証項目

| 項目 | 内容 | 不一致時 |
|---|---|---|
| テキストの欠落 | 変換前の各テキスト要素が変換後に存在するか（完全一致または部分一致）。ラベル＋本文の1要素がTitle要素と本文に分割された場合は、スペース位置で分割した全断片が存在すれば欠落とみなさない | エラー |
| 文書順 | 全文を文書順に連結して比較し、順序の入れ替わり・欠落を位置と直前の文脈付きで報告 | エラー |
| 表（TableStruct） | 数と内容の順序。表題（TableStructTitle）は表の内外どちらにあっても内容一致とみなす | 数・順序の不一致はエラー、位置だけの変化は警告 |
| 図（Fig） | `src` 属性を文書順に並べ、数と順序が一致するか | エラー |
| 構造要素の数 | `TableStruct`/`FigStruct`/`StyleStruct`/`Fig` の出現数。テキストを持たないため、複製・欠落はここでのみ検出できる | エラー（複製か欠落かを表示） |

いずれかの項目でエラーがあると終了コード1を返し、レポートにも記録されます。

### 出力例（成功時）

```
✅ Success: All text content from the original file is present in the final file.
✅ Text order is correct.
✅ Table order is correct.
✅ Figure order is correct.
✅ Struct element counts are correct. (TableStruct=3, FigStruct=9, StyleStruct=0, Fig=9)
```
