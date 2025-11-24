# Subitem1修正ロジック

## 本文章のスコープ
`Item`要素内部の`List`要素を`Subitem1`へ変換する、新しい特化スクリプト`convert_subitem1_focused.py`のロジックを定義する。

**前提**: `convert_item_focused.py`（簡易版）による`Item`の分割・集約処理が完了していること。入力XMLは、`Item`要素の子要素として、処理対象の`List`やその他の要素がフラットに並んでいる状態である。

**参照元ロジック**: `archived_item_logic.py`, `logic3_1_Item_archive.md`

---

## 処理の概要
各`Item`要素の内部を走査し、`ItemSentence`以降の子要素を、その種類と階層レベルに応じて`Subitem1`に変換、または`Subitem1`の内部に再配置する。

---

### 処理1: `column`を含まない`List`要素の集約

#### 説明
`ItemSentence`の後に続く、`column`を持たない連続した`List`要素群を、一つの新しい`Subitem1`要素にまとめます。

#### 例
**入力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">項目名１</Sentence>
  </ItemSentence>
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト１</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト２</Sentence>
    </ListSentence>
  </List>
</Item>
```

**出力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">項目名１</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title/>
    <Subitem1Sentence>
      <Sentence Num="1"/>
    </Subitem1Sentence>
    <List>
      <ListSentence>
        <Sentence Num="1">テキスト１</Sentence>
      </ListSentence>
    </List>
    <List>
      <ListSentence>
        <Sentence Num="1">テキスト２</Sentence>
      </ListSentence>
    </List>
  </Subitem1>
</Item>
```

---

### 処理2: `column`を持つ`List`要素の階層化

`Item`の子要素である`List`を、そのラベルの階層に応じて処理します。比較対象の基準（`ref_level`）は、`Item`内に`Subitem1`がなければ`ItemTitle`、あれば**最後の`Subitem1`のタイトル**となります。

#### ケースA: 新しい`Subitem1`の生成

##### 説明
`List`のラベル階層が、比較基準の階層と**同じ**か、**1つだけ深い**場合に、新しい`Subitem1`を生成します。
*(Note: 「1つだけ深い」が適用されるのは、主に`ItemTitle`から最初の`Subitem1`を生成する場合です)*

##### 例
**入力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle> <!-- level 2 -->
  <ItemSentence>
    <Sentence Num="1">...</Sentence>
  </ItemSentence>
  <List> <!-- label 'ア' is level 3 -->
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">ア</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">項目名２</Sentence>
      </Column>
    </ListSentence>
  </List>
  <List> <!-- label 'イ' is level 3 -->
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">イ</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">項目名３</Sentence>
      </Column>
    </ListSentence>
  </List>
</Item>
```

**出力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">...</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence>
      <Sentence Num="1">項目名２</Sentence>
    </Subitem1Sentence>
  </Subitem1>
  <Subitem1 Num="2">
    <Subitem1Title>イ</Subitem1Title>
    <Subitem1Sentence>
      <Sentence Num="1">項目名３</Sentence>
    </Subitem1Sentence>
  </Subitem1>
</Item>
```

#### ケースB: `List`の内部移動 (ネスト)

##### 説明
`List`のラベル階層が、比較基準（最後の`Subitem1`）よりも**さらに深い**場合（階層差が1より大きい）、その`List`は変換せずに**最後の`Subitem1`の内部に移動**させます。これは、後続の`Subitem2`特化スクリプトの処理対象とすることを意図しています。

##### 例
**入力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">...</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title> <!-- level 3 -->
    <Subitem1Sentence>
      <Sentence Num="1">...</Sentence>
    </Subitem1Sentence>
  </Subitem1>
  <List> <!-- label '（ア）' is level 4 -->
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（ア）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">項目名４</Sentence>
      </Column>
    </ListSentence>
  </List>
</Item>
```

**出力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">...</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence>
      <Sentence Num="1">...</Sentence>
    </Subitem1Sentence>
    <List> <!-- Listのまま中に移動 -->
      <ListSentence>
        <Column Num="1">
          <Sentence Num="1">（ア）</Sentence>
        </Column>
        <Column Num="2">
          <Sentence Num="1">項目名４</Sentence>
        </Column>
      </ListSentence>
    </List>
  </Subitem1>
</Item>
```

---

### 処理3: その他の要素の集約

`TableStruct`など、`List`以外の要素は、直前に`Subitem1`が生成されていれば、その**最後の`Subitem1`の内部に移動**させます。

#### 例
**入力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">...</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence>
      <Sentence Num="1">...</Sentence>
    </Subitem1Sentence>
  </Subitem1>
  <TableStruct>...</TableStruct>
</Item>
```

**出力**
```xml
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">...</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence>
      <Sentence Num="1">...</Sentence>
    </Subitem1Sentence>
    <TableStruct>...</TableStruct> <!-- Subitem1の中に移動 -->
  </Subitem1>
</Item>
```

---

### 最終処理: 空の`Subitem1`ラッパーの解除

#### 説明
すべての変換処理の最後に、特定の条件を満たす「空のラッパー」として機能しているだけの`Subitem1`を検索し、解除（アンラップ）するクリーンアップ処理を実行します。これは、`column`のない`List`が一つだけある場合などに、不要な階層が作られるのを防ぐための後処理です。

#### 条件
以下の**すべて**の条件を満たす`<Subitem1>`がクリーンアップの対象です。
1.  `<Subitem1Title>`にテキストがない。
2.  `<Subitem1Sentence>`にテキストがない。
3.  親要素である`<Item>`の`<ItemTitle>`にテキストがない。
4.  親要素である`<Item>`の`<ItemSentence>`にテキストがない。
5.  `<Subitem1>`の子要素が`<List>`のみである。

#### 動作
上記の条件を満たす`Subitem1`が見つかった場合、その`Subitem1`は削除され、内部にあった`<List>`要素は親の`<Item>`の直接の子要素（元の状態）に戻されます。

#### 例
**クリーンアップ処理前の状態**
```xml
<Item Num="1">
  <ItemTitle/>
  <ItemSentence><Sentence/></ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title/>
    <Subitem1Sentence><Sentence/></Subitem1Sentence>
    <List>
      <ListSentence>
        <Sentence Num="1">テキスト</Sentence>
      </ListSentence>
    </List>
  </Subitem1>
</Item>
```

**クリーンアップ処理後の出力**
```xml
<Item Num="1">
  <ItemTitle/>
  <ItemSentence><Sentence/></ItemSentence>
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト</Sentence>
    </ListSentence>
  </List>
</Item>
```
