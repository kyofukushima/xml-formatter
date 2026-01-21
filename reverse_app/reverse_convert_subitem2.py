#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem2要素をList要素に逆変換するスクリプト

Subitem1要素内のSubitem2要素をList要素に変換する。
- Subitem2Titleがある場合: 2カラムのList要素（Column1: Subitem2Title, Column2: Subitem2Sentence）
- Subitem2Titleがない場合: ColumnなしのList要素
"""

import sys
from pathlib import Path

# 共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reverse_xml_converter import ReverseConversionConfig, main_with_config


def main():
    """メイン関数"""
    # Subitem2逆変換の設定
    config = ReverseConversionConfig(
        parent_tag='Subitem1',
        child_tag='Subitem2',
        title_tag='Subitem2Title',
        sentence_tag='Subitem2Sentence',
        script_name='reverse_convert_subitem2'
    )

    return main_with_config(
        config,
        description='Subitem2要素をList要素に逆変換するスクリプト',
        default_output_suffix='_reverse_subitem2.xml'
    )


if __name__ == '__main__':
    sys.exit(main())
