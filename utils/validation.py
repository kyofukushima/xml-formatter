"""
検証ユーティリティ

XML構文検証とテキスト内容検証の機能を提供します。
"""
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict
import xml.etree.ElementTree as ET
import streamlit as st


def validate_xml_syntax(file_path: Path) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    XML構文検証を実行
    
    Args:
        file_path: 検証するXMLファイルのパス
    
    Returns:
        (is_valid: bool, error_message: Optional[str], validation_output: Optional[str])
    """
    if not file_path.exists():
        return False, "ファイルが見つかりません", None
    
    try:
        # xml.etree.ElementTreeを使用して構文検証
        tree = ET.parse(file_path)
        return True, None, f"SUCCESS: XML file '{file_path}' is well-formed."
    except ET.ParseError as e:
        error_msg = f"XML構文エラー: {str(e)}"
        return False, error_msg, f"ERROR: XML parsing failed for file '{file_path}'.\nError message: {e}"
    except Exception as e:
        error_msg = f"予期しないエラー: {str(e)}"
        return False, error_msg, f"ERROR: Unexpected error: {e}"


def validate_xml_syntax_with_script(
    file_path: Path,
    validation_script_path: Optional[Path] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    既存の検証スクリプトを使用してXML構文検証を実行
    
    Args:
        file_path: 検証するXMLファイルのパス
        validation_script_path: 検証スクリプトのパス（Noneの場合はデフォルト）
    
    Returns:
        (is_valid: bool, error_message: Optional[str], validation_output: Optional[str])
    """
    if validation_script_path is None:
        # デフォルトの検証スクリプトパス
        script_dir = file_path.parent.parent / "scripts"
        validation_script_path = script_dir / "validate_xml.py"
    
    if not validation_script_path.exists():
        # スクリプトが見つからない場合は、直接検証
        return validate_xml_syntax(file_path)
    
    try:
        result = subprocess.run(
            [sys.executable, str(validation_script_path), str(file_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        
        if result.returncode == 0 and "SUCCESS:" in output:
            return True, None, output
        else:
            return False, "XML構文エラーが検出されました", output
    
    except subprocess.TimeoutExpired:
        return False, "検証がタイムアウトしました", None
    except Exception as e:
        return False, f"検証スクリプトの実行エラー: {str(e)}", None


def validate_text_content(
    original_file: Path,
    processed_file: Path,
    comparison_script_path: Optional[Path] = None
) -> Tuple[bool, Optional[str], Optional[str], Optional[Dict]]:
    """
    テキスト内容検証を実行（元のXMLと処理後のXMLのテキスト内容が一致するか確認）
    
    Args:
        original_file: 元のXMLファイルのパス
        processed_file: 処理後のXMLファイルのパス
        comparison_script_path: 比較スクリプトのパス（Noneの場合はデフォルト）
    
    Returns:
        (is_valid: bool, error_message: Optional[str], validation_output: Optional[str], report_data: Optional[Dict])
    """
    if not original_file.exists():
        return False, "元のファイルが見つかりません", None, None
    
    if not processed_file.exists():
        return False, "処理後のファイルが見つかりません", None, None
    
    if comparison_script_path is None:
        # デフォルトの比較スクリプトパス
        script_dir = original_file.parent.parent / "scripts"
        comparison_script_path = script_dir / "compare_xml_text_content.py"
    
    if not comparison_script_path.exists():
        return False, "比較スクリプトが見つかりません", None, None
    
    try:
        # 一時的なレポートファイルを作成
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_report:
            report_path = Path(tmp_report.name)
        
        result = subprocess.run(
            [
                sys.executable,
                str(comparison_script_path),
                str(original_file),
                str(processed_file),
                "--report_file",
                str(report_path)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # レポートファイルを読み込む
        report_data = None
        if report_path.exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # レポートの内容を解析
            report_data = {
                "content": report_content,
                "success": "✅ Success:" in report_content or "SUCCESS:" in report_content,
                "errors": []
            }
            
            # エラー行を抽出
            for line in report_content.split('\n'):
                if "❌ Error:" in line or "ERROR:" in line:
                    report_data["errors"].append(line)
            
            # 一時ファイルを削除
            report_path.unlink()
        
        if result.returncode == 0 and report_data and report_data["success"]:
            return True, None, result.stdout, report_data
        else:
            error_msg = "テキスト内容の不一致が検出されました"
            if report_data and report_data["errors"]:
                error_msg += f"\nエラー数: {len(report_data['errors'])}"
            return False, error_msg, result.stdout + result.stderr, report_data
    
    except subprocess.TimeoutExpired:
        return False, "検証がタイムアウトしました", None, None
    except Exception as e:
        return False, f"検証スクリプトの実行エラー: {str(e)}", None, None


def format_validation_report(report_data: Dict) -> str:
    """
    検証レポートをフォーマット
    
    Args:
        report_data: 検証レポートデータ
    
    Returns:
        フォーマットされたレポート文字列
    """
    if not report_data:
        return "レポートデータがありません"
    
    lines = []
    lines.append("=" * 60)
    lines.append("検証レポート")
    lines.append("=" * 60)
    
    if report_data.get("success"):
        lines.append("✅ 検証結果: 成功")
    else:
        lines.append("❌ 検証結果: 失敗")
    
    if report_data.get("errors"):
        lines.append(f"\nエラー数: {len(report_data['errors'])}")
        lines.append("\nエラー詳細:")
        for error in report_data["errors"][:10]:  # 最初の10個のみ表示
            lines.append(f"  - {error}")
        if len(report_data["errors"]) > 10:
            lines.append(f"  ... 他 {len(report_data['errors']) - 10} 件のエラー")
    
    if report_data.get("content"):
        lines.append("\n詳細:")
        lines.append("-" * 60)
        lines.append(report_data["content"][:1000])  # 最初の1000文字のみ表示
        if len(report_data["content"]) > 1000:
            lines.append("\n... (以下省略)")
    
    return "\n".join(lines)


