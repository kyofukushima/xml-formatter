# Paragraph修正ロジック

参考入力ファイル：test_input5.xml

参考出力ファイル：test_output.xml

## 本文章のスコープ
Paragraph特化スクリプト
※ ただし、item特化スクリプト、Article特化スクリプトへの言及あり

パターン１　

## 項目ラベルについて

項目ラベルとは、要素の分割や階層の変更に関係する、文章の区切りを示す文字列群である

次のパターンが存在する。

| パターン名 | 正規表現 | 例 | 変換先候補 |
|-----------|---------|-----|-----------|
| **数字** | `^[０-９0-9]+$` | １、２、３、1、2、3 | Paragraph / Item |
| **括弧数字** | `^[（(][０-９0-9]+[）)]$` | （１）、（２）、(1)、(2) | Item / Subitem1 |
| **カタカナ** | `^[ア-ヴ]+$` | ア、イ、ウ、エ、オ | Subitem1 / Subitem2 |
| **括弧カタカナ** | `^[（(][ア-ヴ]+[）)]$` | （ア）、（イ）、(ア)、(イ) | Subitem2 / Subitem3 |
| **二重括弧カタカナ** | `^[（(]{2}[ア-ヴ]+[）)]{2}$` | （（ア））、（（イ））、((ア))、((イ)) | Subitem3 / Subitem4 |
| **小文字アルファベット** | `^[a-z]+$` | a、b、c | Subitem3 / Subitem4 |
| **全角小文字アルファベット** | `^[ａ-ｚ]+$` | ａ、ｂ、ｃ | Subitem3 / Subitem4 |
| **大文字アルファベット** | `^[A-Z]+$` | A、B、C | Subitem3 / Subitem4 |
| **全角大文字アルファベット** | `^[Ａ-Ｚ]+$` | Ａ、Ｂ、Ｃ | Subitem3 / Subitem4 |
| **括弧小文字アルファベット** | `^[（(][a-z]+[）)]$` | （a）、（b）、(a)、(b) | Subitem4 / Subitem5 |
| **括弧全角小文字アルファベット** | `^[（(][ａ-ｚ]+[）)]$` | （ａ）、（ｂ）、(ａ)、(ｂ) | Subitem4 / Subitem5 |
| **第○パターン** | `^第[0-9０-９一二三四五六七八九十百千]+$` | 第１、第２、第一、第二 | Article（分割） |
| **括弧科目名** | `^〔.+〕$` | 〔医療と社会〕、〔指導項目〕 | Item（特殊） |
| **空** | `^$` | （空文字） | 継承または省略 |

### 階層レベルの順序

項目ラベルには階層レベルがあり、数字が小さいほど浅い階層（上位）、大きいほど深い階層（下位）となる：

| 階層レベル | ラベルの種類 | 例 | XML要素の目安 |
|----------|------------|-----|---------------|
| **0** | 第○パターン | 第１、第２ | `Article`（分割） |
| **1** | 数字 | １、２、３ | `Paragraph` または `Item` |
| **2** | 括弧数字 | （１）、（２） | `Item` または `Subitem1` |
| **3** | カタカナ | ア、イ、ウ | `Subitem1` または `Subitem2` |
| **4** | 括弧カタカナ | （ア）、（イ） | `Subitem2` または `Subitem3` |
| **5** | 二重括弧カタカナ | （（ア））、（（イ）） | `Subitem3` または `Subitem4` |
| **6** | アルファベット | a、b、A、B | `Subitem3` 以降 |
| **7** | 括弧アルファベット | （a）、（ａ） | `Subitem4` 以降 |
| **-** | 括弧科目名 | 〔医療と社会〕 | 階層レベルに影響（特殊処理） |
| **-** | 空 | （空文字） | 親要素を継承 |

### パターン判定の優先順位

同じラベルが複数のパターンにマッチする可能性がある場合、以下の優先順位でチェックする：

1. **括弧科目名**（`〔XXX〕`）- 最優先
2. **第○パターン**（`第○`）- Article分割
3. **二重括弧カタカナ**（`（（ア））`）- より具体的なパターンから先にチェック
4. **括弧アルファベット**（`（a）`）
5. **括弧カタカナ**（`（ア）`）
6. **括弧数字**（`（１）`）
7. **カタカナ**（`ア`）- 括弧なし
8. **アルファベット**（`a、A`）- 括弧なし
9. **数字**（`１`）- 括弧なし
10. **空** - 最後



## 処理1　ParagraphNumが空の場合

Paragraph要素にParagraphNumが存在しない場合は、Paragraph要素の最初に空で追加する
※ ただし、この例は未発見
入力例

```xml
<Paragraph Num="1">
<List>
  <ListSentence>
    <Sentence Num="1">高等部における教育については，学校教育法第７２条に定める目的を実現するために，生徒の障害の状態や特性及び心身の発達の段階等を十分考慮して，次に掲げる目標の達成に努めなければならない。</Sentence>
  </ListSentence>
</List>
```

出力例

```xml
<Paragraph Num="1">
<ParagraphNum />
<List>
  <ListSentence>
    <Sentence Num="1">高等部における教育については，学校教育法第７２条に定める目的を実現するために，生徒の障害の状態や特性及び心身の発達の段階等を十分考慮して，次に掲げる目標の達成に努めなければならない。</Sentence>
  </ListSentence>
</List>
```

## 処理2　ParagraphSentenceがParagraphNum要素の次にない場合

後続の要素によって、処理が変化する

### 処理2-1 ParagraphNumの次にList要素が続く場合

List要素の中の値によって、処理が変化する

#### 処理2-1-1 List要素が文章の場合

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


文章が複数続く場合は、項目ラベルに該当するものに到達するまでItem要素内のリストとして変換する

項目ラベルに該当するものに到達した場合の処理は、別途定義。

入力例（項目ラベルに到達した場合の処理）

```xml
<Paragraph Num="1">
  <ParagraphNum />
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト1</Sentence>
    </ListSentence>
  </List>
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
      	<Sentence Num="1">１</Sentence>
      </Column>
      <Column Num="2">
      	<Sentence Num="1">テキスト</Sentence>
      </Column>
    </ListSentence>
  </List>
```
出力例（項目ラベルに到達した場合の処理）


```xml
<Paragraph Num="1">
	<ParagraphNum />
  <ParagraphSentence>
  	<Sentence Num="1" >テキスト</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle></ItemTitle>
    <ItemSentence>
      <Sentence Num="1" ></Sentence>
    </ItemSentence>
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
  </Item>
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
最終出力例（項目ラベルに到達した場合の処理）
※ 項目ラベルに到達した際の処理（後続で定義）も併せて行なっている

```xml
<Paragraph Num="1">
	<ParagraphNum />
  <ParagraphSentence>
  	<Sentence Num="1" >テキスト</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle></ItemTitle>
    <ItemSentence>
      <Sentence Num="1" ></Sentence>
    </ItemSentence>
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
  </Item>
	<Item Num="2">
    <ItemTitle></ItemTitle>
    <ItemSentence>
	    <Sentence Num="1"></Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
      <Subitem1Title>１</Subitem1Title>
      <Subitem1Sentence>
	      <Sentence Num="1">テキスト</Sentence>
      </Subitem1Sentence>
    </Subitem1>
```

#### 処理2-1-2 List要素がラベル＋文章の場合

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









## 処理3 項目ラベルに該当するものに到達した場合の処理

項目ラベルに該当するものに到達した場合、以下の処理を行う

### 処理の流れ
前提として、最初のParagraphTitle要素の値の階層レベルを基準とする（この処理は、Paragraphのタグを閉じたらリセット）
要するに、最初のParagraphTitle要素が「１」であったならば、次に２が出てきた場合は新たなParagraph要素のParagraphTitle要素として扱い、最初のParagraphTitle要素が「（１）」であったならば、次に（２）が出てきた場合は新たなParagraph要素のParagraphTitle要素として扱う。
そして、別の階層の要素が登場した場合は、その都度対応が異なる
そもそも、最初のParagraphTitle要素が空である（ParagraphSentenceとList要素が続く場合。）
#### 到達した項目ラベルが現在のものと同じ階層レベルの場合
現在の項目を閉じ、同階層の要素を追加し、項目ラベルとテキストはそれぞれtitle要素とsentence要素に挿入する
なお、到達時点で、それまでがList要素できているか、ParagraphSentence要素またはitemSentence,Subitem1Sentence要素（以下、ParagraphSentence群と呼ぶ）できているか、で微妙に対応が異なる。詳細については後述の「List要素の後に到達した場合」「ParagraphSentence群後に到達した場合」を参照

入力例
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
出力例
```xml
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>
    <Sentence Num="1" >テキスト1</Sentence>
  </ParagraphSentence>
</Paragraph>
<Paragraph Num="2">
  <ParagraphNum>２</ParagraphNum>
  <ParagraphSentence>
    <Sentence Num="1" >テキスト2</Sentence>
  </ParagraphSentence>   
```
##### List要素の後に到達した場合
到達した項目ラベルと同階層の要素のタグで閉じる。その後、同階層の要素を新たに追加し、到達した項目ラベルとテキストはそれぞれTitle要素とParagraphSentence群に追加する

入力例1（初期）
```xml
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
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
        <Sentence Num="1">２</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">テキスト3</Sentence>
      </Column>
    </ListSentence>
  </List>
```
入力例2（入力例1に処理1,2を実施）
```xml
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>
    <Sentence Num="1">テキスト1</Sentence>
  </ParagraphSentence>
    <Item Num="1">
      <ItemTitle></ItemTitle>
      <ItemSentence>
        <Sentence Num="1" ></Sentence>
      </ItemSentence>
      <List>
        <ListSentence>
          <Sentence Num="1">テキスト2</Sentence>
        </ListSentence>
      </List>
      <ListSentence>
        <Column Num="1">
          <Sentence Num="1">２</Sentence>
        </Column>
        <Column Num="2">
          <Sentence Num="1">テキスト3</Sentence>
        </Column>
      </ListSentence>
    </List>

```


出力例
```xml
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>
    <Sentence Num="1" >テキスト1</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle></ItemTitle>
    <ItemSentence>
      <Sentence Num="1" ></Sentence>
    </ItemSentence>
  </Item>
  <List>
    <ListSentence>
      <Sentence Num="1" >テキスト2</Sentence>
    </ListSentence>
  </List>
</Paragraph>
<Paragraph Num="2">
  <ParagraphNum>２</ParagraphNum>
  <ParagraphSentence>
    <Sentence Num="1" >テキスト3</Sentence>
  </ParagraphSentence>
```
※ ただし、この例では、入力例は初期の状態であるが、出力例にかけて、途中で処理1,2が起こっている。

#### 到達した項目ラベルが、現在のものより深い階層レベルの場合（深い階層への移行）

現在の階層より深い階層のラベルに到達した場合（現在の階層レベルの数値より、到達した項目ラベルの階層レベルの方が大きい場合）、そのまま残す。
このロジックとは別に、item専用のロジックで処理する

##### 処理手順

1. **階層レベルの差分を計算**
   - 現在のレベルと到達したラベルのレベルの差を計算
   - 差が1の場合：1つ下の階層の要素を作成
   - 差が2以上の場合：List要素をそのままのこす（現状、2以上急に階層を飛ばす実例は見つかっていない）

##### 入力例1-1: レベル差が1の場合（数字 → 括弧数字）※ Paragraphロジック適用後

```xml
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>
    <Sentence  Num="1" >項目1</Sentence>
  </ParagraphSentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence  Num="1" >（１）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence  Num="1" >項目2</Sentence>
      </Column>
    </ListSentence>
  </List>
</Paragraph>
```

##### 出力例1:
item専用ロジック適用後。
```xml
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>
    <Sentence  Num="1" >項目1</Sentence>
  </ParagraphSentence>
    <Item Num="1">
      <ItemTitle>（１）</ItemTitle>
      <ItemSentence>
        <Sentence Num="1" >項目2</Sentence>
      </ItemSentence>
  </Item>
</Paragraph>
```
#### 到達した項目ラベルが、現在のものより浅い階層レベルの場合（浅い階層への戻り）※ itemロジックから適用

本来、Articleのロジックをすでに済ませている想定のため、本ドキュメントで定義しているParagraph修正ロジックでは不要。
見つかった場合は、警告をコメントアウトで記載（処理はしない）

## 基本変換
item要素のロジック以降で起用する
### 処理3-1 Column構造を持つList要素

項目ラベルがColumn[0]に、テキストがColumn[1]に分かれている場合

**入力例:**
```xml
<Paragraph Num="1">
  <ParagraphNum />
  <ParagraphSentence>
    <Sentence>前置テキスト</Sentence>
  </ParagraphSentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence>（１）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence>項目1のテキスト</Sentence>
      </Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence>（２）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence>項目2のテキスト</Sentence>
      </Column>
    </ListSentence>
  </List>
</Paragraph>
```

**出力例:**
```xml
<Paragraph Num="1">
  <ParagraphNum />
  <ParagraphSentence>
    <Sentence>前置テキスト</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
      <Sentence>項目1のテキスト</Sentence>
    </ItemSentence>
  </Item>
  <Item Num="2">
    <ItemTitle>（２）</ItemTitle>
    <ItemSentence>
      <Sentence>項目2のテキスト</Sentence>
    </ItemSentence>
  </Item>
</Paragraph>
```

### 処理3-2: ラベル+スペース+テキスト形式

単一のSentence要素内に「ラベル＋全角スペース＋テキスト」が混在している場合

**入力例:**
```xml
<Paragraph Num="1">
  <ParagraphNum />
  <ParagraphSentence>
    <Sentence>前置テキスト</Sentence>
  </ParagraphSentence>
  <ParagraphSentence>
    <Sentence>（ア）　項目アのテキスト</Sentence>
  </ParagraphSentence>
  <ParagraphSentence>
    <Sentence>（イ）　項目イのテキスト</Sentence>
  </ParagraphSentence>
</Paragraph>
```

**出力例:**
```xml
<Paragraph Num="1">
  <ParagraphNum />
  <ParagraphSentence>
    <Sentence>前置テキスト</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>（ア）</ItemTitle>
    <ItemSentence>
      <Sentence>項目アのテキスト</Sentence>
    </ItemSentence>
  </Item>
  <Item Num="2">
    <ItemTitle>（イ）</ItemTitle>
    <ItemSentence>
      <Sentence>項目イのテキスト</Sentence>
    </ItemSentence>
  </Item>
</Paragraph>
```

### 処理3-3 項目ラベル後に通常テキストが続く場合

項目ラベルの後に、項目ラベルでない通常のテキストが続く場合、それらはList要素として配置

**入力例:**
```xml
<Paragraph Num="1">
  <ParagraphNum />
  <List>
    <ListSentence>
      <Sentence>前置テキスト</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence>１</Sentence>
      </Column>
      <Column Num="2">
        <Sentence>項目1のタイトル</Sentence>
      </Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence>項目1の補足テキスト1</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence>項目1の補足テキスト2</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence>２</Sentence>
      </Column>
      <Column Num="2">
        <Sentence>項目2のタイトル</Sentence>
      </Column>
    </ListSentence>
  </List>
</Paragraph>
```

**出力例:**
```xml
<Paragraph Num="1">
  <ParagraphNum />
  <ParagraphSentence>
    <Sentence>前置テキスト</Sentence>
  </ParagraphSentence>
  <!-- ここまでは処理1,2で対応済み -->
  <Item Num="1">
    <ItemTitle>１</ItemTitle>
    <ItemSentence>
      <Sentence>項目1のタイトル</Sentence>
    </ItemSentence>
    <List>
      <ListSentence>
        <Sentence>項目1の補足テキスト1</Sentence>
      </ListSentence>
    </List>
    <List>
      <ListSentence>
        <Sentence>項目1の補足テキスト2</Sentence>
      </ListSentence>
    </List>
  </Item>
  <Item Num="2">
    <ItemTitle>２</ItemTitle>
    <ItemSentence>
      <Sentence>項目2のタイトル</Sentence>
    </ItemSentence>
  </Item>
</Paragraph>
```

### パターン4: 深い階層への移行（Subitem要素の作成）

項目ラベルの階層レベルが深い場合、適切なSubitem要素を作成
ただし、この処理はsubitemロジックで適用

**入力例:**
```xml
<Paragraph Num="1">
  <ParagraphNum />
  <Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
      <Sentence>項目1</Sentence>
    </ItemSentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence>ア</Sentence>
      </Column>
      <Column Num="2">
        <Sentence>サブ項目ア</Sentence>
      </Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence>イ</Sentence>
      </Column>
      <Column Num="2">
        <Sentence>サブ項目イ</Sentence>
      </Column>
    </ListSentence>
  </List>
  </Item>
  <Item Num="2">
    <ItemTitle>（２）</ItemTitle>
    <ItemSentence>
      <Sentence>項目2</Sentence>
    </ItemSentence>
  </Item>
</Paragraph>
```

**出力例:**
```xml
<Paragraph Num="1">
  <ParagraphNum />
  <Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
      <Sentence>項目1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
      <Subitem1Title>ア</Subitem1Title>
      <Subitem1Sentence>
        <Sentence>サブ項目ア</Sentence>
      </Subitem1Sentence>
    </Subitem1>
    <Subitem1 Num="2">
      <Subitem1Title>イ</Subitem1Title>
      <Subitem1Sentence>
        <Sentence>サブ項目イ</Sentence>
      </Subitem1Sentence>
    </Subitem1>
  </Item>
  <Item Num="2">
    <ItemTitle>（２）</ItemTitle>
    <ItemSentence>
      <Sentence>項目2</Sentence>
    </ItemSentence>
  </Item>
</Paragraph>
```
### 階層判定のロジック

項目ラベルを検出した際、以下の判定を行う：

1. **現在の親要素の確認**
   - Paragraph内 → Item作成
   - Item内 → Subitem1作成（ただし、Itemロジックで対応）
   - Subitem1内 → Subitem2作成（ただし、subitemロジックで対応）
   - ...以下同様

2. **階層レベルの比較**
   - 前のラベルより浅い階層 → 親要素を閉じて新しい要素作成（ただし、Article,Paragraphと、浅いロジックから順に適用していく想定なので、出現しない想定）
   - 前のラベルと同じ階層 → 兄弟要素として作成
   - 前のラベルより深い階層 → 子要素として作成（ただし、ロジック単体では、List要素をそのままのこし、階層の深いロジックで改めて処理）

3. **レベル差が2以上の場合**
   - 出現しない想定であるが、出現したらコメントアウトで警告文を記載

（修正ここまで）

### 処理3-4 特殊ケース: 括弧科目名パターン

`〔科目名〕`のような括弧科目名は、通常のラベルとは異なる特殊な処理を行う。

##### 特徴

1. **階層レベルへの影響**
   - 括弧科目名自体は階層要素（Item等）を作成する
   - 空のTitle要素を作成（ラベルがないため）
   - 科目名はSentence要素に配置

2. **後続要素の処理**
   - 後続の数字ラベルやカタカナラベルは、括弧科目名要素の子要素として配置

##### 入力例: 〔科目名〕→ 数字ラベル

```xml
<Paragraph Num="1">
  <ParagraphNum />
  <ParagraphSentence>
    <Sentence>各科目</Sentence>
  </ParagraphSentence>
  <List>
    <ListSentence>
      <Sentence>〔医療と社会〕</Sentence>
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
      <Column Num="1">
        <Sentence>２</Sentence>
      </Column>
      <Column Num="2">
        <Sentence>内容</Sentence>
      </Column>
    </ListSentence>
  </List>
</Paragraph>
```

##### 出力例:

```xml
<Paragraph Num="1">
  <ParagraphNum />
  <ParagraphSentence>
    <Sentence>各科目</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle></ItemTitle>
    <ItemSentence>
      <Sentence>〔医療と社会〕</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
      <Subitem1Title>１</Subitem1Title>
      <Subitem1Sentence>
        <Sentence>目標</Sentence>
      </Subitem1Sentence>
    </Subitem1>
    <Subitem1 Num="2">
      <Subitem1Title>２</Subitem1Title>
      <Subitem1Sentence>
        <Sentence>内容</Sentence>
      </Subitem1Sentence>
    </Subitem1>
  </Item>
</Paragraph>
```

**注意:**
- 括弧科目名はItemTitle要素を空で作成し、ItemSentence内に配置
- 後続の「１」「２」はSubitem1として配置（階層が1つ下がる）

---

### 補足

同じList要素内でColumnでラベルとテキストが分かれている例と、ParagraphNumの下以外に配置されているParagraphSentence内にラベル＋スペース＋テキスト　で記載されている場合があるが、それぞれ同様にitemTitleとItemSentenceに分割する

入力例

```xml
<Paragraph Num="1">
  <ParagraphNum />
  <List>
    <ListSentence>
      <Sentence Num="1">テキスト1</Sentence>
    </ListSentence>
  </List>
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
      	<Sentence Num="1">（ア）</Sentence>
      </Column>
      <Column Num="2">
      	<Sentence Num="1">テキスト</Sentence>
      </Column>
    </ListSentence>
  </List>
  <ParagraphSentence>
    <Sentence Num="1">（イ）　テキスト</Sentence>
  </ParagraphSentence>
```

出力例

```xml
<Paragraph Num="1">
	<ParagraphNum />
  <ParagraphSentence>
  	<Sentence Num="1" >テキスト</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle></ItemTitle>
    <ItemSentence>
      <Sentence Num="1" ></Sentence>
    </ItemSentence>
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
  </Item>
  <Item Num="2">
    <ItemTitle>（ア）</ItemTitle>
    <ItemSentence>
	    <Sentence Num="1" >テキスト</Sentence>
    </ItemSentence>
  </Item>
    <Item Num="3">
    <ItemTitle>（イ）</ItemTitle>
    <ItemSentence>
	    <Sentence Num="1" >テキスト</Sentence>
    </ItemSentence>
  </Item>
```


## 処理4 実装アルゴリズム

### 処理4-1 階層判定アルゴリズム（擬似コード）

```python
def determine_hierarchy_action(current_level, new_label):
    """
    現在の階層レベルと新しいラベルから、実行すべきアクションを決定
    
    Args:
        current_level (int): 現在の階層レベル (1-7)
        new_label (str): 到達した項目ラベル
    
    Returns:
        dict: {
            'action': 'create_child' | 'create_sibling' | 'close_and_create',
            'target_level': int,
            'empty_levels': List[int]  # 空で作成する中間階層
        }
    """
    new_level = get_hierarchy_level(new_label)
    
    if new_level > current_level:
        # 深い階層への移行
        if new_level - current_level == 1:
            # 直接の子要素
            return {
                'action': 'create_child',
                'target_level': new_level,
                'empty_levels': []
            }
        else:
            # レベル差が2以上 → 空の中間要素を作成
            empty_levels = list(range(current_level + 1, new_level))
            return {
                'action': 'create_child_with_intermediates',
                'target_level': new_level,
                'empty_levels': empty_levels
            }
    
    elif new_level == current_level:
        # 同じ階層 → 兄弟要素
        return {
            'action': 'create_sibling',
            'target_level': new_level,
            'empty_levels': []
        }
    
    else:  # new_level < current_level
        # 浅い階層への戻り
        close_levels = list(range(new_level + 1, current_level + 1))
        return {
            'action': 'close_and_create',
            'target_level': new_level,
            'close_levels': close_levels
        }
```

### 処理4-2 ラベル分離アルゴリズム（擬似コード）

```python
def split_label_and_text(sentence_text):
    """
    Sentence要素内の「ラベル＋スペース＋テキスト」を分離
    
    Args:
        sentence_text (str): Sentence要素のテキスト
    
    Returns:
        Tuple[Optional[str], Optional[str]]: (ラベル, 残りのテキスト)
    """
    # 優先順位順にパターンマッチング
    patterns = [
        r'^〔.+〕$',  # 括弧科目名
        r'^第[0-9０-９一二三四五六七八九十百千]+[\s　]+(.+)$',  # 第○パターン
        r'^[（(]{2}[ア-ヴ]+[）)]{2}[\s　]+(.+)$',  # 二重括弧カタカナ
        r'^[（(][a-zａ-ｚ]+[）)][\s　]+(.+)$',  # 括弧アルファベット
        r'^[（(][ア-ヴ]+[）)][\s　]+(.+)$',  # 括弧カタカナ
        r'^[（(][0-9０-９]+[）)][\s　]+(.+)$',  # 括弧数字
        r'^[ア-ヴ]+[\s　]+(.+)$',  # カタカナ
        r'^[a-zA-Zａ-ｚＡ-Ｚ]+[\s　]+(.+)$',  # アルファベット
        r'^[0-9０-９]+[\s　]+(.+)$',  # 数字
    ]
    
    for pattern in patterns:
        match = re.match(pattern, sentence_text)
        if match:
            # ラベル部分を抽出（スペースの前まで）
            label = sentence_text.split('[\s　]')[0]
            # 残りのテキストを抽出
            text = match.group(1) if match.groups() else None
            return (label, text)
    
    # マッチしない場合
    return (None, sentence_text)
```

### 処理4-3 要素作成フロー

```
1. List要素を走査
   ↓
2. ラベル判定
   - Column構造あり → Column[0]からラベル抽出
   - Column構造なし → Sentenceテキストから分離
   ↓
3. 階層レベル判定
   - get_hierarchy_level(label)
   ↓
4. アクション決定
   - determine_hierarchy_action(current_level, label)
   ↓
5. 要素作成
   - 深い階層: create_child_element()
   - 同じ階層: create_sibling_element()
   - 浅い階層: close_elements() + create_element()
   ↓
6. Title/Sentence挿入
   - ラベル → Title要素
   - テキスト → Sentence要素
   ↓
7. Num属性振り直し
   - 親要素ごとにリセット
```

---

## 処理5 注意事項とエッジケース

### 処理5-1 注意事項

1. **ラベルの判定は優先順位順に行う**（上記「パターン判定の優先順位」参照）
2. **全角・半角の両方に対応**する
3. **括弧の種類**（全角括弧「（）」と半角括弧「()」）の両方に対応する
4. **階層レベルの飛び越し**（例: 数字 → 括弧カタカナ）に対応し、必要に応じて空の中間要素を作成する
5. **Num属性は親要素が変わるたびにリセット**する

### 処理5-2 エッジケース

#### ケース1: 連続する同じラベル

**入力:**
```xml
<List><Sentence>１</Sentence> + <Sentence>項目1</Sentence></List>
<List><Sentence>１</Sentence> + <Sentence>項目2</Sentence></List>
```

**処理:**
- 同じラベル「１」が連続する場合
- 1つ目は新規作成、2つ目も兄弟要素として作成（Num="1", Num="2"）

#### ケース2: ParagraphNumが空で最初がItem相当ラベル

**シナリオ:**
- ParagraphNum: 空
- 最初のList: （１）項目1

**処理:**
- ParagraphNumは空のまま
- ParagraphSentenceは作成しない
- 直接Item要素を作成

#### ケース3: TableStruct/FigStruct要素の処理

**注意:**
- TableStruct、FigStruct要素は通常の階層処理の対象外
- これらの要素内のList要素は変換しない
- 元の構造をそのまま保持

#### ケース4: 空のTitle/Sentenceの扱い

**ルール:**
- Title要素: 空文字列を許可（括弧科目名パターン等）
- Sentence要素: 空文字列を許可（中間階層の空要素）
- ただし、両方が空の場合は要素自体を作成しない場合もある

---

## 処理6 実装時の推奨事項

### 処理6-1 段階的実装

1. **Phase 1: 基本パターン**
   - 数字、括弧数字、カタカナのみ対応
   - 階層レベル1-3のみ

2. **Phase 2: 拡張パターン**
   - 括弧カタカナ、アルファベット追加
   - 階層レベル4-7対応

3. **Phase 3: 特殊パターン**
   - 括弧科目名
   - 第○パターン
   - 空の中間要素自動作成

4. **Phase 4: エッジケース**
   - 全角・半角混在
   - 括弧の種類混在
   - 階層レベルの飛び越し

### 処理6-2 テストケース

各パターンごとに以下のテストケースを作成：

1. **正常系**
   - 標準的な階層構造
   - 連続する同じレベルのラベル

2. **異常系**
   - 階層レベルの飛び越し（2段階以上）
   - 浅い階層への急な戻り

3. **エッジケース**
   - 空のParagraphNum
   - 括弧科目名
   - TableStruct/FigStruct内のList

---

## 処理7 文書のまとめ

### 処理7-1 本文書の構成

| セクション | 内容 | 行数 |
|-----------|------|------|
| **項目ラベルについて** | 14種類のラベルパターン定義 | 63行 |
| **処理1** | ParagraphNumが空の場合 | 22行 |
| **処理2** | ParagraphSentence補完処理 | 283行 |
| **処理3** | 項目ラベル到達時の処理 | 692行 |
| **処理4** | 実装アルゴリズム | 122行 |
| **処理5** | 注意事項とエッジケース | 90行 |
| **処理6** | 実装時の推奨事項 | 36行 |
| **処理7** | 文書のまとめ（本セクション） | - |

### 処理7-2 主要な処理パターン

#### 階層判定の3パターン

1. **同じ階層レベル**
   - 兄弟要素として作成
   - Num属性を連番で付与

2. **深い階層レベル（下位）**
   - 子要素として作成
   - レベル差が2以上の場合、空の中間要素を自動作成

3. **浅い階層レベル（上位）**
   - 該当レベルまですべての要素を閉じる
   - 新しい要素を作成
   - カウンタをリセット

#### 変換の4パターン

1. **Column構造** → Title + Sentence
2. **ラベル+スペース+テキスト** → Title + Sentence  
3. **通常テキスト続き** → List要素として子要素化
4. **深い階層移行** → Subitem要素作成

### 処理7-3 実装の準備状況

#### ✅ 完了している定義

- [x] 14種類の項目ラベルパターン
- [x] 階層レベル0-7の定義
- [x] パターン判定の優先順位（1-10）
- [x] 3つの階層判定パターン（同じ/深い/浅い）
- [x] 4つの変換パターン
- [x] 擬似コードアルゴリズム

#### 📝 実装が必要な項目

- [ ] `utils/label_utils.py` - ラベル判定共通ユーティリティ
- [ ] `convert_paragraph_focused.py` - Paragraph特化スクリプト
- [ ] `convert_item_focused.py` - Item特化スクリプト
- [ ] `convert_subitem_focused.py` - Subitem特化スクリプト

### 処理7-4 実装の推奨順序

#### Phase 1: ラベルユーティリティ（基盤）

```python
# utils/label_utils.py
- detect_label_pattern(label) → str
- get_hierarchy_level(label) → int
- split_label_and_text(text) → Tuple[str, str]
- determine_hierarchy_action(current, new) → dict
```

**目的:** すべての特化スクリプトで共通利用

#### Phase 2: Article特化スクリプト（完了済み）

```
✅ convert_article_focused.py
- 第○パターンの検出
- Article分割処理
- Num属性振り直し（親要素ごと）
```

#### Phase 3: Paragraph特化スクリプト

```
convert_paragraph_focused.py
- 数字ラベルの検出
- 連続番号判定
- 新しいParagraph作成
- ParagraphSentence補完
```

**対象:** 
- 処理1: ParagraphNum補完
- 処理2: ParagraphSentence補完
- 処理3の一部: 数字ラベル → 新しいParagraph

#### Phase 4: Item特化スクリプト

```
convert_item_focused.py
- 括弧数字ラベルの検出
- Item作成
- 後続List要素の子要素化
- 括弧科目名パターン対応
```

**対象:**
- 処理3の主要部分: List → Item変換
- 処理3-1: Column構造
- 処理3-2: ラベル+スペース+テキスト
- 処理3-3: 通常テキスト続き
- 処理3-4: 括弧科目名パターン

#### Phase 5: Subitem特化スクリプト

```
convert_subitem_focused.py
- カタカナ、括弧カタカナ、二重括弧カタカナ
- アルファベット（全半角、括弧付き）
- 深い階層（Subitem1～10）
- 空の中間要素自動作成
```

**対象:**
- 処理3の深い階層部分
- 階層レベル3-7の処理
- 空の中間要素作成

#### Phase 6: 統合テスト

```
- Article → Paragraph → Item → Subitem の順に連続実行
- test_input5.xml → test_output5.xml との比較
- エッジケースのテスト
```

### 処理7-5 参照ドキュメント

| ドキュメント | 説明 | 関連セクション |
|-------------|------|---------------|
| **本文書** | Paragraph修正ロジックの詳細 | 全セクション |
| **修正ロジック分析.md** | 全体的な変換ルール | ルール1-9 |
| **kokuji_markup_policy.md** | マークアップポリシー | パターン1-22 |
| **kokuji20250320.xsd** | XMLスキーマ定義 | 要素定義 |

### 処理7-6 次のステップ

1. **`utils/label_utils.py`の実装**
   - 本文書の擬似コードを実装
   - 14種類のラベルパターンをサポート
   - 階層レベル判定機能

2. **Item特化スクリプトの実装**
   - `convert_item_focused.py`を作成
   - 処理3の主要部分を実装
   - 4つの変換パターンに対応

3. **段階的テスト**
   - 各Phaseごとに動作確認
   - test_input5.xmlで実験
   - 統計情報の収集

4. **統合と最適化**
   - すべてのスクリプトを連続実行
   - パフォーマンス測定
   - エッジケースの対応

---

**文書作成日:** 2025年10月28日  
**最終更新日:** 2025年10月28日  
**総行数:** 1355行以上  
**実装準備状況:** ✅ 完了（実装開始可能）
