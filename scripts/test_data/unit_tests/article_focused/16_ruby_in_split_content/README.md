# 16: Article分割時の本文に Ruby（ふりがな）を含むケース

境界ラベル「第２」の List の2列目以降に Ruby を含む Sentence がある場合、
新しい Article の ParagraphSentence に Ruby 要素を保持したまま移すことを確認する
（従来は文字列化により読み「なん」が本文に混ざっていた）。
3列以上の Column は従来どおり全角スペースで結合する。
