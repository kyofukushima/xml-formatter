# Paragraph修正ロジック4

## 対応スクリプト
`convert_paragraph_step4.py`

## 本文章のスコープ
Paragraph特化スクリプト（Step4: ParagraphSentence分割）

**前提**: Paragraph修正ロジック3（Step2-3）の処理済みであること

## 項目ラベル定義

項目ラベルの詳細な定義については、[common/label_definitions.md](common/label_definitions.md) を参照してください

## 処理１ ParagraphNumの直下以外にParagraphSentenceが存在する場合
全角スペースでテキストを分割し、リスト要素に変換する

入力例
```xml
<ParagraphSentence>
    <Sentence Num="1">（（ア））　項目名</Sentence>
</ParagraphSentence>
```
出力例
```xml
<List>
    <ListSentence>
    <Column Num="1">
        <Sentence Num="1">（（ア））</Sentence>
    </Column>
    <Column Num="2">
        <Sentence Num="1">項目名</Sentence>
    </Column>
    </ListSentence>
</List>
```