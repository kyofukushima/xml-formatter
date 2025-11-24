"""
共通ユーティリティモジュール

各特化型スクリプト（Article、Paragraph、Item等）で共通的に使用する
機能を提供します。
"""

from .xml_utils import (
    indent_xml,
    indent_xml_native,
    save_xml_with_indent,
    pretty_print_xml,
    get_python_version_info
)

from .renumber_utils import (
    renumber_nums_in_tree,
    renumber_nums_in_file,
    renumber_common_elements,
    get_default_mappings
)

from .label_utils import (
    LabelPattern,
    detect_label_pattern,
    is_label,
    get_hierarchy_level,
    split_label_and_content,
    is_paragraph_label,
    is_item_label
)

__all__ = [
    # XML整形関連
    'indent_xml',
    'indent_xml_native',
    'save_xml_with_indent',
    'pretty_print_xml',
    'get_python_version_info',
    
    # Num属性振り直し関連
    'renumber_nums_in_tree',
    'renumber_nums_in_file',
    'renumber_common_elements',
    'get_default_mappings',
    
    # 項目ラベル判定関連
    'LabelPattern',
    'detect_label_pattern',
    'is_label',
    'get_hierarchy_level',
    'split_label_and_content',
    'is_paragraph_label',
    'is_item_label'
]

