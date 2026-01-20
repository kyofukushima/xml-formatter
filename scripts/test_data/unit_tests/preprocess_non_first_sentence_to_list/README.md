# preprocess_non_first_sentence_to_list.py 単体テスト

`preprocess_non_first_sentence_to_list.py`の単体テストケースです。

このスクリプトは、前処理として、Paragraph要素だけでなく、Item要素やSubitem1-5要素内のSentence要素も処理します。
各要素タイプで、タイトル要素の直後のSentence要素（1個目）以外をList要素に変換します。

## テスト構造

各テストケースは個別のディレクトリに配置され、以下のファイルを含みます：

- `input.xml`: テスト入力ファイル
- `expected.xml`: 期待される出力ファイル
- `output.xml`: テスト実行時に生成される出力ファイル（自動生成）

## テストケース一覧

### 01_pattern1_split_label
ラベルとテキストが全角スペースで分割されている場合、`ParagraphSentence`を`List`要素に変換する。

**入力例:**
```xml
<ParagraphSentence>
  <Sentence Num="1">（１）　項目名</Sentence>
</ParagraphSentence>
```

**期待される出力:**
```xml
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence Num="1">（１）</Sentence>
    </Column>
    <Column Num="2">
      <Sentence Num="1">項目名</Sentence>
    </Column>
  </ListSentence>
</List>
```

### 02_pattern2_skip_not_label
全角スペースで分割されているが、前半がラベルではない場合、変換されない。

**入力例:**
```xml
<ParagraphSentence>
  <Sentence>ただの文章　これは変換されない。</Sentence>
</ParagraphSentence>
```

**期待される出力:** 入力と同じ（変換なし）

### 03_pattern3_skip_no_space
ラベルが含まれているが、全角スペースがない場合、変換されない。

**入力例:**
```xml
<ParagraphSentence>
  <Sentence>（１）これは変換されない。</Sentence>
</ParagraphSentence>
```

**期待される出力:** 入力と同じ（変換なし）

### 04_pattern4_multiple_paragraph_sentences
Paragraph内に複数のParagraphSentenceが存在する場合、ParagraphNumの直後のParagraphSentence以外が変換される。

**入力例:**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence>これはParagraphNumの直後のParagraphSentenceです。変換されません。</Sentence>
  </ParagraphSentence>
  <TableStruct>...</TableStruct>
  <ParagraphSentence>
    <Sentence>（１）　2個目のParagraphSentenceの内容</Sentence>
  </ParagraphSentence>
  <TableStruct>...</TableStruct>
  <ParagraphSentence>
    <Sentence>（２）　3個目のParagraphSentenceの内容</Sentence>
  </ParagraphSentence>
</Paragraph>
```

**期待される出力:**
- ParagraphNumの直後のParagraphSentenceは変換されない
- 2個目以降のParagraphSentenceは変換される

### 05_pattern5_first_has_label
ParagraphNumの直後のParagraphSentenceにラベルが含まれていても、変換されない。

**入力例:**
```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence>（１）　ParagraphNumの直後のParagraphSentenceは変換されません</Sentence>
  </ParagraphSentence>
  <TableStruct>...</TableStruct>
  <ParagraphSentence>
    <Sentence>（２）　2個目のParagraphSentenceは変換されます</Sentence>
  </ParagraphSentence>
</Paragraph>
```

**期待される出力:**
- ParagraphNumの直後のParagraphSentenceは変換されない（ラベルがあっても）
- 2個目以降のParagraphSentenceは変換される

## テストの実行方法

```bash
cd scripts/test_data/unit_tests/preprocess_non_first_sentence_to_list
python3 run_tests.py
```

すべてのテストケースが自動的に実行され、結果が表示されます。

## テスト結果の確認

各テストケースのディレクトリ内に`output.xml`が生成されます。テストが失敗した場合は、`expected.xml`と`output.xml`の差分が表示されます。

