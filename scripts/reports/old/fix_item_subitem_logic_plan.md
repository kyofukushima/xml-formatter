# Item/Subitem変換ロジック修正方針

## 目的
ユーザーの指示「同じ種類であれば分割し、それ以外であれば取り込む」というロジックを、現在のコードベースに厳密に適用するための修正方針を明確にする。特に、`ItemTitle`が空の`Item`や、`List`要素の取り込み/分割の判断基準を明確化する。

## 現状の課題

1.  **`Item`要素の順序逆転問題の解消:**
    *   `convert_item_step0.py` および `convert_subitem*_step0.py` において、`AGGREGATING_INTO_CONTAINER`モードでの要素挿入順序の誤り、および`NORMAL_PROCESSING`モードでの`insert`使用による順序逆転の問題は解消済み。
    *   これにより、`Item Num="1"`の子要素として`ア`と`（ア）`の`List`が元の順序で取り込まれることは確認済み。

2.  **「同じ種類であれば分割し、それ以外であれば取り込む」ロジックの不完全な適用:**
    *   `test_output_item_step0.xml`の`Paragraph Num="3"`において、`Item Num="1"`（`ItemTitle`が`（１）`で`PAREN_NUMBER`型）の後に、`Item Num="2"`（`ItemTitle`が空で`other`型）が兄弟要素として存在している。
    *   ユーザーの指示を厳密に適用すると、`PAREN_NUMBER`型と`other`型は異なる種類であるため、`Item Num="2"`は`Item Num="1"`の子要素として取り込まれるべきである。
    *   この問題は、`are_same_hierarchy`関数（および`are_same_hierarchy_subitem*`関数）のロジックと、`process_paragraph_recursive`（および`process_item_recursive`、`process_subitem*_recursive`）関数内のモード遷移および要素作成ロジックの間に不整合があることに起因する。

## 理想の状態

*   すべての`convert_*.py`スクリプトにおいて、ユーザーの指示「**同じ種類であれば分割し、それ以外であれば取り込む**」が厳密に適用される。
*   具体的には、`Item`（または`Subitem`）要素の`Title`の型と、次に続く`List`要素（またはその他の要素が`Item`に変換された場合の`Title`の型）を比較し、
    *   **同じ種類**と判定された場合は、新しい`Item`（または`Subitem`）として**分割**される。
    *   **異なる種類**と判定された場合は、既存の`Item`（または`Subitem`）の**子要素として取り込まれる**。
*   これにより、`test_output_item_step0.xml`の`Paragraph Num="3"`の例では、`Item Num="1"`（`PAREN_NUMBER`型）の後に続く`ItemTitle`が空の`Item`（`other`型）は、`Item Num="1"`の子要素として取り込まれるようになる。また、`Item Num="1`の後に続く`List`（`Column Num="1"`が`（イ）`で`PAREN_NUMBER`型）は、`Item Num="1"`と同じ種類であるため、新しい`Item`として分割される。

## 修正方針（詳細）

1.  **`are_same_hierarchy`関数（および`are_same_hierarchy_subitem*`関数）のロジック修正:**
    *   現在の`are_same_hierarchy`関数は、`item_type == 'other'`の場合に`list_type`が`'labeled'`, `'subject_name'`, `'instruction'`であれば`True`（分割）を返しているが、これはユーザーの指示と矛盾する。`'other'`型と`'labeled'`型は異なる種類であるため、この場合は`False`（取り込み）を返すように変更する。
    *   修正後のロジックは以下の通りとする：
        *   `item_type`と`list_type`が両方とも`'labeled'`の場合のみ、`item_pattern == list_pattern`で比較し、同じ種類であれば`True`（分割）、異なる種類であれば`False`（取り込み）を返す。
        *   `item_type`が`'subject_name'`かつ`list_type`が`'subject_name'`の場合、`True`（分割）を返す。
        *   `item_type`が`'instruction'`かつ`list_type`が`'instruction'`の場合、`True`（分割）を返す。
        *   上記以外の場合は、すべて異なる種類とみなし、`False`（取り込み）を返す。
    *   この修正を、以下のすべてのファイルに適用する：
        *   `scripts/education_script/focused_converters/convert_item_step0.py`
        *   `scripts/education_script/focused_converters/convert_subitem1_step0.py`
        *   `scripts/education_script/focused_converters/convert_subitem2_step0.py`
        *   `scripts/education_script/focused_converters/convert_subitem3_step0.py`

2.  **`process_paragraph_recursive`関数（および`process_item_recursive`、`process_subitem*_recursive`関数）のモード遷移ロジックの調整:**
    *   `LOOKING_FOR_FIRST_ITEM`モードは、`ParagraphSentence`（または`ItemSentence`、`Subitem*Sentence`）の直後の最初の要素を処理するのみに限定する。
    *   このモードで最初の`Item`（または`Subitem`）が作成された後は、必ず`NORMAL_PROCESSING`モードに移行するようにする。
    *   `AGGREGATING_INTO_CONTAINER`モードは完全に削除する。このモードで行っていた処理は、`NORMAL_PROCESSING`モードの「取り込み」ロジックに統合される。
    *   `NORMAL_PROCESSING`モードでは、常に`are_same_hierarchy`関数（または`are_same_hierarchy_subitem*`関数）の結果に基づいて「分割」か「取り込み」かを判断する。
        *   `are_same_hierarchy`が`True`を返した場合（同じ種類）、新しい`Item`（または`Subitem`）を作成し、`new_children`に追加する。
        *   `are_same_hierarchy`が`False`を返した場合（異なる種類）、現在の要素を`last_item`（または`last_subitem*`）の子要素として取り込む。
    *   この修正を、以下のすべてのファイルに適用する：
        *   `scripts/education_script/focused_converters/convert_item_step0.py`
        *   `scripts/education_script/focused_converters/convert_subitem1_step0.py`
        *   `scripts/education_script/focused_converters/convert_subitem2_step0.py`
        *   `scripts/education_script/focused_converters/convert_subitem3_step0.py`

## 具体的な修正手順

1.  **`convert_item_step0.py`の修正:**
    *   `are_same_hierarchy`関数を上記修正方針に従って変更。
    *   `process_paragraph_recursive`関数内の`LOOKING_FOR_FIRST_ITEM`モードのロジックを修正し、`AGGREGATING_INTO_CONTAINER`モードへの遷移を削除し、`NORMAL_PROCESSING`モードへの移行を適切に行うようにする。
    *   `AGGREGATING_INTO_CONTAINER`モードのブロックを削除。
    *   `NORMAL_PROCESSING`モードで`List`以外の要素を取り込む際も`last_item.append(child)`を使用するように変更。
2.  **`convert_subitem1_step0.py`の修正:**
    *   `are_same_hierarchy_subitem1`関数を上記修正方針に従って変更。
    *   `process_item_recursive`関数内の`LOOKING_FOR_FIRST_ITEM`モードのロジックを修正し、`AGGREGATING_INTO_CONTAINER`モードへの遷移を削除し、`NORMAL_PROCESSING`モードへの移行を適切に行うようにする。
    *   `AGGREGATING_INTO_CONTAINER`モードのブロックを削除。
    *   `NORMAL_PROCESSING`モードで`List`以外の要素を取り込む際も`last_subitem1.append(child)`を使用するように変更。
3.  **`convert_subitem2_step0.py`の修正:**
    *   `are_same_hierarchy_subitem2`関数を上記修正方針に従って変更。
    *   `process_subitem1_recursive`関数内の`LOOKING_FOR_FIRST_ITEM`モードのロジックを修正し、`AGGREGATING_INTO_CONTAINER`モードへの遷移を削除し、`NORMAL_PROCESSING`モードへの移行を適切に行うようにする。
    *   `AGGREGATING_INTO_CONTAINER`モードのブロックを削除。
    *   `NORMAL_PROCESSING`モードで`List`以外の要素を取り込む際も`last_subitem2.append(child)`を使用するように変更。
4.  **`convert_subitem3_step0.py`の修正:**
    *   `are_same_hierarchy_subitem3`関数を上記修正方針に従って変更。
    *   `process_subitem2_recursive`関数内の`LOOKING_FOR_FIRST_ITEM`モードのロジックを修正し、`AGGREGATING_INTO_CONTAINER`モードへの遷移を削除し、`NORMAL_PROCESSING`モードへの移行を適切に行うようにする。
    *   `AGGREGATING_INTO_CONTAINER`モードのブロックを削除。
    *   `NORMAL_PROCESSING`モードで`List`以外の要素を取り込む際も`last_subitem3.append(child)`を使用するように変更。

この修正方針を適用することで、ユーザーの意図する「同じ種類であれば分割し、それ以外であれば取り込む」というロジックが、すべての階層レベルで一貫して適用されることを目指します。
