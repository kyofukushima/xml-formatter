"""
ファイル操作ユーティリティ

ファイルのアップロード、保存、検証などの機能を提供します。
"""
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import streamlit as st


def save_uploaded_file(uploaded_file) -> Optional[Path]:
    """
    アップロードされたファイルを一時保存
    
    Args:
        uploaded_file: StreamlitのUploadedFileオブジェクト
    
    Returns:
        保存されたファイルのPathオブジェクト、失敗時はNone
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
            tmp_file.write(uploaded_file.read())
            return Path(tmp_file.name)
    except Exception as e:
        st.error(f"ファイルの保存に失敗しました: {e}")
        return None


def validate_xml_file(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    XMLファイルの検証（拡張子、存在確認）
    
    Args:
        file_path: 検証するファイルのパス
    
    Returns:
        (is_valid: bool, error_message: Optional[str])
    """
    if not file_path.exists():
        return False, "ファイルが見つかりません"
    
    if file_path.suffix.lower() != '.xml':
        return False, "XMLファイルではありません"
    
    # ファイルサイズのチェック（100MB制限）
    max_size = 100 * 1024 * 1024  # 100MB
    if file_path.stat().st_size > max_size:
        return False, f"ファイルサイズが大きすぎます（最大100MB）"
    
    return True, None


def cleanup_temp_files(file_paths: list[Path]) -> None:
    """
    一時ファイルの削除
    
    Args:
        file_paths: 削除するファイルのパスのリスト
    """
    for path in file_paths:
        if isinstance(path, Path) and path.exists():
            try:
                path.unlink()
            except Exception as e:
                st.warning(f"一時ファイルの削除に失敗しました: {path} - {e}")


