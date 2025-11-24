# 告示XML作成マークアップポリシー

## 概要
このドキュメントは、告示文をXML化する際の基本方針と具体的なマークアップルールを定義します。
対象スキーマ：`kokuji20250320.xsd`

## 1. 基本ポリシー

### 1.1 Paragraph要素の必須記述
- スキーマの構成により、必ず`Paragraph`要素は記述する
- 内容が空の場合でも構造維持のため記述

### 1.2 空要素の記述
- スキーマの構成により、必要な場合には空の`Article`や`Paragraph`等を記述
- それぞれ必要となる空の要素（`ParagraphNum`、`ArticleTitle`等）を記述

### 1.3 前文の扱い
- 「第１条」や「第１」の前にある文章は前文とし、`Preamble`として記述
- 告示文の導入部分や背景説明を含む

### 1.4 デザインの再現方針
- 告示は法令と異なり自由な構造で作成されているため、字下げ等のデザインは可能な限り再現する
- ただし、完全な再現は目指さず、XML構造として適切な形に調整

### 1.5 セマンティクス vs データ作成
- データ作成を優先するため、厳密なセマンティクスは考慮しない
- 実用性と処理効率を重視した構造化

### 1.6 要素判定の原則
- 法令とは異なり、文頭の数字や文字の表記に基づく要素の指定は行わない
- 法令の場合：条の下層のアラビア数字は項、項の下層の漢数字は号
- 告示の場合：様々な表記が存在するため、作成されている告示の構造に基づいて要素を判断

### 1.7 XMLスキーマ設定
全てのXMLファイルのLaw要素には以下の属性を必ず含める：
```xml
<Law Era="[年号]" Year="[年]" Num="[番号]" 
     PromulgateMonth="[月]" PromulgateDay="[日]" 
     LawType="Notice" Lang="ja" 
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
     xsi:noNamespaceSchemaLocation="kokuji20250320.xsd">
```

#### ⚠️ 重要：XSDファイルのパス設定
- `xsi:noNamespaceSchemaLocation`の値は、**XMLファイルからkokuji20250320.xsdへの相対パス**で指定する
- XMLファイルとXSDファイルが同じディレクトリにある場合：`"kokuji20250320.xsd"`
- XMLファイルがサブディレクトリにある場合：`"../kokuji20250320.xsd"`（1階層上）
- XMLファイルが深いサブディレクトリにある場合：`"../../kokuji20250320.xsd"`（2階層上）
- パスが間違っているとXMLlintによるスキーマ検証が正常に動作しない

### 1.8 番号体系の柔軟性
告示では様々な番号体系が使用されるため、全てのパターンで以下の番号体系に柔軟に対応する：

#### 対応する番号体系
- **全角数字**: １、２、３
- **半角数字**: 1、2、3
- **括弧数字**: (1)、(2)、(3)
- **括弧小文字**: (a)、(b)、(c)
- **括弧大文字**: (A)、(B)、(C)
- **漢数字**: 一、二、三
- **漢数字+読点**: 一、、二、、三、
- **階層番号**: 1.1.1、1.1.2
- **数字+ピリオド**: 1.、2.、3.
- **カタカナ**: イ、ロ、ハ
- **ひらがな**: ア、イ、ウ

#### マークアップ時の対応
- 各パターンの説明で特定の番号体系を例示している場合でも、実際の文書の番号体系に合わせて柔軟に適用する
- 番号の内容は元文書のまま各Title要素（`ParagraphNum`、`ItemTitle`、`Subitem1Title`等）に記述する
- 番号体系の違いによってパターンの判定や要素構造を変更することはない

### 1.9 表・図の配置
階層の中に表や図が含まれる場合は、スキーマ定義に従って適切な要素内に配置する：

#### 配置可能な要素
- **Paragraph**: 段落レベルで表・図を配置
- **Item**: 項目レベルで表・図を配置
- **Subitem1〜Subitem10**: 各階層のサブ項目レベルで表・図を配置
- **GeneralParagraph**: 一般段落レベルで表・図を配置
- **AppdxTable**: 別表内で表・図を配置
- **AppdxNote**: 別記内で表・図を配置
- **AppdxFig**: 別図内で表・図を配置

#### マークアップ方法
- **TableStruct**: 表を含む場合に使用
  ```xml
  <Item Num="1">
    <ItemTitle>項目番号</ItemTitle>
    <ItemSentence>
      <Sentence>項目内容</Sentence>
    </ItemSentence>
    <TableStruct>
      <Table>
        <!-- 表の内容 -->
      </Table>
    </TableStruct>
  </Item>
  ```

- **FigStruct**: 図を含む場合に使用
  ```xml
  <Item Num="1">
    <ItemTitle>項目番号</ItemTitle>
    <ItemSentence>
      <Sentence>項目内容</Sentence>
    </ItemSentence>
    <FigStruct>
      <Fig src="図のパス"/>
    </FigStruct>
  </Item>
  ```

#### 配置の原則
- 表・図は文書内での出現位置に応じて最も適切な階層レベルの要素内に配置する
- 複数の表・図がある場合は、それぞれを独立したTableStruct・FigStructとして配置する
- 表・図の前後にテキストがある場合は、List要素等と組み合わせて使用する

#### パス設定例
```
プロジェクト構造例：
kokuji_xml_mcp_server/
├── kokuji20250320.xsd                    # スキーマファイル
├── 告示A.xml                             # → "kokuji20250320.xsd"
└── subfolder/
    ├── 告示B.xml                         # → "../kokuji20250320.xsd"
    └── deep/
        └── 告示C.xml                     # → "../../kokuji20250320.xsd"
```

## 2. パターン別対応方法

### パターン1：文頭番号なし項目列挙型告示

#### 文章のパターン概要
- 文頭に番号がない文章（またはタイトル＋文章）があり、その後に「一」「二」と続くパターン
- 冒頭の説明文または導入文の後に項目が列挙される形式
- 漢数字パターンとアラビア数字パターンの両方が存在
- 階層化されている場合には「SubItem1」「SubItem2」等で記述

#### 文章のマークアップ方法説明
- MainProvision以下、文頭番号がない文章を「Paragraph」として「ParagraphSentence」で記述
- 以降の番号付き文章は「Paragraph」内の「Item」として「一」を「ItemTitle」、文章を「ItemSentence」で記述
- さらに階層化されている場合には、「SubItem1」「SubItem2」などで記述

#### 文章のパターン例
```
告示文

テキスト

一　項目名A
テキスト

二　項目名B
テキスト
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>テキスト</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle>一</ItemTitle>
      <ItemSentence>
        <Sentence>項目名A</Sentence>
      </ItemSentence>
      <Subitem1 Num="1">
        <Subitem1Title></Subitem1Title>
        <Subitem1Sentence>
          <Sentence>テキスト</Sentence>
        </Subitem1Sentence>
      </Subitem1>
    </Item>
    <Item Num="2">
      <ItemTitle>二</ItemTitle>
      <ItemSentence>
        <Sentence>項目名B</Sentence>
      </ItemSentence>
      <Subitem1 Num="1">
        <Subitem1Title></Subitem1Title>
        <Subitem1Sentence>
          <Sentence>テキスト</Sentence>
        </Subitem1Sentence>
      </Subitem1>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン2：文頭番号なし文章・表併用型告示

#### 文章のパターン概要
- 文頭に番号のない文章（またはタイトル＋文章）があり、その後に表が続くパターン
- 冒頭の説明文や導入文の後に、詳細な情報を表形式で提示する形式
- 表が文章の補完的な役割を果たし、文章と表が一体となって内容を構成

#### 文章のマークアップ方法説明
- MainProvision以下、文頭番号がない文章を「Paragraph」として「ParagraphSentence」で記述
- 表部分は「Paragraph」内に「TableStruct」として「Table」で記述
- 表のヘッダー行がある場合は「TableHeaderRow」と「TableHeaderColumn」を使用
- データ行は「TableRow」と「TableColumn」で記述

#### 文章のパターン例
```
告示文

テキスト

[表：表の内容]
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>テキスト</Sentence>
    </ParagraphSentence>
    <TableStruct>
      <Table>
        <TableHeaderRow>
          <TableHeaderColumn BorderTop="solid" BorderBottom="solid" BorderLeft="solid" BorderRight="solid">
            <Sentence>項目名A</Sentence>
          </TableHeaderColumn>
          <TableHeaderColumn BorderTop="solid" BorderBottom="solid" BorderLeft="solid" BorderRight="solid">
            <Sentence>項目名B</Sentence>
          </TableHeaderColumn>
        </TableHeaderRow>
        <TableRow>
          <TableColumn BorderTop="solid" BorderBottom="solid" BorderLeft="solid" BorderRight="solid">
            <Sentence>テキスト</Sentence>
          </TableColumn>
          <TableColumn BorderTop="solid" BorderBottom="solid" BorderLeft="solid" BorderRight="solid">
            <Sentence>テキスト</Sentence>
          </TableColumn>
        </TableRow>
      </Table>
    </TableStruct>
  </Paragraph>
</MainProvision>
```

### パターン3：項目名型告示

#### 文章のパターン概要
- 文頭に番号+項目名があるパターン、または番号なしの項目名があるパターン
- 各項目が明確なタイトルを持ち、その下に詳細な内容が続く形式
- 項目の内容が複雑で、リストや詳細な説明を含む場合が多い
- 規則、基準、手続き等の詳細を示す告示に多い

#### 文章のマークアップ方法説明
**番号+項目名の場合:**
- MainProvision以下、「番号+項目」を「Paragraph」で記述し、「番号」を「ParagraphNum」、「項目」を「ParagraphSentence」で記述
- 「項目」以降の内容は「List」とするため、「Paragraph」内に「Item」を記述して空の「ItemSentence」、「Sentence」を記述し、「Item」内に「List」を記述

**番号なし項目名の場合:**
- MainProvision以下、「項目名」を「Paragraph」で記述し、「ParagraphNum」は空、「項目名」を「ParagraphSentence」で記述
- 項目名以降の内容（文章）は、「Paragraph」内に「Item」を記述して空の「ItemSentence」、「Sentence」を記述し、「Item」内に「List」を記述

#### 文章のパターン例

**番号+項目名の場合:**
```
告示文

一　項目名A
テキスト
テキスト

二　項目名B
テキスト
テキスト

三　項目名C
テキスト
テキスト
```

**番号なし項目名の場合:**
```
告示文

項目名A
テキスト
テキスト

項目名B 
テキスト
テキスト

項目名C
テキスト
テキスト
```

#### 文章のマークアップ例

**番号+項目名の場合:**
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum>一</ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名A</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle></ItemTitle>
      <ItemSentence>
        <Sentence></Sentence>
      </ItemSentence>
      <List>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
      </List>
    </Item>
  </Paragraph>
  <Paragraph Num="2">
    <ParagraphNum>二</ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名B</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle></ItemTitle>
      <ItemSentence>
        <Sentence></Sentence>
      </ItemSentence>
      <List>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
      </List>
    </Item>
  </Paragraph>
  <Paragraph Num="3">
    <ParagraphNum>三</ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名C</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle></ItemTitle>
      <ItemSentence>
        <Sentence></Sentence>
      </ItemSentence>
      <List>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
      </List>
    </Item>
  </Paragraph>
</MainProvision>
```

**番号なし項目名の場合:**
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名A</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle></ItemTitle>
      <ItemSentence>
        <Sentence></Sentence>
      </ItemSentence>
      <List>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
      </List>
    </Item>
  </Paragraph>
  <Paragraph Num="2">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名B</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle></ItemTitle>
      <ItemSentence>
        <Sentence></Sentence>
      </ItemSentence>
      <List>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
      </List>
    </Item>
  </Paragraph>
  <Paragraph Num="3">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名C</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle></ItemTitle>
      <ItemSentence>
        <Sentence></Sentence>
      </ItemSentence>
      <List>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
      </List>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン4：番号+内容列記型告示

#### 文章のパターン概要
- 文頭に番号+内容が列記されているパターン
- 各項目が番号と具体的な内容（企業名、項目名等）で構成される
- 項目が単純に並列して列挙される形式
- リスト形式の告示や指定・認定型告示に多い

#### 文章のマークアップ方法説明
- MainProvision以下、「Paragraph」の中で「Item」として記述
- 各項目の「番号」を「ItemTitle」、「内容」を「ItemSentence」で記述

#### 文章のパターン例
```
告示文

一　テキスト
二　テキスト  
三　テキスト
四　テキスト
五　テキスト
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence></Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle>一</ItemTitle>
      <ItemSentence>
        <Sentence>テキスト</Sentence>
      </ItemSentence>
    </Item>
    <Item Num="2">
      <ItemTitle>二</ItemTitle>
      <ItemSentence>
        <Sentence>テキスト</Sentence>
      </ItemSentence>
    </Item>
    <Item Num="3">
      <ItemTitle>三</ItemTitle>
      <ItemSentence>
        <Sentence>テキスト</Sentence>
      </ItemSentence>
    </Item>
    <Item Num="4">
      <ItemTitle>四</ItemTitle>
      <ItemSentence>
        <Sentence>テキスト</Sentence>
      </ItemSentence>
    </Item>
    <Item Num="5">
      <ItemTitle>五</ItemTitle>
      <ItemSentence>
        <Sentence>テキスト</Sentence>
      </ItemSentence>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン5：編+条+項目階層型告示

#### 文章のパターン概要
- 編ではじまり章がなく、文頭数字+項目名があり、1、(1)…と階層化するパターン
- 「編」→「条」→「項（番号+項目名）」→「号（項目詳細）」の階層構造
- 複雑な階層を持つ大規模な告示に多用される形式
- 各階層で番号と内容が明確に分離されている

#### 文章のマークアップ方法説明
- MainProvision以下、「編」は「Part」で記述、「Part」の中で「Article」が必要になるので、空の「Article」を記述し、「Article」内に「Paragraph」を配置
- 以降の階層として「番号+項目名+文章」の場合は「Item」の中に空の「ItemSentence」、「Sentence」を記述し、その後に「List」で記述（パターン3と同様）
- さらに階層が深くなる場合は「Subitem1」で記述

#### 文章のパターン例
```
告示文

第１編　項目名

1　項目名
テキスト

2　項目名
テキスト
一　テキスト
二　テキスト

```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Part Num="1">
    <PartTitle>第１編　項目名</PartTitle>
    <Article Num="1">
      <ArticleTitle></ArticleTitle>
      <Paragraph Num="1">
        <ParagraphNum>1</ParagraphNum>
        <ParagraphSentence>
          <Sentence>項目名</Sentence>
        </ParagraphSentence>
        <Item Num="1">
          <ItemTitle></ItemTitle>
          <ItemSentence>
            <Sentence></Sentence>
          </ItemSentence>
          <List>
            <ListSentence>
              <Sentence Num="1" >テキスト</Sentence>
            </ListSentence>
          </List>
        </Item>
      <Paragraph Num="2">
        <ParagraphNum>2</ParagraphNum>
        <ParagraphSentence>
          <Sentence>項目名</Sentence>
        </ParagraphSentence>
        <Item Num="1">
          <ItemTitle></ItemTitle>
          <ItemSentence>
            <Sentence></Sentence>
          </ItemSentence>
          <List>
            <ListSentence>
              <Sentence Num="1" >テキスト</Sentence>
            </ListSentence>
          </List>
        </Item>
        <Item Num="2">
          <ItemTitle></ItemTitle>
          <ItemSentence>
            <Sentence></Sentence>
          </ItemSentence>
         <Subitem1 Num="1">
            <Subitem1Title>一</Subitem1Title>
            <Subitem1Sentence>
              <Sentence>テキスト</Sentence>
            </Subitem1Sentence>
	        </Subitem1>	
        	<Subitem1 Num="1">
            <Subitem1Title>二</Subitem1Title>
            <Subitem1Sentence>
              <Sentence>テキスト</Sentence>
            </Subitem1Sentence>
         	</Subitem1>
        </Item>
      </Paragraph>
    </Article>
  </Part>
</MainProvision>
```

### パターン6：第1条+項目階層型告示

#### 文章のパターン概要
- 第1ではじまり、文頭数字+項目名があり、1、(1)…と階層化するパターン
- 「第1条」→「項（番号+項目名）」→「号（項目詳細）」の階層構造
- 条文形式でありながら項目の詳細展開を持つ形式
- 各階層で番号と内容が明確に分離されている

#### 文章のマークアップ方法説明
- MainProvision以下、「第1」を「Article」で記述し、第1の「項目名」を「Paragraph」で記述
- 以降は「Item」の中に「番号」を「ItemTitle」、「項目」を「ItemSentence」で記述し、「文章」を「List」で記述
- さらに階層が深くなる場合には「Item」の中に「Subitem1」を記述し、「番号」を「Subitem1Title」、「文章」を「Subitem1Sentence」で記述

#### 文章のパターン例
```
告示文

第1　項目名

1　項目名
テキスト

2　項目名
テキスト
(1)　テキスト
(2)　テキスト
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Article Num="1">
    <ArticleTitle>第1</ArticleTitle>
    <Paragraph Num="1">
      <ParagraphNum></ParagraphNum>
      <ParagraphSentence>
        <Sentence>項目名</Sentence>
      </ParagraphSentence>
      <Item Num="1">
        <ItemTitle>1</ItemTitle>
        <ItemSentence>
          <Sentence>項目名</Sentence>
        </ItemSentence>
        <List>
          <ListSentence>
            <Sentence>テキスト</Sentence>
          </ListSentence>
        </List>
      </Item>
      <Item Num="2">
        <ItemTitle>2</ItemTitle>
        <ItemSentence>
          <Sentence>項目名</Sentence>
        </ItemSentence>
        <List>
          <ListSentence>
            <Sentence>テキスト</Sentence>
          </ListSentence>
        </List>
      </Item>
      <Item Num="3">
        <ItemTitle></ItemTitle>
        <ItemSentence>
          <Sentence></Sentence>
        </ItemSentence>
        <Subitem1 Num="1">
          <Subitem1Title>(1)</Subitem1Title>
          <Subitem1Sentence>
            <Sentence>テキスト</Sentence>
          </Subitem1Sentence>
        </Subitem1>
        <Subitem1 Num="2">
          <Subitem1Title>(2)</Subitem1Title>
          <Subitem1Sentence>
            <Sentence>テキスト</Sentence>
          </Subitem1Sentence>
        </Subitem1>
      </Item>
    </Paragraph>
  </Article>
</MainProvision>
```

### パターン7：文頭数字+項目階層型告示

#### 文章のパターン概要
- 文頭番号+項目名があり、階層化するパターン
- 番号付き項目から詳細項目へと段階的に展開する形式
- 各階層で番号と内容が明確に分離されている
- 様々な番号体系（１、(1)、(a)、(A)、一、一、、1.1.1、イ、ア等）に対応

#### 文章のマークアップ方法説明
- MainProvision以下、最上位項目を「Paragraph」で記述し、「番号」「項目」をそれぞれ「ParagraphNum」「Sentence」で記述
- 下位項目を「Item」で記述し、「番号」「項目」をそれぞれ「ItemTitle」「Sentence」で記述
- その後の文章をパターン3と同様に「List」で記述
- 番号体系は文書に応じて柔軟に対応

#### 文章のパターン例
```
告示文

1　項目名

(1)　項目名
テキスト

(2)　項目名
テキスト
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum>1</ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle>(1)</ItemTitle>
      <ItemSentence>
        <Sentence>項目名</Sentence>
      </ItemSentence>
      <List>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
      </List>
    </Item>
    <Item Num="2">
      <ItemTitle>(2)</ItemTitle>
      <ItemSentence>
        <Sentence>項目名</Sentence>
      </ItemSentence>
      <List>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
      </List>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン7-2：多層文頭数字+項目階層型告示

#### 文章のパターン概要
- 番号+項目名からはじまり、下層にも異なる番号体系で階層化するパターン
- 複数の階層で様々な番号体系（１、(1)、(a)、(A)、一、一、、1.1.1、イ、ア等）を使用する複雑な構造
- 各階層で番号と内容が明確に分離されている
- 階層ごとに異なる番号体系を使い分ける多層階層構造

#### 文章のマークアップ方法説明
- MainProvision以下、「Paragraph」で記述し、最上位の「番号」を「ParagraphNum」、「項目名」を「ParagraphSentence」「Sentence」で記述
- 下層を「Item」で記述し、「番号」（様々な番号体系に対応）を「ItemTitle」、「項目名」または「テキスト」を「ItemSentence」「Sentence」で記述
- リスト形式のテキストは「List」「ListSentence」「Sentence」で記述
- さらに下層がある場合は「Subitem1」「Subitem2」等で記述し、「番号」を各「Title」、「テキスト」を各「Sentence」で記述
- 番号体系は文書に応じて柔軟に対応（１、(1)、(a)、(A)、一、一、、1.1.1、イ、ア等）

#### 文章のパターン例
```
告示文

一、　項目名
(A)　項目名
テキスト

二、　項目名
1. テキスト
2. テキスト

三、　項目名
(A)　項目名
(1)　テキスト
(2)　テキスト


```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum>一、</ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle>(A)</ItemTitle>
      <ItemSentence>
        <Sentence>項目名</Sentence>
      </ItemSentence>
      <List>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
      </List>
    </Item>
  </Paragraph>
  <Paragraph Num="2">
    <ParagraphNum>二、</ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle>1.</ItemTitle>
      <ItemSentence>
        <Sentence>テキスト</Sentence>
      </ItemSentence>
    </Item>
    <Item Num="2">
      <ItemTitle>2.</ItemTitle>
      <ItemSentence>
        <Sentence>テキスト</Sentence>
      </ItemSentence>
    </Item>
  </Paragraph>
  <Paragraph Num="3">
    <ParagraphNum>三、</ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle>(A)</ItemTitle>
      <ItemSentence>
        <Sentence>項目名</Sentence>
      </ItemSentence>
      <Subitem1 Num="1">
        <Subitem1Title>(1)</Subitem1Title>
        <Subitem1Sentence>
          <Sentence>テキスト</Sentence>
        </Subitem1Sentence>
      </Subitem1>
      <Subitem1 Num="2">
        <Subitem1Title>(2)</Subitem1Title>
        <Subitem1Sentence>
          <Sentence>テキスト</Sentence>
        </Subitem1Sentence>
      </Subitem1>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン7-3D：番号なし項目階層型告示

#### 文章のパターン概要
- 文頭数字がない項目名からはじまり、下層にも文頭数字がない項目名が続き、その下層には文頭数字があるパターン
- 「項目名」→「項目名」→「番号+項目名」の階層構造
- 上位階層では番号なし、下位階層で番号ありという特殊な構造
- 各階層で番号の有無と内容が明確に分離されている

#### 文章のマークアップ方法説明
- MainProvision以下、「Paragraph」の中に空の「ParagraphNum」を記述し、冒頭の「項目名」は「ParagraphSentence」「Sentence」で記述
- 下層は「Item」で記述し、「項目名」を「ItemSentence」「Sentence」で記述
- さらに下層を「Item」で記述し、「文頭数字」を「ItemTitle」、「項目名」を「ItemSentence」「Sentence」で記述
- 番号体系は文書に応じて柔軟に対応

#### 文章のパターン例
```
告示文

項目名

項目名

1　項目名
2　項目名
3　項目名
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle></ItemTitle>
      <ItemSentence>
        <Sentence>項目名</Sentence>
      </ItemSentence>
      <Subitem1 Num="1">
        <Subitem1Title>1</Subitem1Title>
        <Subitem1Sentence>
          <Sentence>項目名</Sentence>
        </Subitem1Sentence>
      </Subitem1>
      <Subitem1 Num="2">
        <Subitem1Title>2</Subitem1Title>
        <Subitem1Sentence>
          <Sentence>項目名</Sentence>
        </Subitem1Sentence>
      </Subitem1>
      <Subitem1 Num="3">
        <Subitem1Title>3</Subitem1Title>
        <Subitem1Sentence>
          <Sentence>項目名</Sentence>
        </Subitem1Sentence>
      </Subitem1>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン8：前文+条文階層型告示

#### 文章のパターン概要
- 文頭に番号のない文章（またはタイトル+文章）があり、その後に第1、1…と階層化するパターン
- 「前文」→「第1条」→「項目」の階層構造
- 前文部分と本則部分が明確に分離された構造
- 条文形式でありながら前文を持つ特殊な形式

#### 文章のマークアップ方法説明
- 「第1」より前の文章を「前文」として、「Preamble」内に「Paragraph」を用いて記述
- 「第1」以降は「MainProvision」として、「第1」を「Article」の「ArticleTitle」、「項目」は「Article」の中に「Paragraph」「ParagraphSentence」「Sentence」で記述
- 次の階層は「Paragraph」内に「Item」を記述し、番号は「ItemTitle」、文章は「ItemSentence」「Sentence」で記述
- 番号体系は文書に応じて柔軟に対応

#### 文章のパターン例
```
告示文

テキスト

第1　項目名

1　テキスト
2　テキスト
3　テキスト
```

#### 文章のマークアップ例
```xml
<Law Era="昭和" Year="26" Num="203" PromulgateMonth="8" PromulgateDay="28" LawType="Notice" Lang="ja">
  <LawNum>告示番号</LawNum>
  <LawTitle>告示名</LawTitle>
  <LawBody>
    <Preamble>
      <Paragraph Num="1">
        <ParagraphNum></ParagraphNum>
        <ParagraphSentence>
          <Sentence>テキスト</Sentence>
        </ParagraphSentence>
      </Paragraph>
    </Preamble>
    <MainProvision>
      <Article Num="1">
        <ArticleTitle>第1</ArticleTitle>
        <Paragraph Num="1">
          <ParagraphNum></ParagraphNum>
          <ParagraphSentence>
            <Sentence>項目名</Sentence>
          </ParagraphSentence>
          <Item Num="1">
            <ItemTitle>1</ItemTitle>
            <ItemSentence>
              <Sentence>テキスト</Sentence>
            </ItemSentence>
          </Item>
          <Item Num="2">
            <ItemTitle>2</ItemTitle>
            <ItemSentence>
              <Sentence>テキスト</Sentence>
            </ItemSentence>
          </Item>
          <Item Num="3">
            <ItemTitle>3</ItemTitle>
            <ItemSentence>
              <Sentence>テキスト</Sentence>
            </ItemSentence>
          </Item>
        </Paragraph>
      </Article>
    </MainProvision>
  </LawBody>
</Law>
```

### パターン9：表組中心型告示

#### 文章のパターン概要
- 本文がいきなり表組のパターン
- 前文や項目番号なしで、告示文の直後に表が配置される
- 表が告示の主要な内容を構成する形式
- 最もシンプルな構造で、表のみで情報を伝達

#### 文章のマークアップ方法説明
- 「MainProvision」以下に、空の「Paragraph」、「ParagraphNum」、「ParagraphSentence」、「Sentence」を記述し、「Paragraph」の中に「TableStruct」で表組を記述
- 表の内容は「Table」要素内に適切にマークアップ
- 表以外の説明文等がある場合は、適切な階層に配置

#### 文章のパターン例
```
告示文

[表組]
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence></Sentence>
    </ParagraphSentence>
    <TableStruct>
      <Table>
        <!-- 表の内容 -->
      </Table>
    </TableStruct>
  </Paragraph>
</MainProvision>
```

### パターン9-2D：表組+図併用型告示

#### 文章のパターン概要
- 本文がいきなり表組で、その後に図があるパターン
- 前文や項目番号なしで、告示文の直後に表と図が順次配置される
- 表と図の両方で情報を伝達する複合型の形式
- 視覚的な情報（表+図）で内容を完結に表現

#### 文章のマークアップ方法説明
- 「MainProvision」以下に、空の「Paragraph」、「ParagraphNum」、「ParagraphSentence」、「Sentence」を記述し、「Paragraph」の中に「TableStruct」「Table」で表組を記述、同じく「Paragraph」内に「FigStruct」「Fig」で図を記述
- 表と図は同一のParagraph内に順次配置
- 表と図以外の説明文等がある場合は、適切な階層に配置

#### 文章のパターン例
```
告示文

[表組]

[図]
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence></Sentence>
    </ParagraphSentence>
    <TableStruct>
      <Table>
        <!-- 表の内容 -->
      </Table>
    </TableStruct>
    <FigStruct>
      <Fig src="図のパス"/>
    </FigStruct>
  </Paragraph>
</MainProvision>
```

### パターン9-3D：表形式推奨型告示

#### 文章のパターン概要
- 表組ではないが、表形式で記述すると良いパターン
- 縦書きの項目列挙形式だが、構造的に表として整理すべき内容
- 判断が難しく、自動化は困難な特殊ケース
- 人間の判断により表構造への変換を推奨する形式

#### 文章のマークアップ方法説明
- 「MainProvision」以下に、空の「Paragraph」、「ParagraphNum」、「ParagraphSentence」、「Sentence」を記述し、「Paragraph」の中に「TableStruct」「Table」で表組を記述
- 元の縦書き項目列挙を表形式に構造化して記述
- 表への変換は人間の判断に基づいて実施
- 自動化による判定は困難なため、手動での構造化が必要

#### 文章のパターン例
```
告示文

[縦書き項目列挙（表形式で記述推奨）]
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence></Sentence>
    </ParagraphSentence>
    <TableStruct>
      <Table>
        <!-- 表形式に構造化した内容 -->
      </Table>
    </TableStruct>
  </Paragraph>
</MainProvision>
```

#### 注意事項
- このパターンは自動判定が困難なため、Claude Desktopでの自動変換には含めない
- 人間による内容確認と判断が必要
- 表形式への変換可否は文書の内容と構造を総合的に判断

### パターン10：告示文単独型告示

#### 文章のパターン概要
- 告示文のみで終了するパターン
- 本文に項目、表、図等の追加要素を持たない
- 最もシンプルな告示構造
- 告示文だけで内容が完結する形式

#### 文章のマークアップ方法説明
- 「MainProvision」以下に、空の「Paragraph」「ParagraphNum」「ParagraphSentence」「Sentence」を記述
- 追加の要素（Item、TableStruct、FigStruct等）は含まない
- 最小限の構造で告示を表現

#### 文章のパターン例
```
告示文
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence></Sentence>
    </ParagraphSentence>
  </Paragraph>
</MainProvision>
```

### パターン11：目次+章構造型告示

#### 文章のパターン概要
- 目次が含まれ、章があるパターン
- 告示文の後に目次、その後に章立ての本文が続く構造
- 大規模な告示で使用される正式な文書構造
- TOC（目次）とChapter（章）の階層構造を持つ

#### 文章のマークアップ方法説明
- 「LawBody」以下に、「目次」を「TOC」で記述、次に「MainProvision」以下に、「章」を「Chapter」「ChapterTitle」で記述、「Chapter」内に空の「Article」をいれ、「Article」内に「Paragraph」を記述、「文頭番号」を「ParagraphNum」、「項目名」を「Sentence」で記述し、「文章」を「Item」「ItemSentence」「Sentence」で記述
- TOCでは各章を「TOCChapter」と「ChapterTitle」で記述
- MainProvisionでは各章を「Chapter」と「ChapterTitle」で構造化
- 章内の内容は Article → Paragraph → Item の階層で記述

#### 文章のパターン例
```
告示文

目次
第1章　項目名
第2章　項目名
第3章　項目名
第4章　項目名
第5章　項目名
第6章　項目名

第1章　項目名

1　項目名
　テキスト
```

#### 文章のマークアップ例
```xml
<LawBody>
  <TOC>
    <TOCChapter Num="1">
      <ChapterTitle>第1章　項目名</ChapterTitle>
    </TOCChapter>
    <TOCChapter Num="2">
      <ChapterTitle>第2章　項目名</ChapterTitle>
    </TOCChapter>
    <TOCChapter Num="3">
      <ChapterTitle>第3章　項目名</ChapterTitle>
    </TOCChapter>
    <TOCChapter Num="4">
      <ChapterTitle>第4章　項目名</ChapterTitle>
    </TOCChapter>
    <TOCChapter Num="5">
      <ChapterTitle>第5章　項目名</ChapterTitle>
    </TOCChapter>
    <TOCChapter Num="6">
      <ChapterTitle>第6章　項目名</ChapterTitle>
    </TOCChapter>
  </TOC>
  <MainProvision>
    <Chapter Num="1">
      <ChapterTitle>第1章　項目名</ChapterTitle>
      <Article Num="1">
        <ArticleTitle></ArticleTitle>
        <Paragraph Num="1">
          <ParagraphNum>1</ParagraphNum>
          <ParagraphSentence>
            <Sentence>項目名</Sentence>
          </ParagraphSentence>
          <Item Num="1">
            <ItemTitle></ItemTitle>
            <ItemSentence>
              <Sentence>テキスト</Sentence>
            </ItemSentence>
          </Item>
        </Paragraph>
      </Article>
    </Chapter>
  </MainProvision>
</LawBody>
```

### パターン11-2D：目次+章+条文階層型告示

#### 文章のパターン概要
- 目次が第建てで、本則が条建てのパターン
- 目次では章立て、本則では条文による構造化
- TOC（目次）+ MainProvision（本則）の二重管理で、章と条の混合構造
- 大規模告示で章と条を組み合わせた正式な文書構造

#### 文章のマークアップ方法説明
- 第建ての目次を「章」と看做す場合、「LawBody」以下に「目次」を「TOC」で記述、次に「MainProvision」以下に、「第1」を「Chapter」「ChapterTitle」で記述、「Chapter」内に「Article」を記述し、条建ての内容を「Article」内に「Paragraph」を記述、文頭番号がある内容は「Item」で記述し、「文頭番号」を「ItemTitle」、「文章」を「ItemSentence」「Sentence」で記述

#### 文章のパターン例
```
告示文

目次
第1章　項目名
第2章　項目名

第1章　項目名

番号　項目名

1　テキスト
```

#### 文章のマークアップ例
```xml
<LawBody>
  <TOC>
    <TOCChapter Num="1">
      <ChapterTitle>第1章　項目名</ChapterTitle>
    </TOCChapter>
    <TOCChapter Num="2">
      <ChapterTitle>第2章　項目名</ChapterTitle>
    </TOCChapter>
  </TOC>
  <MainProvision>
    <Chapter Num="1">
      <ChapterTitle>第1章　項目名</ChapterTitle>
      <Article Num="1">
        <ArticleTitle>番号</ArticleTitle>
        <Paragraph Num="1">
          <ParagraphNum></ParagraphNum>
          <ParagraphSentence>
            <Sentence>項目名</Sentence>
          </ParagraphSentence>
          <Item Num="1">
            <ItemTitle>1</ItemTitle>
            <ItemSentence>
              <Sentence>テキスト</Sentence>
            </ItemSentence>
          </Item>
        </Paragraph>
      </Article>
    </Chapter>
  </MainProvision>
</LawBody>
```

### パターン12：番号なしリスト型告示

#### 文章のパターン概要
- 番号のないリストのみのパターン
- 項目番号や階層構造を持たず、単純なリスト形式
- List要素を使用した最もシンプルなリスト構造
- 列挙型の告示で番号付けが不要な場合に使用

#### 文章のマークアップ方法説明
- 「MainProvision」以下に、空の「Paragraph」、「ParagraphNum」「ParagraphSentence」「Sentence」を記述し、「Item」「ItemSentence」「Sentence」を記述し、「Item」の中に「List」として記述

#### 文章のパターン例
```
告示文

テキスト
テキスト
テキスト
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence></Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle></ItemTitle>
      <ItemSentence>
        <Sentence></Sentence>
      </ItemSentence>
      <List>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
      </List>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン13：第1条+文頭文字階層型告示

#### 文章のパターン概要
- 第1ではじまり、文頭数字や文頭文字（イロハ）があるパターン
- 条文形式から項目階層への展開構造
- Article → Paragraph → Item の基本階層
- 条文ベースでありながら文字による細分化を持つ形式

#### 文章のマークアップ方法説明
- 「MainProvision」以下、「第一」を「Article」の「ArticleTitle」で記述し、「文章」は「Article」の中に「Paragraph」「ParagraphSentence」「Sentence」で記述、次の階層は「Paragraph」内に「Item」を記述し、番号（文字）は「ItemTitle」、文章は「ItemSentence」「Sentence」で記述

#### 文章のパターン例
```
告示文

第一　項目名

イ　テキスト
ロ　テキスト
ハ　テキスト
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Article Num="1">
    <ArticleTitle>第一</ArticleTitle>
    <Paragraph Num="1">
      <ParagraphNum></ParagraphNum>
      <ParagraphSentence>
        <Sentence>項目名</Sentence>
      </ParagraphSentence>
      <Item Num="1">
        <ItemTitle>イ</ItemTitle>
        <ItemSentence>
          <Sentence>テキスト</Sentence>
        </ItemSentence>
      </Item>
      <Item Num="2">
        <ItemTitle>ロ</ItemTitle>
        <ItemSentence>
          <Sentence>テキスト</Sentence>
        </ItemSentence>
      </Item>
      <Item Num="3">
        <ItemTitle>ハ</ItemTitle>
        <ItemSentence>
          <Sentence>テキスト</Sentence>
        </ItemSentence>
      </Item>
    </Paragraph>
  </Article>
</MainProvision>
```

### パターン14：図単独型告示

#### 文章のパターン概要
- 本文がいきなり図（様式）のパターン
- 告示文の直後に図のみが配置される構造
- 最もシンプルな図中心の告示形式
- 様式や図面を主体とする告示に使用

#### 文章のマークアップ方法説明
- 「MainProvision」以下に、空の「Paragraph」「ParagraphNum」「ParagraphSentence」「Sentence」を記述し、「Paragraph」の中に「FigStruct」「Fig」で図（様式）を記述

#### 文章のパターン例
```
告示文

[図]
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence></Sentence>
    </ParagraphSentence>
    <FigStruct>
      <Fig src="図のパス"/>
    </FigStruct>
  </Paragraph>
</MainProvision>
```

### パターン14-2D：図+タイトル型告示

#### 文章のパターン概要
- 本文がいきなり図（様式）ではじまり、図のタイトルがあるパターン
- 図にタイトルが付与された構造
- FigStructTitle要素を使用した図の構造化
- タイトル付きの図面や様式を含む告示

#### 文章のマークアップ方法説明
- 「MainProvision」以下に、空の「Paragraph」「ParagraphNum」「ParagraphSentence」「Sentence」を記述し、「Paragraph」の中に「FigStruct」を記述、図のタイトルを「FigStructTitle」で記述し、図を「Fig」で記述

#### 文章のパターン例
```
告示文

項目名

[図]
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence></Sentence>
    </ParagraphSentence>
    <FigStruct>
      <FigStructTitle>項目名</FigStructTitle>
      <Fig src="図のパス"/>
    </FigStruct>
  </Paragraph>
</MainProvision>
```

### パターン14-3D：前文+図+タイトル型告示

#### 文章のパターン概要
- 冒頭に文章（タイトル）があり、タイトルがついた図があるパターン
- 前文 → 図タイトル → 図の構造
- 説明文と図の組み合わせ構造
- 図面に説明が必要な告示に使用

#### 文章のマークアップ方法説明
- 「MainProvision」以下に、空の「Paragraph」「ParagraphNum」「ParagraphSentence」「Sentence」を記述し、「Paragraph」の中に「FigStruct」を記述、図のタイトルを「FigStructTitle」で記述し、図を「Fig」で記述

#### 文章のパターン例
```
告示文

テキスト

項目名

[図]
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>テキスト</Sentence>
    </ParagraphSentence>
    <FigStruct>
      <FigStructTitle>項目名</FigStructTitle>
      <Fig src="図のパス"/>
    </FigStruct>
  </Paragraph>
</MainProvision>
```

### パターン15：前文+項目+表階層型告示

#### 文章のパターン概要
- 冒頭が文章ではじまり、その下層に文頭数字+項目名のあとに表があるパターン
- 前文 → 項目 → 表の階層構造
- 項目説明と表を組み合わせた複合構造
- 詳細な説明と表による情報提供を併用する告示

#### 文章のマークアップ方法説明
- 「MainProvision」以下、「冒頭の文章」を「Paragraph」「ParagraphSentence」「Sentence」で記述、下層を「Item」で記述し、「文頭番号」を「ItemTitle」、「項目名」を「ItemSentence」「Sentence」で記述、「Item」の中に「TableStruct」をいれて、「表」を「Table」で記述、さらに下層にも「表」がある場合には、下層部分を「Subitem1」で記述し、「Subitem1」の中に「TableStruct」「Table」で記述

#### 文章のパターン例
```
告示文

テキスト

一　項目名

[表]

二　項目名

[表]
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>テキスト</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle>一</ItemTitle>
      <ItemSentence>
        <Sentence>項目名</Sentence>
      </ItemSentence>
      <TableStruct>
        <Table>
          <!-- 表の内容 -->
        </Table>
      </TableStruct>
    </Item>
    <Item Num="2">
      <ItemTitle>二</ItemTitle>
      <ItemSentence>
        <Sentence>項目名</Sentence>
      </ItemSentence>
      <TableStruct>
        <Table>
          <!-- 表の内容 -->
        </Table>
      </TableStruct>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン16：前文+多階層型告示

#### 文章のパターン概要
- 文頭に番号のない文章があり、その後に一、イ...と階層化するパターン
- 前文から多段階の階層展開
- Paragraph → Item → Subitem1 の深い階層構造
- 複雑な分類や細分化が必要な告示に使用

#### 文章のマークアップ方法説明
- 「MainProvision」以下、「冒頭の文章」を「Paragraph」「ParagraphSentence」「Sentence」で記述、下層を「Item」で記述し、「文頭番号」を「ItemTitle」、「文章」を「ItemSentence」「Sentence」で記述、さらにその下層を「Subitem1」で記述し、「文頭番号や文頭文字」を「Subitem1Title」で記述、「文章」を「Subitem1Sentence」「Sentence」で記述、さらに下層が続く場合は、「Subitem2」で記述

#### 文章のパターン例
```
告示文

テキスト

一　テキスト
　イ　テキスト
　ロ　テキスト

二　テキスト
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>テキスト</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle>一</ItemTitle>
      <ItemSentence>
        <Sentence>テキスト</Sentence>
      </ItemSentence>
      <Subitem1 Num="1">
        <Subitem1Title>イ</Subitem1Title>
        <Subitem1Sentence>
          <Sentence>テキスト</Sentence>
        </Subitem1Sentence>
      </Subitem1>
      <Subitem1 Num="2">
        <Subitem1Title>ロ</Subitem1Title>
        <Subitem1Sentence>
          <Sentence>テキスト</Sentence>
        </Subitem1Sentence>
      </Subitem1>
    </Item>
    <Item Num="2">
      <ItemTitle>二</ItemTitle>
      <ItemSentence>
        <Sentence>テキスト</Sentence>
      </ItemSentence>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン17：文頭数字+超階層型告示

#### 文章のパターン概要
- 冒頭に文頭数字+文章があり、その後、第一、1、(1)、と階層化するパターン
- 最も複雑な多層階層構造
- Paragraph → Item → Subitem1 の超深層構造
- 法令的な詳細分類が必要な大規模告示に使用

#### 文章のマークアップ方法説明
- 「MainProvision」以下、冒頭を「Paragraph」で記述し、「文頭数字」を「ParagraphNum」、「文章」を「ParagraphSentence」「Sentence」で記述、下層を「Item」で記述し、「文頭番号（第一）」を「ItemTitle」、「文章」を「Sentence」で記述、さらにその下層を「Subitem1」で記述し、「文頭番号や文頭文字」を「Subitem1Title」で記述、「文章」を「Subitem1Sentence」「Sentence」で記述

#### 文章のパターン例
```
告示文

一　テキスト

第一　テキスト
　1　テキスト
　　(1)　テキスト
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum>一</ParagraphNum>
    <ParagraphSentence>
      <Sentence>テキスト</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle>第一</ItemTitle>
      <ItemSentence>
        <Sentence>テキスト</Sentence>
      </ItemSentence>
      <Subitem1 Num="1">
        <Subitem1Title>1</Subitem1Title>
        <Subitem1Sentence>
          <Sentence>テキスト</Sentence>
        </Subitem1Sentence>
      </Subitem1>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン18D：階層内図挿入型告示

#### 文章のパターン概要
- 階層の中に図が入っているパターン
- 項目説明の中に図が挿入された構造
- Item内でのFigStruct配置
- 階層的説明と図解を組み合わせた告示

#### 文章のマークアップ方法説明
- 「MainProvision」以下、冒頭を「Paragraph」で記述し、「文頭番号」を「ParagraphNum」、「項目名」を「ParagraphSentence」「Sentence」で記述、下層は「Item」で記述し、「文頭番号」を「ItemTitle」、「項目名」を「ItemSentence」「Sentence」で記述、「画像」を「Item」内に「FigStruct」「Fig」で記述するが、「Item」内に「FigStruct」を記述した場合、「Item」内に下層構造をもてないため、「図以降の文章」は「List」「ListSentence」「Sentence」記述

#### 文章のパターン例
```
告示文

一　項目名

1　項目名

[図]

テキスト
テキスト
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum>一</ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle>1</ItemTitle>
      <ItemSentence>
        <Sentence>項目名</Sentence>
      </ItemSentence>
      <FigStruct>
        <Fig src="図のパス"/>
      </FigStruct>
      <List>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
      </List>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン19D：表題複数+別表階層型告示

#### 文章のパターン概要
- 表題が複数出現し、階層の中に別表が入っているパターン
- 複数の表題による段落分けと別表の組み合わせ構造
- 表題による構造化と表による詳細情報の提供
- 複雑な情報整理が必要な告示に使用

#### 文章のマークアップ方法説明
- 「MainProvision」以下、「表題」が告示中に複数出現し、「LawTitle」は使用できないため、「表題」を「Paragraph」「ParagraphSentence」「Sentence」で記述し、「表題後の文章」を「Item」「ItemSentence」「Sentence」で記述し、番号付きの内容はそれぞれ「Subitem1」「Subitem2」として記述、「別表」は本来「AppdxTable」であるが、「MainProvision」内に記述できないため、本則中の別表は「TableStruct」「Table」で記述

#### 文章のパターン例
```
告示文

表題

テキスト

一　テキスト
二　テキスト

[別表]
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>表題</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle></ItemTitle>
      <ItemSentence>
        <Sentence>テキスト</Sentence>
      </ItemSentence>
      <Subitem1 Num="1">
        <Subitem1Title>一</Subitem1Title>
        <Subitem1Sentence>
          <Sentence>テキスト</Sentence>
        </Subitem1Sentence>
      </Subitem1>
      <Subitem1 Num="2">
        <Subitem1Title>二</Subitem1Title>
        <Subitem1Sentence>
          <Sentence>テキスト</Sentence>
        </Subitem1Sentence>
      </Subitem1>
      <TableStruct>
        <Table>
          <!-- 別表の内容 -->
        </Table>
      </TableStruct>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン20D：スペース列記型告示

#### 文章のパターン概要
- スペース（空白）を使って列記しているパターン
- 番号や記号を使わず空白による項目分離
- List要素による単純な列挙構造
- 最もシンプルな項目列挙形式

#### 文章のマークアップ方法説明
- 「MainProvision」以下、空の「Paragraph」と「Item」を記述し、列記部分は「List」で記述し、「ListSentence」内に各文章を「Sentence」で記述

#### 文章のパターン例
```
告示文

表題

テキスト
テキスト
テキスト
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>表題</Sentence>
    </ParagraphSentence>
    <Item Num="1">
      <ItemTitle></ItemTitle>
      <ItemSentence>
        <Sentence></Sentence>
      </ItemSentence>
      <List>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
        <ListSentence>
          <Sentence>テキスト</Sentence>
        </ListSentence>
      </List>
    </Item>
  </Paragraph>
</MainProvision>
```

### パターン21D：表記号組み合わせ型告示

#### 文章のパターン概要
- 表に記号が用いられているパターン
- 表のヘッダーや内容に特殊記号を含む構造
- TableHeaderRow、TableRow等による詳細な表構造
- 複雑な表形式の情報を含む告示

#### 文章のマークアップ方法説明
- 「MainProvision」以下、文頭数字とタイトルを「Paragraph」で記述し、「文頭数字」は「ParagraphNum」、「タイトル」を「ParagraphSentence」「Sentence」で記述、表は「TableStruct」「Table」で記述するが、表題にある波括弧は記述できないので、表題部分を「TableHeaderRow」「TableHeaderColumn」で記述、波括弧の部分をセル結合のイメージで「colspan」属性を用いて記述、以下の「値」の部分については「TableRow」「TableColumn」「Sentence」で記述

#### 文章のパターン例
```
告示文

一　項目名

[複雑な表（記号付き）]
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphNum>一</ParagraphNum>
    <ParagraphSentence>
      <Sentence>項目名</Sentence>
    </ParagraphSentence>
    <TableStruct>
      <Table>
        <TableHeaderRow>
          <TableHeaderColumn>項目</TableHeaderColumn>
          <TableHeaderColumn>項目</TableHeaderColumn>
          <TableHeaderColumn>項目</TableHeaderColumn>
        </TableHeaderRow>
        <TableHeaderRow>
          <TableHeaderColumn>項目</TableHeaderColumn>
          <TableHeaderColumn>項目</TableHeaderColumn>
          <TableHeaderColumn>項目</TableHeaderColumn>
          <TableHeaderColumn>項目</TableHeaderColumn>
        </TableHeaderRow>
        <TableRow>
          <TableColumn>値</TableColumn>
          <TableColumn>値</TableColumn>
          <TableColumn>値</TableColumn>
          <TableColumn>値</TableColumn>
        </TableRow>
      </Table>
    </TableStruct>
  </Paragraph>
</MainProvision>
```

### パターン22D：見出し付き文章型告示

#### 文章のパターン概要
- 文章に見出しがついているパターン
- ParagraphCaption要素を使用した見出し構造
- 文章の前に説明的な見出しを持つ形式
- 内容の理解を助ける見出し付きの告示

#### 文章のマークアップ方法説明
- 「MainProvision」以下、「Paragraph」で記述し、括弧でくくられた項目名は「ParagraphCaption」で記述、「ParagraphNum」は空になるが、「文章」は「ParagraphSentence」「Sentence」で記述

#### 文章のパターン例
```
告示文

（見出し）

テキスト
```

#### 文章のマークアップ例
```xml
<MainProvision>
  <Paragraph Num="1">
    <ParagraphCaption>見出し</ParagraphCaption>
    <ParagraphNum></ParagraphNum>
    <ParagraphSentence>
      <Sentence>テキスト</Sentence>
    </ParagraphSentence>
  </Paragraph>
</MainProvision>
```


## 品質保証ガイドライン

### 1. 必須チェック項目
- XMLlintによるスキーマ検証
- 原文との内容一致確認
- 必須属性の設定確認

### 2. 推奨チェック項目
- 構造の論理的整合性
- 要素の適切な使い分け
- 空要素の適切な処理

### 3. 例外処理
- 既存パターンに該当しない場合は、最も近いパターンを基準に調整
- 特殊なケースは個別に判断し、本ポリシーの更新を検討

### 4. 階層構造チェック項目

#### 必須チェック項目
- **「次のとおり」判定**: 「次のとおりとする」「以下のとおり」「下記のとおり」等の文言の後に続く内容は、同一Item要素内に配置されているか
- **表・図の配置確認**: TableStruct、FigStructが適切な親要素の下に配置されているか
- **論理的階層**: 文章の論理構造と XML の階層構造が一致しているか

#### 推奨チェック項目
- **Item番号の連続性**: Item要素のNum属性が適切に連番になっているか
- **内容の完全性**: 「次のとおり」で予告された内容が実際に配置されているか
- **構造の一貫性**: 同様のパターンが文書内で一貫してマークアップされているか

### 5. よくある間違いと修正方法

#### 間違い例1: 表・図を独立したItem要素にしてしまう
```xml
<!-- ❌ 間違い -->
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence>...次のとおりとする。</Sentence>
  </ItemSentence>
</Item>
<Item Num="2">  <!-- 間違い：表が独立している -->
  <ItemTitle></ItemTitle>
  <ItemSentence>
    <Table>...</Table>
  </ItemSentence>
</Item>

<!-- ✅ 正しい -->
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence>...次のとおりとする。</Sentence>
  </ItemSentence>
  <TableStruct>  <!-- 正しい：同一Item内に配置 -->
    <Table>...</Table>
  </TableStruct>
</Item>
```

#### 間違い例2: 図を独立したItem要素にしてしまう
```xml
<!-- ❌ 間違い -->
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence>標章の様式は、次のとおりとする。</Sentence>
  </ItemSentence>
</Item>
<Item Num="2">  <!-- 間違い：図が独立している -->
  <ItemTitle></ItemTitle>
  <ItemSentence>
    <Sentence></Sentence>
  </ItemSentence>
  <FigStruct>
    <Fig src="hyosho.jpg"/>
  </FigStruct>
</Item>

<!-- ✅ 正しい -->
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence>標章の様式は、次のとおりとする。</Sentence>
  </ItemSentence>
  <FigStruct>  <!-- 正しい：同一Item内に配置 -->
    <Fig src="hyosho.jpg"/>
  </FigStruct>
</Item>
```

#### 間違い例3: 番号付き文章をParagraphSentence内に配置
```xml
<!-- ❌ 間違い -->
<ParagraphSentence>
  <Sentence>１　モーターボート競走に使用する...</Sentence>
</ParagraphSentence>

<!-- ✅ 正しい -->
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence>モーターボート競走に使用する...</Sentence>
  </ItemSentence>
</Item>
```

#### 判断フローチャート
```
文章に「次のとおりとする」「以下のとおり」等の文言がある
↓
YES → その後に表・図・リスト等の具体的内容がある
      ↓
      YES → 同一Item要素内にTableStruct/FigStruct/List等を配置
      ↓
      NO → 通常のItem要素として処理

NO → 通常のItem要素として処理
```

---
**更新履歴**
- 2025年8月: 初版作成

**注意**: このポリシーは告示XML作成の標準化を目的としており、継続的な改善を前提としています。
