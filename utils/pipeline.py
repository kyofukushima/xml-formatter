"""
パイプライン実行ユーティリティ

変換スクリプトを順次実行するパイプライン処理を提供します。
"""
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import streamlit as st


# 変換スクリプトの実行順序（推奨順序）
RECOMMENDED_SCRIPT_ORDER = [
    "preprocess_non_first_sentence_to_list.py",
    "convert_article_focused.py",
    "convert_paragraph_step3.py",
    "convert_paragraph_step4.py",
    "convert_item_step0.py",
    "convert_subitem1_step0.py",
    "convert_subitem2_step0.py",
    "convert_subitem3_step0.py",
    "convert_subitem4_step0.py",
    "convert_subitem5_step0.py",
    "convert_subitem6_step0.py",
    "convert_subitem7_step0.py",
    "convert_subitem8_step0.py",
    "convert_subitem9_step0.py",
    "convert_subitem10_step0.py",
]


def get_available_scripts(script_dir: Path) -> List[str]:
    """
    利用可能な変換スクリプトのリストを取得
    
    Args:
        script_dir: スクリプトディレクトリのパス
    
    Returns:
        スクリプト名のリスト
    """
    if not script_dir.exists():
        return []
    
    scripts = []
    for script_file in script_dir.glob("*.py"):
        # テストファイルやバックアップファイルを除外
        if not script_file.name.startswith("test_") and not script_file.name.endswith(".bak.py"):
            scripts.append(script_file.name)
    
    # 推奨順序でソート
    scripts_sorted = []
    for recommended in RECOMMENDED_SCRIPT_ORDER:
        if recommended in scripts:
            scripts_sorted.append(recommended)
            scripts.remove(recommended)
    
    # 残りのスクリプトを追加
    scripts_sorted.extend(sorted(scripts))
    
    return scripts_sorted


def get_script_description(script_name: str) -> str:
    """
    スクリプトの説明を取得
    
    Args:
        script_name: スクリプト名
    
    Returns:
        スクリプトの説明
    """
    descriptions = {
        "preprocess_non_first_sentence_to_list.py": "前処理: 2個目以降のSentence要素をList要素に変換",
        "convert_article_focused.py": "Article要素の分割と調整",
        "convert_paragraph_step3.py": "Paragraph処理（step3）",
        "convert_paragraph_step4.py": "Paragraph処理（step4）",
        "convert_item_step0.py": "Item変換",
        "convert_subitem1_step0.py": "Subitem1変換",
        "convert_subitem2_step0.py": "Subitem2変換",
        "convert_subitem3_step0.py": "Subitem3変換",
        "convert_subitem4_step0.py": "Subitem4変換",
        "convert_subitem5_step0.py": "Subitem5変換",
        "convert_subitem6_step0.py": "Subitem6変換",
        "convert_subitem7_step0.py": "Subitem7変換",
        "convert_subitem8_step0.py": "Subitem8変換",
        "convert_subitem9_step0.py": "Subitem9変換",
        "convert_subitem10_step0.py": "Subitem10変換",
    }
    return descriptions.get(script_name, "変換スクリプト")


def run_pipeline(
    input_path: Path,
    output_path: Path,
    scripts: List[str],
    script_dir: Path,
    intermediate_dir: Optional[Path] = None,
    timeout: int = 300,
    progress_callback: Optional[callable] = None
) -> Tuple[bool, Optional[str], Dict[str, any]]:
    """
    パイプラインを実行
    
    Args:
        input_path: 入力XMLファイルのパス
        output_path: 出力XMLファイルのパス
        scripts: 実行するスクリプトのリスト
        script_dir: スクリプトディレクトリのパス
        intermediate_dir: 中間ファイル保存ディレクトリ（オプション）
        timeout: タイムアウト時間（秒）
        progress_callback: 進捗コールバック関数（current_step, total_steps, script_name）
    
    Returns:
        (success: bool, error_message: Optional[str], execution_log: Dict)
    """
    if not input_path.exists():
        return False, f"入力ファイルが見つかりません: {input_path}", {}
    
    if not script_dir.exists():
        return False, f"スクリプトディレクトリが見つかりません: {script_dir}", {}
    
    execution_log = {
        "total_steps": len(scripts),
        "completed_steps": 0,
        "failed_step": None,
        "steps": []
    }
    
    current_input = input_path
    total_steps = len(scripts)
    
    for step_idx, script_name in enumerate(scripts, 1):
        script_path = script_dir / script_name
        
        if not script_path.exists():
            error_msg = f"スクリプトが見つかりません: {script_name}"
            execution_log["failed_step"] = script_name
            return False, error_msg, execution_log
        
        # 中間ファイルのパスを決定
        if intermediate_dir:
            intermediate_dir.mkdir(parents=True, exist_ok=True)
            step_output = intermediate_dir / f"step_{step_idx:02d}_{script_name.replace('.py', '.xml')}"
        else:
            step_output = script_dir.parent / "temp" / f"step_{script_name.replace('.py', '.xml')}"
            step_output.parent.mkdir(exist_ok=True)
        
        # 進捗コールバック
        if progress_callback:
            progress_callback(step_idx, total_steps, script_name)
        
        step_info = {
            "step": step_idx,
            "script": script_name,
            "input": str(current_input),
            "output": str(step_output),
            "success": False,
            "error": None
        }
        
        try:
            # Pythonスクリプトを実行
            result = subprocess.run(
                [sys.executable, str(script_path), str(current_input), str(step_output)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                error_msg = f"{script_name}の実行に失敗しました"
                if result.stderr:
                    error_msg += f"\nエラー詳細: {result.stderr}"
                step_info["error"] = error_msg
                execution_log["steps"].append(step_info)
                execution_log["failed_step"] = script_name
                return False, error_msg, execution_log
            
            if not step_output.exists():
                error_msg = f"出力ファイルが作成されませんでした: {script_name}"
                step_info["error"] = error_msg
                execution_log["steps"].append(step_info)
                execution_log["failed_step"] = script_name
                return False, error_msg, execution_log
            
            step_info["success"] = True
            execution_log["steps"].append(step_info)
            execution_log["completed_steps"] = step_idx
            
            current_input = step_output
        
        except subprocess.TimeoutExpired:
            error_msg = f"タイムアウト: {script_name}（{timeout}秒）"
            step_info["error"] = error_msg
            execution_log["steps"].append(step_info)
            execution_log["failed_step"] = script_name
            return False, error_msg, execution_log
        
        except Exception as e:
            error_msg = f"実行エラー: {script_name} - {str(e)}"
            step_info["error"] = error_msg
            execution_log["steps"].append(step_info)
            execution_log["failed_step"] = script_name
            return False, error_msg, execution_log
    
    # 最終結果をコピー
    try:
        import shutil
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(current_input, output_path)
        execution_log["final_output"] = str(output_path)
        return True, None, execution_log
    except Exception as e:
        return False, f"最終出力ファイルのコピーに失敗しました: {e}", execution_log


