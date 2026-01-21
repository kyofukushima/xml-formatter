#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem3要素をList要素に逆変換するスクリプト

Subitem2要素内のSubitem3要素をList要素に変換する。
- Subitem3Titleがある場合: 2カラムのList要素（Column1: Subitem3Title, Column2: Subitem3Sentence）
- Subitem3Titleがない場合: ColumnなしのList要素
"""

import sys
from pathlib import Path

# 共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reverse_xml_converter import ReverseConversionConfig, main_with_config


def main():
    """メイン関数"""
    # Subitem3逆変換の設定
    config = ReverseConversionConfig(
        parent_tag='Subitem2',
        child_tag='Subitem3',
        title_tag='Subitem3Title',
        sentence_tag='Subitem3Sentence',
        script_name='reverse_convert_subitem3'
    )

    return main_with_config(
        config,
        description='Subitem3要素をList要素に逆変換するスクリプト',
        default_output_suffix='_reverse_subitem3.xml'
    )


if __name__ == '__main__':
    sys.exit(main())




