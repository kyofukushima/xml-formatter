"""
XMLプレビューコンポーネント

XMLファイルの内容をプレビュー表示するためのコンポーネント
"""
import streamlit as st
from pathlib import Path
from typing import Optional


def preview_xml_file(file_path: Path, max_lines: int = 1000, show_line_numbers: bool = True) -> None:
    """
    XMLファイルの内容をプレビュー表示
    
    Args:
        file_path: プレビューするXMLファイルのパス
        max_lines: 表示する最大行数（デフォルト: 1000行）
        show_line_numbers: 行番号を表示するかどうか
    """
    if not file_path.exists():
        st.error(f"ファイルが見つかりません: {file_path}")
        return
    
    try:
        # ファイルを読み込む
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        
        # ファイルが大きい場合の処理
        if total_lines > max_lines:
            st.warning(f"⚠️ ファイルが大きいため、最初の{max_lines}行のみを表示しています（全{total_lines}行）")
            display_lines = lines[:max_lines]
            truncated = True
        else:
            display_lines = lines
            truncated = False
        
        # XMLコンテンツを結合
        xml_content = ''.join(display_lines)
        
        # プレビュー表示
        st.code(xml_content, language='xml', line_numbers=show_line_numbers)
        
        # ファイル情報
        file_size = file_path.stat().st_size
        st.caption(f"📄 ファイル: {file_path.name} | サイズ: {file_size / 1024:.2f} KB | 行数: {total_lines}")
        
        if truncated:
            st.info(f"💡 残りの{total_lines - max_lines}行を表示するには、ファイルをダウンロードしてください。")
    
    except UnicodeDecodeError:
        st.error("❌ ファイルの文字エンコーディングが正しくありません（UTF-8が必要です）")
    except Exception as e:
        st.error(f"❌ ファイルの読み込みに失敗しました: {e}")


def preview_xml_content(xml_content: str, file_name: str = "preview.xml") -> None:
    """
    XMLコンテンツを直接プレビュー表示
    
    Args:
        xml_content: プレビューするXMLコンテンツ
        file_name: ファイル名（表示用）
    """
    if not xml_content:
        st.warning("プレビューするコンテンツがありません")
        return
    
    lines = xml_content.split('\n')
    total_lines = len(lines)
    
    # プレビュー表示
    st.code(xml_content, language='xml', line_numbers=True)
    st.caption(f"📄 {file_name} | 行数: {total_lines}")

