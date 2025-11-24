# 教育科目XMLマークアップポリシー

## 概要

このドキュメントは、教育関連XMLファイル（特に文部科学省告示等）において、`List`要素で記述された科目構成を適切な`Item`/`Subitem`階層構造に変換するためのルールを定義します。

## 対象となる文書構造

### 典型的な科目構成パターン

教育関連告示では、以下のような科目構成が一般的です：

```
〔科目名〕
１ 目標
　（長文の目標説明）
　（１）目標の詳細項目1
　（２）目標の詳細項目2
　（３）目標の詳細項目3

２ 内容
　（長文の導入説明）
　〔指導項目〕
　（１）指導項目1
　　ア 詳細項目1-a
　　イ 詳細項目1-b
　（２）指導項目2
　　ア 詳細項目2-a
　　イ 詳細項目2-b
　　ウ 詳細項目2-c

３ 内容の取扱い
　（１）取扱い方法1
　　ア 配慮事項1-a
　　イ 配慮事項1-b
　（２）取扱い方法2
　　ア 配慮事項2-a
```

## 変換ルール

### 1. 階層構造の基本ルール

#### 1.1 科目タイトル → Item要素

**検出パターン**: `〔XXX〕`形式のテキスト（ただし`〔指導項目〕`を除く）

**元のXML構造**:
```xml
<List>
  <ListSentence>
    <Sentence>〔地域保健理療と保健理療経営〕</Sentence>
  </ListSentence>
</List>
```

**変換後の構造**:
```xml
<Item Num="1">
  <ItemTitle>〔地域保健理療と保健理療経営〕</ItemTitle>
  <ItemSentence>
    <Sentence Num="1"></Sentence>
  </ItemSentence>
  <!-- 以下、子要素が続く -->
</Item>
```

#### 1.2 数字タイトル（１、２、３等） → Subitem1要素

**検出パターン**: Column形式で第1カラムが`１`、`２`、`３`等の数字

**元のXML構造**:
```xml
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence>１</Sentence>
    </Column>
    <Column Num="2">
      <Sentence>目標</Sentence>
    </Column>
  </ListSentence>
</List>
```

**変換後の構造**:
```xml
<Subitem1 Num="1">
  <Subitem1Title>１</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">目標</Sentence>
  </Subitem1Sentence>
  <!-- 長文の場合、次にList要素が続く -->
</Subitem1>
```

#### 1.3 長文の取り込み → List要素

**検出パターン**: 数字タイトルの直後に、15文字以上の番号なしテキスト

**元のXML構造**:
```xml
<List>
  <ListSentence>
    <Sentence>保健理療の見方・考え方を働かせ，地域保健理療及び保健理療経営に関する実践的・体験的な学習活動を通して，施術を行うために必要な資質・能力を次のとおり育成することを目指す。</Sentence>
  </ListSentence>
</List>
```

**変換後の構造**（Subitem1内に追加）:
```xml
<Subitem1 Num="1">
  <Subitem1Title>１</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">目標</Sentence>
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Sentence Num="1">保健理療の見方・考え方を働かせ...（長文）</Sentence>
    </ListSentence>
  </List>
</Subitem1>
```

#### 1.4 括弧数字（（１）、（２）等） → Subitem2要素

**検出パターン**: Column形式で第1カラムが`（１）`、`（２）`、`（３）`等の括弧付き数字

**元のXML構造**:
```xml
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence>（１）</Sentence>
    </Column>
    <Column Num="2">
      <Sentence>地域保健理療及び保健理療経営について体系的・系統的に理解するとともに，関連する技術を身に付けるようにする。</Sentence>
    </Column>
  </ListSentence>
</List>
```

**変換後の構造**:
```xml
<Subitem2 Num="1">
  <Subitem2Title>（１）</Subitem2Title>
  <Subitem2Sentence>
    <Sentence Num="1">地域保健理療及び保健理療経営について体系的・系統的に理解するとともに，関連する技術を身に付けるようにする。</Sentence>
  </Subitem2Sentence>
</Subitem2>
```

#### 1.5 カタカナ項目（ア、イ、ウ等） → Subitem3要素

**検出パターン**: Column形式で第1カラムが`ア`、`イ`、`ウ`等のカタカナ

**元のXML構造**:
```xml
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence>ア</Sentence>
    </Column>
    <Column Num="2">
      <Sentence>少子高齢化の現状と動向</Sentence>
    </Column>
  </ListSentence>
</List>
```

**変換後の構造**:
```xml
<Subitem3 Num="1">
  <Subitem3Title>ア</Subitem3Title>
  <Subitem3Sentence>
    <Sentence Num="1">少子高齢化の現状と動向</Sentence>
  </Subitem3Sentence>
</Subitem3>
```

#### 1.6 〔指導項目〕の特殊処理

**検出パターン**: `〔指導項目〕`というテキスト

`〔指導項目〕`は科目タイトルとして扱わず、空タイトルの`Subitem1`要素として処理します。

**元のXML構造**:
```xml
<List>
  <ListSentence>
    <Sentence>〔指導項目〕</Sentence>
  </ListSentence>
</List>
```

**変換後の構造**:
```xml
<Subitem1 Num="3">
  <Subitem1Title></Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">〔指導項目〕</Sentence>
  </Subitem1Sentence>
  <!-- 以下、指導項目の詳細（Subitem2, Subitem3）が続く -->
</Subitem1>
```

### 2. 判定ロジック

#### 2.1 科目タイトルの判定

```python
def is_subject_title(text: str) -> bool:
    """科目タイトルの判定：〔XXX〕形式（〔指導項目〕を除く）"""
    return text.startswith('〔') and text.endswith('〕')
```

**判定条件**:
- テキストが`〔`で始まり`〕`で終わる
- ただし`〔指導項目〕`は例外として科目タイトルとしない

#### 2.2 数字タイトルの判定

```python
def is_numeric_title(text: str) -> bool:
    """数字タイトルの判定：１、２、３等"""
    return text.strip() in ['１', '２', '３', '1', '2', '3', '４', '５', '4', '5']
```

**判定条件**:
- 全角数字: `１`、`２`、`３`、`４`、`５`
- 半角数字: `1`、`2`、`3`、`4`、`5`

#### 2.3 括弧数字の判定

```python
def is_parenthesis_number(text: str) -> bool:
    """括弧数字の判定：（１）、（２）等"""
    import re
    return bool(re.match(r'^[（(]\d+[）)]$', text.strip()))
```

**判定条件**:
- 全角括弧: `（１）`、`（２）`、`（３）`...
- 半角括弧: `(1)`、`(2)`、`(3)`...

#### 2.4 カタカナ項目の判定

```python
def is_katakana_item(text: str) -> bool:
    """カタカナ項目の判定：ア、イ、ウ等"""
    katakana_items = ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ',
                     'サ', 'シ', 'ス', 'セ', 'ソ']
    return text.strip() in katakana_items
```

**判定条件**:
- 対象カタカナ: `ア`、`イ`、`ウ`、`エ`、`オ`、`カ`、`キ`、`ク`、`ケ`、`コ`、`サ`、`シ`、`ス`、`セ`、`ソ`

#### 2.5 長文の判定

```python
def is_long_sentence(text: str) -> bool:
    """長文判定：15文字以上で、番号や記号で始まらない"""
    text = text.strip()
    if len(text) < 15:
        return False
    # 番号や記号で始まっていないか確認
    if re.match(r'^[（(]\d+[）)]', text):
        return False
    if re.match(r'^[１-９1-9]', text):
        return False
    if text[0] in ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ']:
        return False
    return True
```

**判定条件**:
- 15文字以上
- 括弧数字で始まらない
- 数字で始まらない
- カタカナで始まらない

### 3. 変換処理フロー

#### 3.1 科目シーケンスの検出

1. XMLツリー内のすべての`Paragraph`要素を走査
2. `Paragraph`内の`List`要素を順に確認
3. 科目タイトル（`〔XXX〕`形式、`〔指導項目〕`を除く）を検出
4. 科目タイトルから次の科目タイトルまでの`List`要素をシーケンスとして収集

#### 3.2 階層構造の構築

各`List`要素を順に処理し、以下の優先順位で判定・変換：

1. **科目タイトル** → `Item`要素を作成（最初の1回のみ）
2. **〔指導項目〕** → 空タイトルの`Subitem1`要素を作成
3. **数字タイトル（Column形式）** → `Subitem1`要素を作成、カウンタをリセット
4. **長文（単独Sentence）** → 直前が数字タイトルの場合、`List`要素として追加
5. **括弧数字（Column形式）** → `Subitem2`要素を作成、親が`Subitem1`
6. **カタカナ項目（Column形式）** → `Subitem3`要素を作成、親が`Subitem2`

#### 3.3 要素の番号付け

- `Item`: 科目ごとに連番（1, 2, 3...）
- `Subitem1`: `Item`内で連番（1, 2, 3...）
- `Subitem2`: `Subitem1`内で連番（1, 2, 3...）、新しい`Subitem1`で1にリセット
- `Subitem3`: `Subitem2`内で連番（1, 2, 3...）、新しい`Subitem2`で1にリセット

#### 3.4 元のList要素の削除と新要素の挿入

1. 変換対象の`List`要素シーケンスの最初の要素の位置を記録
2. シーケンス内のすべての`List`要素を`Paragraph`から削除
3. 作成した`Item`要素を記録した位置に挿入

### 4. 完全な変換例

#### 4.1 入力XML

```xml
<Paragraph Num="1">
  <ParagraphNum></ParagraphNum>
  <ParagraphSentence>
    <Sentence></Sentence>
  </ParagraphSentence>
  
  <List>
    <ListSentence>
      <Sentence>〔地域保健理療と保健理療経営〕</Sentence>
    </ListSentence>
  </List>
  
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence>１</Sentence>
      </Column>
      <Column Num="2">
        <Sentence>目標</Sentence>
      </Column>
    </ListSentence>
  </List>
  
  <List>
    <ListSentence>
      <Sentence>保健理療の見方・考え方を働かせ，地域保健理療及び保健理療経営に関する実践的・体験的な学習活動を通して，施術を行うために必要な資質・能力を次のとおり育成することを目指す。</Sentence>
    </ListSentence>
  </List>
  
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence>（１）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence>地域保健理療及び保健理療経営について体系的・系統的に理解するとともに，関連する技術を身に付けるようにする。</Sentence>
      </Column>
    </ListSentence>
  </List>
  
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence>２</Sentence>
      </Column>
      <Column Num="2">
        <Sentence>内容</Sentence>
      </Column>
    </ListSentence>
  </List>
  
  <List>
    <ListSentence>
      <Sentence>１に示す資質・能力を身に付けることができるよう，次の〔指導項目〕を指導する。</Sentence>
    </ListSentence>
  </List>
  
  <List>
    <ListSentence>
      <Sentence>〔指導項目〕</Sentence>
    </ListSentence>
  </List>
  
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence>（１）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence>少子高齢社会と社会保障</Sentence>
      </Column>
    </ListSentence>
  </List>
  
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence>ア</Sentence>
      </Column>
      <Column Num="2">
        <Sentence>少子高齢化の現状と動向</Sentence>
      </Column>
    </ListSentence>
  </List>
</Paragraph>
```

#### 4.2 出力XML

```xml
<Paragraph Num="1">
  <ParagraphNum></ParagraphNum>
  <ParagraphSentence>
    <Sentence></Sentence>
  </ParagraphSentence>
  
  <Item Num="1">
    <ItemTitle>〔地域保健理療と保健理療経営〕</ItemTitle>
    <ItemSentence>
      <Sentence Num="1"></Sentence>
    </ItemSentence>
    
    <Subitem1 Num="1">
      <Subitem1Title>１</Subitem1Title>
      <Subitem1Sentence>
        <Sentence Num="1">目標</Sentence>
      </Subitem1Sentence>
      <List>
        <ListSentence>
          <Sentence Num="1">保健理療の見方・考え方を働かせ，地域保健理療及び保健理療経営に関する実践的・体験的な学習活動を通して，施術を行うために必要な資質・能力を次のとおり育成することを目指す。</Sentence>
        </ListSentence>
      </List>
      <Subitem2 Num="1">
        <Subitem2Title>（１）</Subitem2Title>
        <Subitem2Sentence>
          <Sentence Num="1">地域保健理療及び保健理療経営について体系的・系統的に理解するとともに，関連する技術を身に付けるようにする。</Sentence>
        </Subitem2Sentence>
      </Subitem2>
    </Subitem1>
    
    <Subitem1 Num="2">
      <Subitem1Title>２</Subitem1Title>
      <Subitem1Sentence>
        <Sentence Num="1">内容</Sentence>
      </Subitem1Sentence>
      <List>
        <ListSentence>
          <Sentence Num="1">１に示す資質・能力を身に付けることができるよう，次の〔指導項目〕を指導する。</Sentence>
        </ListSentence>
      </List>
    </Subitem1>
    
    <Subitem1 Num="3">
      <Subitem1Title></Subitem1Title>
      <Subitem1Sentence>
        <Sentence Num="1">〔指導項目〕</Sentence>
      </Subitem1Sentence>
      <Subitem2 Num="1">
        <Subitem2Title>（１）</Subitem2Title>
        <Subitem2Sentence>
          <Sentence Num="1">少子高齢社会と社会保障</Sentence>
        </Subitem2Sentence>
        <Subitem3 Num="1">
          <Subitem3Title>ア</Subitem3Title>
          <Subitem3Sentence>
            <Sentence Num="1">少子高齢化の現状と動向</Sentence>
          </Subitem3Sentence>
        </Subitem3>
      </Subitem2>
    </Subitem1>
  </Item>
</Paragraph>
```

## 5. 適用条件と制限事項

### 5.1 適用可能な条件

このマークアップポリシーは、以下の条件を満たす文書に適用可能です：

1. **科目構成が一定**: 「１ 目標」「２ 内容」「３ 内容の取扱い」といった定型的な構成
2. **階層が明確**: 数字 → 括弧数字 → カタカナ の順序で階層化
3. **Column形式の使用**: 番号と内容が2カラムに分離されている
4. **〔XXX〕タイトル**: 科目名が角括弧で囲まれている

### 5.2 制限事項

1. **Column形式の必須性**: 番号と内容が別々の`Column`要素に分離されていない場合、正しく判定できない
2. **番号体系の限定**: 定義された番号体系以外（例：ローマ数字、アルファベット）は未対応
3. **深い階層**: `Subitem3`より深い階層（`Subitem4`以降）は現在のロジックでは未対応
4. **複雑な構造**: 表や図が階層内に混在する場合は追加処理が必要

### 5.3 エラーハンドリング

- 科目タイトルが見つからない場合: シーケンスをスキップ
- 親要素が存在しない場合: 空の親要素を自動作成
- 削除済み要素の削除試行: エラーを無視して続行

## 6. 実装ツール

### 6.1 変換スクリプト

**場所**: `scripts/education_script/convert_list_to_item.py`

**使用方法**:
```bash
python3 convert_list_to_item.py <input_xml_file> [output_xml_file]
```

**例**:
```bash
python3 convert_list_to_item.py input.xml output.xml
```

出力ファイル名を省略した場合、入力ファイル名に`_converted`を付加したファイル名が使用されます。

### 6.2 処理統計

スクリプトは実行後、以下の統計情報を出力します：

- 検出されたシーケンス数
- 作成されたItem要素数
- 作成されたSubitem1要素数
- 作成されたSubitem2要素数
- 作成されたSubitem3要素数

### 6.3 テストデータ

**場所**: `scripts/education_script/test_input.xml`

サンプルの教育科目XMLファイルが用意されており、変換ロジックの動作確認に使用できます。

## 7. 今後の拡張

### 7.1 予想される拡張項目

1. **より深い階層への対応**: `Subitem4`以降の階層
2. **追加の番号体系**: ローマ数字、アルファベット、漢数字等
3. **表・図の統合処理**: 階層内の`TableStruct`、`FigStruct`の適切な配置
4. **複数科目の一括処理**: ディレクトリ内の複数ファイルの一括変換

### 7.2 メンテナンス指針

- 新しいパターンが発見された場合: 判定ロジックに追加し、このドキュメントを更新
- エラーが発生した場合: エラーハンドリングを強化し、ログ出力を追加
- パフォーマンス改善: 大規模ファイルへの対応、並列処理の導入

---

**更新履歴**
- 2025年1月: 初版作成

**参考資料**
- 変換スクリプト: `scripts/education_script/convert_list_to_item.py`
- テストファイル: `scripts/education_script/test_input.xml`
