#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem9要素をList要素に逆変換するスクリプト

Subitem8要素内のSubitem9要素をList要素に変換する。
- Subitem9Titleがある場合: 2カラムのList要素（Column1: Subitem9Title, Column2: Subitem9Sentence）
- Subitem9Titleがない場合: ColumnなしのList要素
"""

import sys
from pathlib import Path

# 共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reverse_xml_converter import ReverseConversionConfig, main_with_config


def main():
    """メイン関数"""
    # Subitem9逆変換の設定
    config = ReverseConversionConfig(
        parent_tag='Subitem8',
        child_tag='Subitem9',
        title_tag='Subitem9Title',
        sentence_tag='Subitem9Sentence',
        script_name='reverse_convert_subitem9'
    )

    return main_with_config(
        config,
        description='Subitem9要素をList要素に逆変換するスクリプト',
        default_output_suffix='_reverse_subitem9.xml'
    )


if __name__ == '__main__':
    sys.exit(main())
