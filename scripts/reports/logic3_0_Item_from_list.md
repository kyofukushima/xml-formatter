# Item修正ロジック0 - ListからItemへの変換

## 対応スクリプト
`convert_item_step0.py`

## 本文章のスコープ
Item特化スクリプト（Step0: ParagraphSentence直後のListをItemに変換）

**前提**: Paragraph修正ロジック3（Step3: Paragraph分割）の処理済みであること

## 項目ラベル定義

項目ラベルの詳細な定義については、[common/label_definitions.md](common/label_definitions.md) を参照してください

## 処理１ ParagraphSentenceの次のList要素がColumn要素を含まないList要素の場合
1. ParagraphSentence要素の下にItem要素を挿入。
2. List要素をItemSentence要素の次に挿入する
3. 次のList要素の判定に映る。
4. 次のList要素もcolumn要素を含まない場合は、Item要素に挿入する
5. Columnを含まないList要素以外に到達した場合は処理を終了

### 例１　columnを含まないList要素が1つ登場
入力例
```xml
<Paragraph Num="1">
    <ParagraphNum />
    <ParagraphSentence>
        <Sentence Num="1">テキスト1</Sentence>
    </ParagraphSentence>
    <List>
        <ListSentence>
        <Sentence Num="1">テキスト2</Sentence>
        </ListSentence>
    </List>
    <List>
        <ListSentence>
        <Column Num="1">
            <Sentence Num="1">（１）</Sentence>
        </Column>
        <Column Num="2">
            <Sentence Num="1">サブ項目</Sentence>
        </Column>
        </ListSentence>
    </List>

```
出力例
```xml
<Paragraph Num="1">
    <ParagraphNum/>
    <ParagraphSentence>
    <Sentence Num="1" >テキスト1</Sentence>
    </ParagraphSentence>
    <Item Num="1">
        <ItemTitle></ItemTitle>
        <ItemSentence>
            <Sentence Num="1" ></Sentence>
        </ItemSentence>
        <List>
            <ListSentence>
            <Sentence Num="1" >テキスト2</Sentence>
            </ListSentence>
        </List>
    </Item>
        <List>
            <ListSentence>
            <Column Num="1">
                <Sentence Num="1">（１）</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">サブ項目</Sentence>
            </Column>
            </ListSentence>
        </List>
    
```

### 例2　columnを含まないList要素が2つ登場
入力例
```xml
<Paragraph Num="1">
    <ParagraphNum />
    <ParagraphSentence>
        <Sentence Num="1">テキスト1</Sentence>
    </ParagraphSentence>
    <List>
        <ListSentence>
        <Sentence Num="1">テキスト2</Sentence>
        </ListSentence>
    </List>
        <List>
        <ListSentence>
        <Sentence Num="1">テキスト3</Sentence>
        </ListSentence>
    </List>
    <List>
        <ListSentence>
        <Column Num="1">
            <Sentence Num="1">（１）</Sentence>
        </Column>
        <Column Num="2">
            <Sentence Num="1">サブ項目</Sentence>
        </Column>
        </ListSentence>
    </List>

```
出力例
```xml
<Paragraph Num="1">
    <ParagraphNum/>
    <ParagraphSentence>
    <Sentence Num="1" >テキスト1</Sentence>
    </ParagraphSentence>
    <Item Num="1">
        <ItemTitle></ItemTitle>
        <ItemSentence>
            <Sentence Num="1" ></Sentence>
        </ItemSentence>
        <List>
            <ListSentence>
            <Sentence Num="1" >テキスト2</Sentence>
            </ListSentence>
        </List>
            <List>
            <ListSentence>
            <Sentence Num="1" >テキスト2</Sentence>
            </ListSentence>
        </List>
    </Item>
    <List>
        <ListSentence>
        <Column Num="1">
            <Sentence Num="1">（１）</Sentence>
        </Column>
        <Column Num="2">
            <Sentence Num="1">サブ項目</Sentence>
        </Column>
        </ListSentence>
    </List>
```

### 処理１-２　columnを含まないList要素が括弧内項目名に該当する場合
ParagraphSentence要素の次のList要素が、入力例のように「〔」と「〕」で囲まれた項目名の場合は、Item要素に変換する

入力例
```xml
<Paragraph Num="1">
    <ParagraphNum />
    <ParagraphSentence>
        <Sentence>項目名１</Sentence>
    </ParagraphSentence>
    <List>
        <ListSentence>
        <Sentence Num="1">〔項目名2〕</Sentence>
        </ListSentence>
    </List>
    <List>
        <ListSentence>
        <Column Num="1">
            <Sentence Num="1">１</Sentence>
        </Column>
        <Column Num="2">
            <Sentence Num="1">項目名３</Sentence>
        </Column>
        </ListSentence>
    </List>
```
出力例
```xml
<Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1">各科目</Sentence>
    </ParagraphSentence>
    <Item Num="1">
        <ItemTitle></ItemTitle>
        <ItemSentence>
            <Sentence Num="1">〔項目名2〕</Sentence>
        </ItemSentence>
    </Item>
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">１</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名３</Sentence>
    </Column>
    </ListSentence>
</List>
```

## 処理２−１ ParagraphSentenceの次のList要素が、Columnが2つあり、ラベルとテキストの構成であり、階層レベルがParagraphNumより深い場合

List要素のColumnの1つ目が項目ラベルに該当し、ParagraphNumの値が空またはParagraphNumとcolumnの1つ目を比較した結果、Columnの1つ目の階層レベルがより深い場合

1. ParagraphSentence要素の下にItem要素を挿入。List要素の項目ラベルに該当するものをItemTitleに挿入し、テキストに該当するものをItemSentence要素に挿入する。
2. その次のList要素のColumnの1つ目が、その前のItemTitle要素と同じ階層パターンの場合、Item要素に1と同様に挿入する（例1-2を参照）
※ 同じパターンではない場合（階層がさらに深い場合）は、処理しない（例1-3,2-3）

### 例1 ParagraphNumが空である
#### 例1-1 column要素が複数あるList要素が1つ連続する
入力例

```xml
<Paragraph Num="1">
    <ParagraphNum />
    <ParagraphSentence>
    <Sentence Num="1">テキスト１</Sentence>
    </ParagraphSentence>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">１</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">項目名１</Sentence>
            </Column>
        </ListSentence>
    </List>
```

出力例

```xml
<Paragraph Num="1">
    <ParagraphNum/>
    <ParagraphSentence>
        <Sentence Num="1" >テキスト１</Sentence>
    </ParagraphSentence>
    <Item Num="1">
        <ItemTitle>１</ItemTitle>
        <ItemSentence>
        <Sentence Num="1" >項目名１</Sentence>
        </ItemSentence>
    </Item>
```

#### 例1-2 column要素が複数あるList要素が2つ連続する
入力例

```xml
<Paragraph Num="1">
    <ParagraphNum />
    <ParagraphSentence>
    <Sentence Num="1">テキスト１</Sentence>
    </ParagraphSentence>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">１</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">項目名１</Sentence>
            </Column>
        </ListSentence>
    </List>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">２</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">項目名２</Sentence>
            </Column>
        </ListSentence>
    </List>
```

出力例

```xml
<Paragraph Num="1">
    <ParagraphNum/>
    <ParagraphSentence>
        <Sentence Num="1" >テキスト１</Sentence>
    </ParagraphSentence>
    <Item Num="1">
        <ItemTitle>１</ItemTitle>
        <ItemSentence>
        <Sentence Num="1" >項目名１</Sentence>
        </ItemSentence>
    </Item>
    <Item Num="2">
        <ItemTitle>２</ItemTitle>
        <ItemSentence>
        <Sentence Num="1" >項目名２</Sentence>
        </ItemSentence>
    </Item>
```

#### 例1-3 column要素が複数あるList要素（項目ラベルが同じレベル）が2つ連続する
入力例

```xml
<Paragraph Num="1">
    <ParagraphNum />
    <ParagraphSentence>
    <Sentence Num="1">テキスト１</Sentence>
    </ParagraphSentence>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">１</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">項目名１</Sentence>
            </Column>
        </ListSentence>
    </List>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">２</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">項目名２</Sentence>
            </Column>
        </ListSentence>
    </List>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">（１）</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">サブ項目名１</Sentence>
            </Column>
        </ListSentence>
    </List>

```

出力例

```xml
<Paragraph Num="1">
    <ParagraphNum/>
    <ParagraphSentence>
        <Sentence Num="1" >テキスト１</Sentence>
    </ParagraphSentence>
    <Item Num="1">
        <ItemTitle>１</ItemTitle>
        <ItemSentence>
        <Sentence Num="1" >項目名１</Sentence>
        </ItemSentence>
    </Item>
    <Item Num="2">
        <ItemTitle>２</ItemTitle>
        <ItemSentence>
        <Sentence Num="1" >項目名２</Sentence>
        </ItemSentence>
    </Item>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">（１）</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">サブ項目名１</Sentence>
            </Column>
        </ListSentence>
    </List>
```

### 例2 ParagraphNumがColumnの1つ目の階層レベルがより深い
#### 例2-1 column要素が複数あるList要素が1つ連続する
入力例
```xml
<Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ParagraphSentence>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">（１）</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">サブ項目名１</Sentence>
            </Column>
        </ListSentence>
    </List>
```

出力例
```xml
<Paragraph Num="1">
<ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>
        <Sentence Num="1" >項目名1</Sentence>
    </ParagraphSentence>
    <Item Num="1">
        <ItemTitle>（１）</ItemTitle>
        <ItemSentence>
        <Sentence Num="1" >サブ項目名１</Sentence>
        </ItemSentence>
    </Item>
```

#### 例2-2 column要素が複数ある同じ階層パターンのList要素が2つ連続する
入力例
```xml
<Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ParagraphSentence>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">（１）</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">サブ項目名１</Sentence>
            </Column>
        </ListSentence>
    </List>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">（２）</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">サブ項目名２</Sentence>
            </Column>
        </ListSentence>
    </List>
```

出力例
```xml
<Paragraph Num="1">
<ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>
        <Sentence Num="1" >項目名1</Sentence>
    </ParagraphSentence>
    <Item Num="1">
        <ItemTitle>（１）</ItemTitle>
        <ItemSentence>
        <Sentence Num="1" >サブ項目名１</Sentence>
        </ItemSentence>
    </Item>
    <Item Num="1">
        <ItemTitle>（２）</ItemTitle>
        <ItemSentence>
        <Sentence Num="1" >サブ項目名２</Sentence>
        </ItemSentence>
    </Item>
```

#### 例2-3 column要素が複数ある同じ階層パターンのList要素が2つ連続し、さらに深い階層のパターンが登場する
入力例
```xml
<Paragraph Num="1">
    <ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ParagraphSentence>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">（１）</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">サブ項目名１</Sentence>
            </Column>
        </ListSentence>
    </List>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">（２）</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">サブ項目名２</Sentence>
            </Column>
        </ListSentence>
    </List>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">（（１））</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">サブサブ項目名１</Sentence>
            </Column>
        </ListSentence>
    </List>
```

出力例
```xml
<Paragraph Num="1">
<ParagraphNum>１</ParagraphNum>
    <ParagraphSentence>
        <Sentence Num="1" >項目名1</Sentence>
    </ParagraphSentence>
    <Item Num="1">
        <ItemTitle>（１）</ItemTitle>
        <ItemSentence>
        <Sentence Num="1" >サブ項目名１</Sentence>
        </ItemSentence>
    </Item>
    <Item Num="1">
        <ItemTitle>（２）</ItemTitle>
        <ItemSentence>
        <Sentence Num="1" >サブ項目名２</Sentence>
        </ItemSentence>
    </Item>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">（（１））</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">サブサブ項目名１</Sentence>
            </Column>
        </ListSentence>
    </List>
```
