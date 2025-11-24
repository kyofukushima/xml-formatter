#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem5要素変換ロジック実装スクリプト（共通化版）

xml_converter.pyを使用してSubitem4要素内のList要素をSubitem5要素に変換する。
"""

import sys
import argparse
from pathlib import Path

# 共通モジュールをインポート
from xml_converter import ConversionConfig, process_xml_file


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Subitem5要素変換ロジック実装スクリプト（共通化版）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python3 convert_subitem5_step0.py input.xml
  python3 convert_subitem5_step0.py input.xml output.xml
        '''
    )

    parser.add_argument('input_file', help='入力XMLファイル')
    parser.add_argument('output_file', nargs='?', help='出力XMLファイル（デフォルト: _subitem5_step0.xml）')

    args = parser.parse_args()

    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1

    output_path = Path(args.output_file) if args.output_file else input_path.parent / f"{input_path.stem}_subitem5_step0.xml"

    # Subitem5変換の設定（学年パターンもサポート）
    config = ConversionConfig(
        parent_tag='Subitem4',
        child_tag='Subitem5',
        title_tag='Subitem5Title',
        sentence_tag='Subitem5Sentence',
        column_condition_min=2,  # Subitem5は col_count == 2
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem5_step0',
        skip_empty_parent=True  # Subitem5変換では親要素チェックを行う
    )

    return process_xml_file(input_path, output_path, config)


if __name__ == '__main__':
    sys.exit(main())

