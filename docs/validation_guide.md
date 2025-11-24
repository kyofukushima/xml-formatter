# XML検証ガイド

このドキュメントでは、XMLファイルが整形式（well-formed）であるか、またスキーマ定義（XSD）に準拠しているかを確認するための検証コマンドについて説明します。

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
