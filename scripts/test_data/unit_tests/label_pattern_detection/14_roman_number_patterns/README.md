# 14_roman_number_patterns

## テスト内容

全角ローマ数字パターンの検証テストです。全角アルファベットとの区別も確認します。

## 含まれるパターン

- **全角ローマ数字（大文字）**: `Ⅰ`, `Ⅱ`, `Ⅲ` (各1個)
- **全角ローマ数字（小文字）**: `ⅰ`, `ⅱ` (各1個)
- **全角アルファベットとの区別**: `Ａ`, `Ｂ` (各1個)

## 期待される動作

各パターンがItemレベルとして扱われます。全角ローマ数字が正しく認識され、全角アルファベットと区別されることを確認します。

## 階層構造

```
Item Num="1": Ⅰ (roman_number_uppercase)
Item Num="2": Ⅱ (roman_number_uppercase)
Item Num="3": Ⅲ (roman_number_uppercase)
  └─ Subitem1 Num="1": ⅰ (roman_number_lowercase)
  └─ Subitem1 Num="2": ⅱ (roman_number_lowercase)
      └─ Subitem2 Num="1": Ａ (fullwidth_uppercase_alphabet)
      └─ Subitem2 Num="2": Ｂ (fullwidth_uppercase_alphabet)
```

## 優先順位の確認

- `roman_number_uppercase` (`Ⅰ`, `Ⅱ`, `Ⅲ`) が全角アルファベットより優先される
- `roman_number_lowercase` (`ⅰ`, `ⅱ`) が全角アルファベットより優先される
- `fullwidth_uppercase_alphabet` (`Ａ`, `Ｂ`) はローマ数字でない場合にのみマッチする

これにより、`Ⅰ`はローマ数字として認識され、`Ａ`はアルファベットとして認識されます。

## Unicode範囲

- **全角ローマ数字（大文字）**: U+2160-U+216F (Ⅰ-Ⅿ)
- **全角ローマ数字（小文字）**: U+2170-U+217F (ⅰ-ⅿ)
- **全角アルファベット（大文字）**: U+FF21-U+FF3A (Ａ-Ｚ)
- **全角アルファベット（小文字）**: U+FF41-U+FF5A (ａ-ｚ)

異なるUnicode範囲のため、正規表現で明確に区別できます。

## 注意事項

- 全角ローマ数字はNumber Formsブロック（U+2160-U+217F）に含まれます
- 全角アルファベットはHalfwidth and Fullwidth Formsブロック（U+FF21-U+FF5A）に含まれます
- このパターンは `fullwidth_uppercase_alphabet` より前に評価されるため、優先順位が正しく設定されている必要があります
