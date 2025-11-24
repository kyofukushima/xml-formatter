# Item修正ロジック1

## 本文章のスコープ
Item特化スクリプト

前提として、Paragraph修正ロジック全ての処理済みであること

テストファイル：
test_input5_item.xml

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

## 処理１ Itemの次のList要素がcolumn要素を含まないList要素の場合
1. ItemSentence要素の下にSubitem1要素を挿入。
2. List要素をSubitem1Sentence要素の次に挿入する
3. 次のList要素の判定に移行する。
4. 次のList要素もcolumn要素を含まない場合は、続けてList要素の次に挿入する
5. Columnを含まないList要素以外に到達した場合は処理を終了（処理２の判定に移行する）

### 例１　columnを含まないList要素が複数（3つ）連続する場合
入力例
```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
        <Sentence Num="1">項目１</Sentence>
    </ItemSentence>
</Item>
<Item Num="2">
    <ItemTitle>（２）</ItemTitle>
    <ItemSentence>
        <Sentence Num="1">項目２</Sentence>
    </ItemSentence>
</Item>
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
    <List>
        <ListSentence>
            <Sentence Num="1">テキスト３</Sentence>
        </ListSentence>
    </List>
    <List>
        <ListSentence>
            <Column Num="1">
                <Sentence Num="1">（３）</Sentence>
            </Column>
            <Column Num="2">
                <Sentence Num="1">項目３</Sentence>
            </Column>
        </ListSentence>
    </List>
```
出力例
```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
        <Sentence Num="1" >項目１</Sentence>
    </ItemSentence>
</Item>
<Item Num="2">
    <ItemTitle>（２）</ItemTitle>
    <ItemSentence>
        <Sentence Num="1" >項目２</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title></Subitem1Title>
        <Subitem1Sentence>
        <Sentence Num="1" ></Sentence>
        </Subitem1Sentence>
        <List>
            <ListSentence>
                <Sentence Num="1" >テキスト１</Sentence>
            </ListSentence>
        </List>
        <List>
            <ListSentence>
                <Sentence Num="1" >テキスト２</Sentence>
            </ListSentence>
        </List>
        <List>
            <ListSentence>
                <Sentence Num="1" >テキスト３</Sentence>
            </ListSentence>
        </List>
    </Subitem1>
</Item>
<!-- 処理2に移行 -->
<List>
    <ListSentence>
        <Column Num="1">
            <Sentence Num="1">（３）</Sentence>
        </Column>
        <Column Num="2">
            <Sentence Num="1">項目３</Sentence>
        </Column>
    </ListSentence>
</List>
```


### 処理１−２ 括弧科目名（〔XXX〕）の特殊処理

#### 責任範囲と例外規定
このスクリプトは通常**Subitem1レベルまで**の変換を担当するが、
科目名（〔XXX〕）は例外として**Subitem2レベルまで**の生成を許可する。

理由: 科目名は独立した構造単位であり、特殊な階層構造が必要なため。
#### 処理フロー

**ケース1: Item内にSubitemが既に存在する場合**

1. 既存のSubitemの最深レベルを確認
2. 新しいSubitem1を作成（Num = 既存数 + 1）
3. その新Subitem1内に、**Subitem2を作成**
4. Subitem2のSentenceに科目名を設定

理由: 科目名は独立した構造単位であり、既存Subitem1と並列にすべき

**ケース2: Item内にSubitemが存在しない場合**

1. Subitem1を作成（Num = 1）
2. Subitem1のSentenceに科目名を設定
3. Subitem2は作成しない（不要）

##### 例1 元々のItem要素が、Subitem1要素を含む場合
入力:
- Item（Subitem1が1個ある）
- 科目名List「〔項目2〕」

処理:
1. 新しいSubitem1を作成（Num=2）← 既存Subitem1と並列
2. 新Subitem1内にSubitem2を作成（Num=1）← 科目名専用の階層
3. Subitem2のSentenceに「〔項目2〕」を設定

結果構造:
```
Item
├── Subitem1 (Num=1) ← 既存
│   └── List（テキスト1〜3）
└── Subitem1 (Num=2) ← 新規
    └── Subitem2 (Num=1) ← 科目名専用
        └── Sentence「〔項目2〕」
```

入力例
```xml
<Item Num="2">
    <ItemTitle>（1）</ItemTitle>
    <ItemSentence>
        <Sentence Num="1" >項目1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title></Subitem1Title>
        <Subitem1Sentence>
        <Sentence Num="1" ></Sentence>
        </Subitem1Sentence>
        <List>
            <ListSentence>
                <Sentence Num="1" >テキスト１</Sentence>
            </ListSentence>
        </List>
        <List>
            <ListSentence>
                <Sentence Num="1" >テキスト２</Sentence>
            </ListSentence>
        </List>
        <List>
            <ListSentence>
                <Sentence Num="1" >テキスト３</Sentence>
            </ListSentence>
        </List>
    </Subitem1>
</Item>
<List>
    <ListSentence>
    <Sentence Num="1">〔項目2〕</Sentence>
    </ListSentence>
</List>
```
出力例
```xml
<Item Num="2">
    <ItemTitle>（1）</ItemTitle>
    <ItemSentence>
        <Sentence Num="1" >項目1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title></Subitem1Title>
        <Subitem1Sentence>
        <Sentence Num="1" ></Sentence>
        </Subitem1Sentence>
        <List>
            <ListSentence>
                <Sentence Num="1" >テキスト１</Sentence>
            </ListSentence>
        </List>
        <List>
            <ListSentence>
                <Sentence Num="1" >テキスト２</Sentence>
            </ListSentence>
        </List>
        <List>
            <ListSentence>
                <Sentence Num="1" >テキスト３</Sentence>
            </ListSentence>
        </List>
    </Subitem1>
    <Subitem1 Num="2">
        <Subitem1Title></Subitem1Title>
        <Subitem1Sentence>
            <Sentence Num="1"></Sentence>
        </Subitem1Sentence>
        <Subitem2 Num="1">
        <Subitem2Title></Subitem2Title>
        <Subitem2Sentence>
            <Sentence Num="1">〔項目2〕</Sentence>
        </Subitem2Sentence>
        </Subitem2>
    </Subitem1>
</Item>
```
##### 例2 元々のItem要素が、Subitem1要素を含んでいない場合
入力例
```xml
<Item Num="2">
    <ItemTitle>１</ItemTitle>
    <ItemSentence>
        <Sentence Num="1" >項目1</Sentence>
    </ItemSentence>
</Item>
<List>
    <ListSentence>
    <Sentence Num="1">〔項目2〕</Sentence>
    </ListSentence>
</List>
```
出力例
```xml
<Item Num="2">
    <ItemTitle>１</ItemTitle>
    <ItemSentence>
        <Sentence Num="1" >項目1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title></Subitem1Title>
        <Subitem1Sentence>
            <Sentence Num="1" >〔項目2〕</Sentence>
        </Subitem1Sentence>
    </Subitem1>
</Item>
```

## 処理２ Itemの次のList要素が、Columnが2つあり、ラベルとテキストの構成である場合

### 処理２−１ より深い階層のColumn付きList処理

#### 責任範囲
このスクリプトは**Subitem1レベルまで**の変換を担当する。
- 対象: カタカナ（階層3）のラベル
- Subitem2以降（階層4以上）は次の専用スクリプトで処理

#### 処理フロー

1. ItemTitleの階層レベルを取得（空の場合は親要素から）
2. 連続するColumn付きList要素を順次確認
3. ラベルの階層レベルを判定：

   a. **階層差が1の場合**（例: 括弧数字→カタカナ）
      - 同じ階層レベルのListを全て収集
      - Subitem1要素に変換
      - ItemSentenceの直後に挿入
   
   b. **階層差が2以上の場合**（例: 括弧数字→括弧カタカナ）
      - Listのまま保持
      - **直前に作成したSubitem1の末尾に追加**
      - 後続のSubitem2特化スクリプトで処理

4. 処理を継続し、同じ階層レベルのListを全て変換


#### 階層判定ロジック

List要素の階層レベルとの比較対象を以下の順序で決定：

1. **ItemTitleとの比較**
   - 同じ階層 → Item分割（処理２−２）
   - より深い階層 → Step 2へ
   
2. **比較対象の決定**
   - Item内に既存Subitem1がある → 最後のSubitem1Titleを使用
   - Item内にSubitem1がない → ItemTitleを使用

3. **親要素との比較**
   - 同じ階層 → Subitem1に変換
   - より深い階層（差1） → Listのまま最後のSubitem1内に追加
   - より深い階層（差2以上） → Listのまま最後のSubitem1内に追加

#### 階層判定表

| ItemTitle | 既存Subitem1 | List階層 | 比較対象 | 判定 | 処理 |
|-----------|-------------|---------|---------|------|------|
| （１）階層2 | なし | ア 階層3 | ItemTitle | 階層差1 | ✅ Subitem1変換 |
| （１）階層2 | なし | （ア）階層4 | ItemTitle | 階層差2 | ❌ List保持 |
| （１）階層2 | ア 階層3 | イ 階層3 | 最後のSubitem1 | 同じ | ✅ Subitem1変換 |
| （１）階層2 | ア 階層3 | （ア）階層4 | 最後のSubitem1 | 階層差1 | ❌ List保持 |
| （１）階層2 | - | （２）階層2 | ItemTitle | 同じ | 🔄 Item分割 |




#### 例1 ItemTitleが空である
##### 例1-1 column要素が複数あるList要素が1つ連続する
入力例

```xml
<Item Num="1">
    <ItemTitle></ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
</Item>
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">ア</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名2</Sentence>
    </Column>
    </ListSentence>
</List>
```

出力例

```xml
<Item Num="1">
    <ItemTitle></ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title>ア</Subitem1Title>
        <Subitem1Sentence>
            <Sentence  Num="1">項目名2</Sentence>
        </Subitem1Sentence>
    </Subitem1>
</Item>
```

##### 例1-2 column要素が複数あるList要素が2つ連続する
入力例

```xml
<Item Num="1">
    <ItemTitle></ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
</Item>
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">ア</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名2</Sentence>
    </Column>
    </ListSentence>
</List>
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">イ</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名3</Sentence>
    </Column>
    </ListSentence>
</List>
```

出力例

```xml
<Item Num="1">
    <ItemTitle></ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title>ア</Subitem1Title>
        <Subitem1Sentence>
            <Sentence  Num="1">項目名2</Sentence>
        </Subitem1Sentence>
    </Subitem1>
    <Subitem1 Num="2">
        <Subitem1Title>イ</Subitem1Title>
        <Subitem1Sentence>
            <Sentence  Num="1">項目名3</Sentence>
        </Subitem1Sentence>
    </Subitem1>
</Item>
```
##### 例1-3 column要素が複数あるList要素（項目ラベルが同じレベル）が2つ連続する
入力例

```xml
<Item Num="1">
    <ItemTitle></ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
</Item>
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">ア</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名2</Sentence>
    </Column>
    </ListSentence>
</List>
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">イ</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名3</Sentence>
    </Column>
    </ListSentence>
</List>
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">（ア）</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名4</Sentence>
    </Column>
    </ListSentence>
</List>

```

出力例

```xml
<Item Num="1">
    <ItemTitle></ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title>ア</Subitem1Title>
        <Subitem1Sentence>
            <Sentence  Num="1">項目名2</Sentence>
        </Subitem1Sentence>
    </Subitem1>
    <Subitem1 Num="2">
        <Subitem1Title>イ</Subitem1Title>
        <Subitem1Sentence>
            <Sentence  Num="1">項目名3</Sentence>
        </Subitem1Sentence>
        <List>
            <ListSentence>
                <Column Num="1">
                    <Sentence Num="1">（ア）</Sentence>
                </Column>
                <Column Num="2">
                    <Sentence Num="1">項目名4</Sentence>
                </Column>
            </ListSentence>
        </List>
    </Subitem1>
</Item>
```
**注記**: 
- 「（ア）」は階層4のため、このスクリプトでは変換しない
- Listのまま直前のSubitem1（イ）内に保持
- 次のスクリプト（convert_subitem1_to_subitem2.py）で処理される

#### 例2 ItemTitleがColumnの1つ目の階層レベルがより深い
##### 例2-1 column要素が複数あるList要素が1つ連続する
入力例

```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
</Item>
<List>
    <ListSentence>
        <Column Num="1">
            <Sentence Num="1">ア</Sentence>
        </Column>
        <Column Num="2">
            <Sentence Num="1">項目名2</Sentence>
        </Column>
    </ListSentence>
</List>
```

出力例

```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title>ア</Subitem1Title>
        <Subitem1Sentence>
            <Sentence  Num="1">項目名2</Sentence>
        </Subitem1Sentence>
    </Subitem1>
</Item>
```

##### 例2-2 column要素が複数あるList要素が2つ連続する
入力例

```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
</Item>
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">ア</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名2</Sentence>
    </Column>
    </ListSentence>
</List>
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">イ</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名3</Sentence>
    </Column>
    </ListSentence>
</List>
```

出力例

```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title>ア</Subitem1Title>
        <Subitem1Sentence>
            <Sentence  Num="1">項目名2</Sentence>
        </Subitem1Sentence>
    </Subitem1>
    <Subitem1 Num="2">
        <Subitem1Title>イ</Subitem1Title>
        <Subitem1Sentence>
            <Sentence  Num="1">項目名3</Sentence>
        </Subitem1Sentence>
    </Subitem1>
</Item>
```
##### 例2-3 column要素が複数あるList要素（項目ラベルが同じレベル）が2つ連続する
入力例

```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
</Item>
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">ア</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名2</Sentence>
    </Column>
    </ListSentence>
</List>
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">イ</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名3</Sentence>
    </Column>
    </ListSentence>
</List>
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">（ア）</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名4</Sentence>
    </Column>
    </ListSentence>
</List>

```

出力例

```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title>ア</Subitem1Title>
        <Subitem1Sentence>
            <Sentence  Num="1">項目名2</Sentence>
        </Subitem1Sentence>
    </Subitem1>
    <Subitem1 Num="2">
        <Subitem1Title>イ</Subitem1Title>
        <Subitem1Sentence>
            <Sentence  Num="1">項目名3</Sentence>
        </Subitem1Sentence>
        <List>
            <ListSentence>
                <Column Num="1">
                    <Sentence Num="1">（ア）</Sentence>
                </Column>
                <Column Num="2">
                    <Sentence Num="1">項目名4</Sentence>
                </Column>
            </ListSentence>
        </List>
    </Subitem1>
</Item>

```
**注記**: 
- 「（ア）」は階層4のため、このスクリプトでは変換しない
- Listのまま直前のSubitem1（イ）内に保持
- 次のスクリプト（convert_subitem1_to_subitem2.py）で処理される
##### 補足説明： 階層が深いList要素の扱い

この例では：
- 「ア」「イ」: カタカナ（階層3）→ Subitem1に変換 ✅
- 「（ア）」: 括弧カタカナ（階層4）→ **Listのまま保持** ✅
  - 直前のSubitem1（イ）内に追加
  - Subitem2特化スクリプトで処理される

**重要**: このListは削除されず、XML構造内に保持される。
次のスクリプト（convert_subitem1_to_subitem2.py）が：
1. Subitem1内のListを検索
2. 括弧カタカナ（階層4）を発見
3. Subitem2要素に変換

### 処理２−２ List要素のColumnの1つ目が項目ラベルに該当し、ItemTitleの値とcolumnの1つ目を比較した結果、Columnの1つ目の階層レベルが同じである場合
1. Item要素を分割し、columnの1つ目の項目ラベルを新たなItem要素のItemTitleに挿入する。
2. columnの2つ目をItemSentenceに挿入する。

#### 例1 分割が1回
入力例
```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名１</Sentence>
    </ItemSentence>
    </Item>
    <List>
        <ListSentence>
        <Column Num="1">
            <Sentence Num="1">（２）</Sentence>
        </Column>
        <Column Num="2">
            <Sentence Num="1">項目名２</Sentence>
        </Column>
        </ListSentence>
    </List>
    {中略}
```

出力例
```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名１</Sentence>
    </ItemSentence>
</Item>
<Item Num="2">
    <ItemTitle>（２）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名２</Sentence>
    </ItemSentence>
</Item>
    {中略}
```

#### 例2 分割が複数回
入力例
```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名１</Sentence>
    </ItemSentence>
    </Item>
    <List>
        <ListSentence>
        <Column Num="1">
            <Sentence Num="1">（２）</Sentence>
        </Column>
        <Column Num="2">
            <Sentence Num="1">項目名２</Sentence>
        </Column>
        </ListSentence>
    </List>
    <List>
        <ListSentence>
        <Column Num="1">
            <Sentence Num="1">（３）</Sentence>
        </Column>
        <Column Num="2">
            <Sentence Num="1">項目名３</Sentence>
        </Column>
        </ListSentence>
    </List>
    {中略}

```

出力例
```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名１</Sentence>
    </ItemSentence>
</Item>
<Item Num="2">
    <ItemTitle>（２）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名２</Sentence>
    </ItemSentence>
</Item>
<Item Num="3">
    <ItemTitle>（３）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名３</Sentence>
    </ItemSentence>
</Item>
    {中略}
```
#### 例3 Item要素が複数の階層を持つ
Item要素が複数の要素を持っている場合でも、ItemTitleの階層を元に判定する
入力例
```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名１</Sentence>
    </ItemSentence>
    </Item>
<Item Num="2">
    <ItemTitle>（２）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名２</Sentence>
    </ItemSentence>
</Item>
<Item Num="3">
    <ItemTitle>（３）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名３</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title>ア</Subitem1Title>
        <Subitem1Sentence>
            <Sentence  Num="1">項目名４</Sentence>
        </Subitem1Sentence>
    </Subitem1>
</Item>
<List>
    <ListSentence>
        <Column Num="1">
            <Sentence Num="1">（４）</Sentence>
        </Column>
        <Column Num="2">
            <Sentence Num="1">項目名５</Sentence>
        </Column>
    </ListSentence>
</List>
```

出力例
```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名１</Sentence>
    </ItemSentence>
    </Item>
<Item Num="2">
    <ItemTitle>（２）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名２</Sentence>
    </ItemSentence>
</Item>
<Item Num="3">
    <ItemTitle>（３）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名３</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title>ア</Subitem1Title>
        <Subitem1Sentence>
            <Sentence  Num="1">項目名４</Sentence>
        </Subitem1Sentence>
    </Subitem1>
</Item>
<Item Num="4">
    <ItemTitle>（４）</ItemTitle>
    <ItemSentence>
    <Sentence Num="1">項目名５</Sentence>
    </ItemSentence>
</Item>
```

### 処理３　Num属性の振り直し
Item要素のNum要素は、Paragraph要素内での登場順の連番とする。

## 後続処理の責任範囲

このスクリプト（Item特化）の後に実行される専用スクリプト：

### Subitem2特化スクリプト
- 対象: Subitem1内に残ったList要素
- 処理: 括弧カタカナ（階層4）→ Subitem2に変換
- 入力: Item特化スクリプトの出力XML
- 出力: Subitem2まで構造化されたXML

### Subitem3特化スクリプト（必要に応じて）
- 対象: Subitem2内に残ったList要素
- 処理: 二重括弧カタカナ（階層5）→ Subitem3に変換