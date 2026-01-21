#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem5要素をList要素に逆変換するスクリプト

Subitem4要素内のSubitem5要素をList要素に変換する。
- Subitem5Titleがある場合: 2カラムのList要素（Column1: Subitem5Title, Column2: Subitem5Sentence）
- Subitem5Titleがない場合: ColumnなしのList要素
"""

import sys
from pathlib import Path

# 共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reverse_xml_converter import ReverseConversionConfig, main_with_config


def main():
    """メイン関数"""
    # Subitem5逆変換の設定
    config = ReverseConversionConfig(
        parent_tag='Subitem4',
        child_tag='Subitem5',
        title_tag='Subitem5Title',
        sentence_tag='Subitem5Sentence',
        script_name='reverse_convert_subitem5'
    )

    return main_with_config(
        config,
        description='Subitem5要素をList要素に逆変換するスクリプト',
        default_output_suffix='_reverse_subitem5.xml'
    )


if __name__ == '__main__':
    sys.exit(main())
