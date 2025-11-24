# Paragraph修正ロジック2

## 対応スクリプト
`convert_paragraph_step2.py`

## 本文章のスコープ
Paragraph特化スクリプト（Step2: ParagraphSentence作成）

**前提**: Paragraph修正ロジック1（Step1: ParagraphNum補完）の処理済みであること

## 項目ラベル定義

項目ラベルの詳細な定義については、[common/label_definitions.md](common/label_definitions.md) を参照してください


## 処理１ ParagraphNumの次のList要素が、文章である場合

ParagraphSentence要素に文章を変換する。

入力例

```xml
<Paragraph Num="1">
  <ParagraphNum />
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト</Sentence>
    </ListSentence>
  </List>
```

出力例

```xml
<Paragraph Num="1">
	<ParagraphNum />
  <ParagraphSentence>
  	<Sentence Num="1" >テキスト</Sentence>
  </ParagraphSentence>
```

## 処理２　ParagraphNumの次のList要素が、項目ラベル付きである場合

ラベルをParagraphNum要素に挿入し、テキストをParagraphSentence要素に変換する

※ ただし、この例は実例として未発見

入力例

```xml
<Paragraph Num="1">
  <ParagraphNum />
  <List>
    <ListSentence>
      <Column Num="1">
      	<Sentence Num="1">１</Sentence>
      </Column>
      <Column Num="2">
      	<Sentence Num="1">テキスト</Sentence>
      </Column>
    </ListSentence>
  </List>

```

出力例

```xml
<Paragraph Num="1">
<ParagraphNum>１</ParagraphNum>
<ParagraphSentence>
	<Sentence Num="1">テキスト</Sentence>
</ParagraphSentence>
```
なお、大抵は最初の要素はすでにParagraph要素としてマークアップされている例が多い。

例

```xml
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>
  <Sentence Num="1">テキスト1</Sentence>
  </ParagraphSentence>
  <List>
    <ListSentence>
      <Column Num="1">
     		<Sentence Num="1">２</Sentence>
      </Column>
      <Column Num="2">
      	<Sentence Num="1">テキスト2</Sentence>
      </Column>
    </ListSentence>
  </List>
```
