#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Item要素をList要素に逆変換するスクリプト

Paragraph, AppdxTable, その他の要素内のItem要素をList要素に変換する。
- ItemTitleがある場合: 2カラムのList要素（Column1: ItemTitle, Column2: ItemSentence）
- ItemTitleがない場合: ColumnなしのList要素
"""

import sys
from pathlib import Path

# 共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reverse_xml_converter import ReverseConversionConfig, main_with_config


def main():
    """メイン関数"""
    # Item逆変換の設定
    config = ReverseConversionConfig(
        parent_tag='Paragraph',
        child_tag='Item',
        title_tag='ItemTitle',
        sentence_tag='ItemSentence',
        script_name='reverse_convert_item'
    )

    return main_with_config(
        config,
        description='Item要素をList要素に逆変換するスクリプト',
        default_output_suffix='_reverse_item.xml'
    )


if __name__ == '__main__':
    sys.exit(main())
