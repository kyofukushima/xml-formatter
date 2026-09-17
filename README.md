# XML パイプライン処理ガイド

## 概要

`scripts/run_pipeline.sh` は、入力フォルダ内の全XMLファイルを順次変換し、出力フォルダに最終結果と検証レポートを保存するパイプラインスクリプトです。構造変換に加え、XML構文チェックとテキスト内容の整合性検証を自動で行います。

同じ変換・検証をブラウザから実行できるStreamlit製Webアプリ（`app.py`）も用意しています。Webアプリでは各変換オプションのON/OFF、文頭全角スペース補填、ラベル種別の手動指定、逆変換などをGUIで操作できます。起動方法とページ構成は[QUICKSTART_APP.md](./QUICKSTART_APP.md)を、各ページの機能は本書の「[Webアプリのページ構成](#webアプリのページ構成)」を参照してください。

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
- **テキスト内容検証**: パイプライン完了後に `compare_xml_text_content.py` を実行し、元XMLと最終XMLを比較します（レポート: `...-validation_report.txt`）。いずれかの項目で不一致があると終了コード1を返します。検証項目は次のとおりです。
  - **テキストの欠落**: 元XMLの各テキスト要素が最終XMLに存在するか（完全一致または部分一致）。「①　本文」のようにラベル＋本文の1要素がTitle要素と本文Sentenceに分割されるマークアップは、スペース位置で分割した全断片が最終XMLの要素と完全一致すれば欠落とみなしません（分割フォールバック）。
  - **文書順の比較**: 全文を文書順に連結して比較し、順序の入れ替わり・欠落を位置と直前の文脈付きで報告します。
  - **表（TableStruct）**: 数と内容の順序を比較します。内容が同じで位置だけ変わったものは警告（正常）として表示します。表題（TableStructTitle）は表の内外どちらにあっても内容一致とみなします。
  - **図（Fig）**: `src`属性を文書順に並べ、数と順序が完全一致するかを検証します。
  - **構造要素の数**: `TableStruct`/`FigStruct`/`StyleStruct`/`Fig` の出現数を比較し、複製・欠落を検出します。これらは自身にテキストを持たないため、テキスト比較だけでは複製も欠落も素通りします（Article分割によるFigStructの複製がこの検査で検出されます）。
  - **スペース無視オプション**（`--ignore-spaces`）: 全角・半角スペースの有無を無視して比較します。全角スペース補填後のファイルを検証する場合に使います。Webアプリの「納品前検証」ページにチェックボックスがあります。

```bash
# CLIでの個別実行
python3 scripts/compare_xml_text_content.py 変換前.xml 変換後.xml --report_file report.txt
python3 scripts/compare_xml_text_content.py 変換前.xml 変換後.xml --ignore-spaces
```

### Num属性の採番

変換で生成・分割した要素の`Num`属性は `scripts/utils/renumber_utils.py` の共通関数で採番します。タイトル（`ArticleTitle`/`ItemTitle`等）から番号を導出できる場合はコーパス準拠の枝番形式で採番し（「六の二」→`Num="6_2"`、「第十三条の二」→`Num="13_2"`）、全角・半角アラビア数字と漢数字（十・百・千の合成）に対応します。同じ親の子要素すべてが導出可能かつ一意な場合のみタイトル由来とし、1つでも導出できないもの（「（１）」「イ」等）があれば従来どおり1からの連番にフォールバックします。`Paragraph`の`Num`はスキーマ上正の整数のため常に連番です。

### 文頭全角スペース補填（オプション）

告示データ整備方針に基づき、段落冒頭の1字下げを全角スペースで再現する後処理を用意しています（`scripts/postprocess_fullwidth_space.py`）。Webアプリではパイプラインの最終段として実行され、サイドバーのチェックボックス「変換後に文頭全角スペースを補填する」で適用の有無を指定できます（**デフォルトON**。サブオプションの「List内のSentenceも対象にする」「「（」で始まるSentenceは対象外にする」はデフォルトOFF）。`run_pipeline.sh` には含まれないため、CLIでは下記コマンドで個別に実行してください。「文頭スペース補填」ページではパイプラインを通さず補填のみを単独実行できます。また、専用の設定ページ（`app_pages/fullwidth_space_settings.py`）では、各オプションのXML例（補填前→補填後）を確認しながら設定できます。例の「補填後」は実際の補填処理をサンプルXMLに適用した結果を表示するため、例示と実動作は常に一致します。設定はサイドバーと共有されます。

- **対象**: ①Title要素が空のItem/Subitem1～10のSentence冒頭、②`LineBreak="true"`のColumn内Sentence冒頭（Titleあり要素の先頭Column＝見出しは番号と同じ行のため対象外）、③List内Sentence冒頭（サブオプション、デフォルト対象外）
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

### 表・図の後のListの保護（オプション）

告示スキーマ（`schema/kokuji20250320.xsd`）では、`Item`/`Subitem1`～`Subitem10` の内容が「本文（`*Sentence`）→ 下位のSubitem → `TableStruct`/`FigStruct`/`StyleStruct`/`List`」の順序で固定されています。本文の直後に表・図があり、その後にListが続くデータをそのまま変換すると、表・図の後ろに下位のSubitemが作られスキーマ違反になります。これを防ぐオプションです。Webアプリのサイドバーにあるチェックボックス「表・図の後のListを変換せず保持する」で切り替えます（デフォルトOFF＝従来動作）。設定ページ「List保護・統合設定」でXML例を確認できます。

- **動作**: ONの場合、親要素（Item/Subitem）の直下に表・図が置かれた後に続くListは、変換せずListのまま残します（表・図の後ろにListを置くことはスキーマで許容されています）。ColumnなしList統合オプションの対象にもなりません。
- **対象外**: 表・図の**前**にListがある場合、そのListは従来どおり変換され、表・図は変換後のSubitemの中に取り込まれます。親要素直下に表・図が残らないため、後続のListも従来どおり変換されます。`Paragraph` は本文の直後に表・図、その後にItemを置くことが許容されているため、Item変換（`convert_item_step0.py`）ではこの設定に関わらず従来どおり変換されます。
- **後方互換**: OFFのままなら従来と完全に同じ動作です。
- **対応スクリプト**: `convert_item_step0.py`、`convert_subitem1～10_step0.py`（`--preserve-lists-after-struct`フラグ。他のオプションと併用可）
- **単体テスト**: `scripts/test_data/unit_tests/preserve_lists_after_struct/run_tests.py`

```bash
# CLIでの個別実行
python3 scripts/convert_subitem1_step0.py input.xml output.xml --preserve-lists-after-struct
```

---

### 連続するColumnなしListの統合（オプション）

告示データ整備方針①（同一項番内の段落分けを`LineBreak="true"`のColumnで表現）に合わせて、連続するColumnなしList（段落）を個別の要素に分割せず、1つの要素の`*Sentence`内に`Column`（`LineBreak="true"`）として統合するオプションです。Webアプリのサイドバーにあるチェックボックス「連続するColumnなしListをLineBreak付きColumnとして1要素に統合する」で切り替えます（**WebアプリではデフォルトON**。OFFにすると従来どおり段落ごとに個別のItem/Subitemへ分割します。CLIでは`--merge-no-column-lists`を指定したときのみ有効）。設定ページ「List保護・統合設定」（`app_pages/enumeration_settings.py`）でXML例（変換前→変換後）を確認できます。

- **Paragraph直下**: ParagraphSentenceの直後に連続するColumnなしListは、1つの空TitleのItemにまとめ、`ItemSentence`内の`Column Num="1"…"n"`（すべて`LineBreak="true"`）として並べます（従来は`no_column_text_split_mode`により個別のItemに分割）。
- **単独のColumnなしList**: 連続せず1つだけのColumnなしList（統合相手がないもの）は、Columnで包まず従来どおり`*Sentence`直下の`Sentence`として変換します。LineBreak付きColumnは複数段落を1要素にまとめるための構成のため、段落が1つの場合には付与しません。
- **Titleあり要素の本文直後**: ラベル付きListから変換した要素（例:「（１）　見出し」）や、入力時点のItem/Subitemの本文直後に続くColumnなしListは、本文（見出し）を`Column Num="1"`に包み、各段落を`Column Num="2"`以降として`*Sentence`内に畳み込みます。空TitleのSubitemは作りません。
- **LineBreak属性**: `LineBreak="true"`は「そのColumnの後ろで改行する」指示のため、見出しのColumnを含むすべてのColumnに付与します。
- **終了条件**: ラベル付き（Columnあり）List、既存のItem/Subitem要素、TableStruct等が現れた時点で統合を終了し、以降は従来どおり処理します（ラベル付きListは従来どおり直前の要素に取り込まれます）。
- **対象外**: 画像のみのList（QuoteStruct/Fig）と括弧付き見出し（科目名・指導項目・学年）のListは従来どおり処理します。Columnあり（非ラベル）Listを続きの段落として連結する処理（改行しないColumnの連結）は非対応です。
- **全角スペース補填との整合**: 補填処理はTitleあり要素の先頭Column（見出し）を対象外とするため、見出しには補填されず、Column2以降の段落と空Title要素の先頭Columnに補填されます。
- **対応スクリプト**: `convert_item_step0.py`、`convert_subitem1～10_step0.py`（`--merge-no-column-lists`フラグ。保護オプションと併用可）
- **単体テスト**: `scripts/test_data/unit_tests/merge_no_column_lists/run_tests.py`

```bash
# CLIでの個別実行
python3 scripts/convert_item_step0.py input.xml output.xml --merge-no-column-lists
```

---

### ColumnなしListの分割モード（設定ファイル）

ColumnなしList（段落）が連続したときの取り込み方は `scripts/config/label_config.json` の `conversion_behaviors` で階層別に設定します。Webアプリの「ラベル設定管理」ページでも切り替えられ、XML例（入力→出力）を確認できます。

| 設定キー | 画面上の名称 | OFFの動作 | ONの動作（既定） |
|---|---|---|---|
| `no_column_text_split_mode` | 分割モードを有効化 | 直前の要素にList要素のまま取り込む（モード1） | 並列分割して別々のItem/Subitem要素にする（モード2）。ラベル付きListが現れた時点で分割を終了し、TableStruct/FigStruct等は取り込む |
| `image_list_split_mode` | 画像List後の並列分割を有効化 | 画像List（QuoteStructのみ）由来の要素の後に続くテキストのColumnなしListを同じSentenceコンテナ内のSentenceとして統合 | 並列分割して別々の要素にする。数式画像とその変数説明のListが連続する告示データ向け。後続List同士の並列分割には分割モードもONである必要がある |

変換前後のXML例は[変換モード切り替え.md](./変換モード切り替え.md)と[変換例.md](./変換例.md)を参照してください。上記「連続するColumnなしListの統合」オプションをONにした場合は、統合対象の範囲では分割モードより統合が優先されます。

### ラベル種別の手動指定（オーバーライド）

ラベル判定は `label_config.json` の正規表現で自動判定しますが、特定の文書では誤判定が起こります（例: 括弧アルファベット「（ｃ）」「（ｄ）」が、同じ文書内のローマ数字系列「（ｉ）」「（ｉｉ）」に引かれて括弧ローマ数字と判定される）。この場合、Webアプリのホームでファイルをアップロードした後に表示される「ラベル種別の手動指定」で、値ごとに扱いたいラベル種別を選んで「適用」すると、変換処理とラベル判定表の両方に反映されます。

- 指定内容は `label_config.json` の `label_overrides` に「値 → ラベルID」として保存され、自動判定より優先されます。
- 「特定のファイルだけ特定の扱いをする」ための一時設定という位置づけのため、**アプリ（サーバープロセス）起動時にリセット**されます。設定中は画面上部に警告と「手動指定をすべてクリア」ボタンが表示されます。
- 恒久的にルールを変えたい場合は手動指定ではなく「ラベル設定管理」ページでラベル定義を編集してください。

---

## Webアプリのページ構成

`streamlit run app.py` で起動すると、左メニューに次のページが表示されます（`app_pages/` 配下がページの実体です）。

| グループ | ページ | 機能 |
|---|---|---|
| | ホーム | XMLを1ファイルアップロードし、ラベル判定表の確認、ラベル種別の手動指定、パイプライン変換（実行スクリプト・各オプションはサイドバーで選択）、構文検証・テキスト内容検証の自動実行、結果と中間ファイルのダウンロード |
| | 逆変換 | Item〜Subitem10の階層をList要素に戻す。Item要素を処理する親要素（Paragraph/Class/AppdxTable/TableColumn/Remarks/NewProvision）の個別選択と、逆変換前の文頭全角スペース除去に対応 |
| | List有無判定 | 複数XMLまたはフォルダをZIP化したものをアップロードし、List要素の有無と個数を一覧表示（フォルダ階層を列として表示、CSVダウンロード可） |
| | 文頭スペース補填 | パイプラインを通さず、文頭全角スペース補填のみを単独実行 |
| | 納品前検証 | 変換前後のXMLをアップロードし、ホームの変換後に自動実行される検証と同じ内容（テキスト欠落・文書順・表・図・構造要素数）を単独実行。スペース無視オプション付き |
| 設定 | ラベル設定管理 | `label_config.json` のラベル定義、優先度、分割モード（ColumnなしList・画像List）等の編集 |
| 設定 | 全角スペース補填設定 | 補填オプションをXML例（補填前→補填後）を見ながら設定。サイドバーと連動 |
| 設定 | List保護・統合設定 | 列記List保護、LineBreak付きList保護、ColumnなしList統合、表・図の後のList保護をXML例（変換前→変換後）を見ながら設定。サイドバーと連動 |

---

## 出力とファイル配置

```
output/
├── <入力名>-final.xml                 # 最終出力
└── intermediate_files/
    └── <入力名>/
        ├── <入力名>-<各ステップ>.xml        # 中間XML
        ├── <入力名>_before_fullwidth_space.xml  # 全角スペース補填前（Webアプリで補填ONのとき）
        ├── <入力名>-parse_validation.txt    # 構文検証レポート
        └── <入力名>-validation_report.txt   # テキスト検証レポート
```

- 最終ファイルは常に `<入力名>-final.xml` として `<output_folder>` にコピーされます。
- 中間ファイルと検証レポートは出力フォルダ配下の `intermediate_files/` にまとめて保存されます。
- **出力XMLの整形**: 各ステップの保存時に構造要素だけをインデントします。`Sentence`・各種`Title`/`Caption`・`Ruby`等のインライン要素の内側には改行やインデントを追加しません（ふりがなの`</Rt>`と`</Ruby>`の間に空白が入って表示上の改行になる問題への対処。整形処理は `scripts/utils/xml_utils.py` の `indent_xml_preserving_inline` / `format_xml_lxml` に共通化されており、正変換・逆変換の全スクリプトが使用します）。

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

**最終更新**: 2026年9月
