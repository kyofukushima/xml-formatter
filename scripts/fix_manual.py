#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
手動修正スクリプト：漢数字ラベルの問題を修正
"""

import sys
from pathlib import Path
from lxml import etree

def fix_kanji_labels(input_file, output_file):
    """漢数字ラベルの問題を修正"""
    tree = etree.parse(input_file)
    root = tree.getroot()

    for paragraph in root.xpath('.//Paragraph'):
        items = paragraph.findall('Item')
        if len(items) >= 2:
            item1 = items[0]
            item2 = items[1]

            # Item2のSubitem2を探す
            subitem2 = item2.find('.//Subitem2')
            if subitem2 is not None:
                lists = subitem2.findall('List')
                if len(lists) >= 2:
                    # 最初のListが"一"の内容
                    list1 = lists[0]
                    col1_1 = list1.find('.//Column[1]/Sentence')
                    col2_1 = list1.find('.//Column[2]/Sentence')
                    if col1_1 is not None and col2_1 is not None:
                        label1 = "".join(col1_1.itertext()).strip()
                        if label1 == "一":
                            item1.find('ItemTitle').text = label1
                            item1.find('ItemSentence/Sentence').text = "".join(col2_1.itertext()).strip()
                            print("Fixed Item1 with '一'")

                    # 2番目のListが"二"の内容
                    list2 = lists[1]
                    col1_2 = list2.find('.//Column[1]/Sentence')
                    col2_2 = list2.find('.//Column[2]/Sentence')
                    if col1_2 is not None and col2_2 is not None:
                        label2 = "".join(col1_2.itertext()).strip()
                        if label2 == "二":
                            item2.find('ItemTitle').text = label2
                            item2.find('ItemSentence/Sentence').text = "".join(col2_2.itertext()).strip()
                            print("Fixed Item2 with '二'")

                            # Listを削除
                            for list_elem in lists[:2]:
                                subitem2.remove(list_elem)
                            print("Removed kanji number lists")

    # 空のSubitemを削除
    for item in root.xpath('.//Item'):
        subitems_to_remove = []
        for subitem in item.findall('Subitem1') + item.findall('Subitem2'):
            title = subitem.find(f'{subitem.tag}Title')
            sentence = subitem.find(f'{subitem.tag}Sentence/Sentence')

            title_text = "".join(title.itertext()).strip() if title is not None else ""
            sentence_text = "".join(sentence.itertext()).strip() if sentence is not None else ""

            # SubitemTitleとSubitemSentenceが空で、他の子要素がない場合のみ削除
            has_children = (len(subitem.findall('Subitem1')) > 0 or
                          len(subitem.findall('Subitem2')) > 0 or
                          len(subitem.findall('List')) > 0 or
                          len(subitem.findall('TableStruct')) > 0 or
                          len(subitem.findall('FigStruct')) > 0)

            if not title_text and not sentence_text and not has_children:
                subitems_to_remove.append(subitem)

        for subitem in subitems_to_remove:
            item.remove(subitem)

    tree.write(output_file, encoding='utf-8', xml_declaration=True, pretty_print=True)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("使用法: python3 fix_manual.py input.xml output.xml")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    fix_kanji_labels(input_file, output_file)
    print(f"修正完了: {output_file}")
