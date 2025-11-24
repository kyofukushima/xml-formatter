# Paragraph修正ロジック3 - Paragraph分割

## 対応スクリプト
`convert_paragraph_step3.py`

## 本文章のスコープ
Paragraph特化スクリプト（Step3: Paragraph分割）

**前提**: Paragraph修正ロジック2（Step2: ParagraphSentence作成）の処理済みであること

## 項目ラベル定義

項目ラベルの詳細な定義については、[common/label_definitions.md](common/label_definitions.md) を参照してください

## 処理２−２ List要素のColumnの1つ目が項目ラベルに該当し、ParagraphNumの値とcolumnの1つ目を比較した結果、Columnの1つ目の階層レベルが同じである場合

1. Paragraph要素を分割し、columnの1つ目の項目ラベルを新たなParagraph要素のParagraphNumに挿入する。
2. columnの2つ目をParagraphSentenceに挿入する。
※ なお、分割生成した方のParagraph要素は、閉じタグはつけないとともに、もともと存在した分割元のParagraph要素の閉じタグも消さない

なお、分割が発生した場合は、分割後のParagraph要素内に、同様の階層の項目ラベルありのList要素が見つかった時点で再度分割をする（例2）

### 例1 分割が1回
入力例
```xml
<Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>
        <Sentence Num="1">項目名１</Sentence>
    </ParagraphSentence>
    <List>
        <ListSentence>
        <Column Num="1">
            <Sentence Num="1">２</Sentence>
        </Column>
        <Column Num="2">項目名２</Sentence>
        </Column>
        </ListSentence>
    </List>
    {中略}
</Paragraph>
```

出力例
```xml
<Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1" >項目名１</Sentence>
    </ParagraphSentence>
</Paragraph>
<Paragraph Num="2">
    <ParagraphNum>２</ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1" >項目名２</Sentence>
    </ParagraphSentence> 
    {中略}
</Paragraph>
```

### 例2 分割が複数回
#### 1回目の処理
ParagraphNumの要素を元に、最初のList要素を変換する（例１と同様）
入力例
```xml
<Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>
        <Sentence Num="1">項目名１</Sentence>
    </ParagraphSentence>
    <List>
        <ListSentence>
        <Column Num="1">
            <Sentence Num="1">２</Sentence>
        </Column>
        <Column Num="2">項目名２</Sentence>
        </Column>
        </ListSentence>
    </List>
    {中略}
    <List>
        <ListSentence>
        <Column Num="1">
            <Sentence Num="1">３</Sentence>
        </Column>
        <Column Num="2">項目名３</Sentence>
        </Column>
        </ListSentence>
    </List>
    {中略}
</Paragraph>
```

出力例
```xml
<Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1" >項目名１</Sentence>
    </ParagraphSentence>
</Paragraph>
<Paragraph Num="2">
    <ParagraphNum>２</ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1" >項目名２</Sentence>
    </ParagraphSentence> 
    {中略}
    <List>
        <ListSentence>
        <Column Num="1">
            <Sentence Num="1">３</Sentence>
        </Column>
        <Column Num="2">項目名３</Sentence>
        </Column>
        </ListSentence>
    </List>
    {中略}
</Paragraph>
```
#### 2回目の処理
入力例（1回目の処理の出力に同じ）
```xml
<Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1" >項目名１</Sentence>
    </ParagraphSentence>
</Paragraph>
<Paragraph Num="2">
    <ParagraphNum>２</ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1" >項目名２</Sentence>
    </ParagraphSentence> 
    {中略}
    <List>
        <ListSentence>
        <Column Num="1">
            <Sentence Num="1">３</Sentence>
        </Column>
        <Column Num="2">項目名３</Sentence>
        </Column>
        </ListSentence>
    </List>
    {中略}
</Paragraph>
```

出力例
```xml
<Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1" >項目名１</Sentence>
    </ParagraphSentence>
</Paragraph>
<Paragraph Num="2">
    <ParagraphNum>２</ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1" >項目名２</Sentence>
    </ParagraphSentence> 
    {中略}
<Paragraph Num="3">
    <ParagraphNum>３</ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1" >項目名３</Sentence>
    </ParagraphSentence> 
    {中略}
</Paragraph>
```
