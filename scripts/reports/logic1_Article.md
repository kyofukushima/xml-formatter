# Article修正ロジック

## 対応スクリプト
`convert_article_focused.py`

## 参考ファイル
- 参考入力ファイル：test_input5.xml
- 参考出力ファイル：test_output.xml

## パターン１　ArticleTitleが空の場合

出現したarticle要素のArticleTitleに何もない場合は、閉じタグがくるまで何も処理をしない。

入力

```xml
      <Article Num="999999999">
            <ArticleTitle/>
            <Paragraph Num="1">
              <ParagraphNum/>
              <List>
                <ListSentence>
                  <Sentence Num="1" >高等部における教育については，学校教育法第７２条に定める目的を実現するために，生徒の障害の状態や特性及び心身の発達の段階等を十分考慮して，次に掲げる目標の達成に努めなければならない。</Sentence>
                </ListSentence>
              </List>
              <List>
                <ListSentence>
                  <Column Num="1">
                    <Sentence Num="1" >１</Sentence>
                  </Column>
                  <Column Num="2">
                    <Sentence Num="1" >学校教育法第５１条に規定する高等学校教育の目標</Sentence>
                  </Column>
                </ListSentence>
              </List>
              <List>
                <ListSentence>
                  <Column Num="1">
                    <Sentence Num="1" >２</Sentence>
                  </Column>
                  <Column Num="2">
                    <Sentence Num="1" >生徒の障害による学習上又は生活上の困難を改善・克服し自立を図るために必要な知識，技能，態度及び習慣を養うこと。</Sentence>
                  </Column>
                </ListSentence>
              </List>
            </Paragraph>
          </Article>
```

出力

```xml

<Article Num="1">
              <ArticleTitle/>
              <Paragraph Num="1">
                <ParagraphNum/>
                <ParagraphSentence>
                  <Sentence Num="1" >高等部における教育については，学校教育法第７２条に定める目的を実現するために，生徒の障害の状態や特性及び心身の発達の段階等を十分考慮して，次に掲げる目標の達成に努めなければならない。</Sentence>
                </ParagraphSentence>
                <Item Num="1">
                  <ItemTitle>１</ItemTitle>
                  <ItemSentence>
                    <Sentence Num="1" >学校教育法第５１条に規定する高等学校教育の目標</Sentence>
                  </ItemSentence>
                </Item>
                <Item Num="2">
                  <ItemTitle>２</ItemTitle>
                  <ItemSentence>
                    <Sentence Num="1" >生徒の障害による学習上又は生活上の困難を改善・克服し自立を図るために必要な知識，技能，態度及び習慣を養うこと。</Sentence>
                  </ItemSentence>
                </Item>
              </Paragraph>
            </Article>


```

## パターン２ ArticleTitleが第＋数字である

ArticleTitleが「第１」「第二」など、「第」と数字の構成である場合は、次に同じ構成で、次の数字が出てきたタイミングでArticle要素を分割する。

### 注意点

数字のパターンについて

数字のパターンはいくつか存在する

1. 半角数字：1,2.3,4
2. 全角数字：１,２,３,４
3. 括弧付きの数字：（1）, （2）, （3）または（１）, （２）, （３）, （４）
4. 漢数字（一,二,三,四）
5. アルファベット（A,B,C,D または a,b,c,d）

また、「第」が頭についていない場合が存在するが、分割するかどうかは、同じ構成であるかどうかで判断する。

つまり、「第一」の後に「１」が来ても、Article要素は分割せず、「第二」が来た場合と、その他例外パターンが出現した際に分割する。



入力例

```xml
<Article Num="999999999">
  <ArticleTitle>第１</ArticleTitle>
  {中略}
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1" >第２</Sentence>
      </Column>
      {中略}
    </ListSentence>
  </List>
```

出力例

```xml
<Article Num="1">
  <ArticleTitle>第１</ArticleTitle>
{中略}
</Article>
<Article Num="2">
<ArticleTitle>第２</ArticleTitle>
{中略}
```

パターン３　ArticleTitleがない場合

Article要素内にArticleTitle要素がない場合は、要素の最初に追加する

入力例

```xml
<Article Num="999999999">
   <Paragraph Num="1">
              <ParagraphNum/>
  {中略}

```

出力例

```xml
<Article Num="999999999">
  <ArticleTitle/>
   <Paragraph Num="1">
              <ParagraphNum/>
  {中略}

```

