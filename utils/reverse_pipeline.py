"""
逆変換パイプライン実行ユーティリティ

逆変換スクリプトを順次実行するパイプライン処理を提供します。
"""
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Dict


# 逆変換スクリプトの実行順序（内側から外側へ）
REVERSE_SCRIPT_ORDER = [
    "reverse_convert_subitem10.py",
    "reverse_convert_subitem9.py",
    "reverse_convert_subitem8.py",
    "reverse_convert_subitem7.py",
    "reverse_convert_subitem6.py",
    "reverse_convert_subitem5.py",
    "reverse_convert_subitem4.py",
    "reverse_convert_subitem3.py",
    "reverse_convert_subitem2.py",
    "reverse_convert_subitem1.py",
    "reverse_convert_item.py",
]


def get_reverse_script_description(script_name: str) -> str:
    """
    逆変換スクリプトの説明を取得
    
    Args:
        script_name: スクリプト名
    
    Returns:
        スクリプトの説明
    """
    descriptions = {
        "reverse_convert_subitem10.py": "Subitem10 → List 逆変換",
        "reverse_convert_subitem9.py": "Subitem9 → List 逆変換",
        "reverse_convert_subitem8.py": "Subitem8 → List 逆変換",
        "reverse_convert_subitem7.py": "Subitem7 → List 逆変換",
        "reverse_convert_subitem6.py": "Subitem6 → List 逆変換",
        "reverse_convert_subitem5.py": "Subitem5 → List 逆変換",
        "reverse_convert_subitem4.py": "Subitem4 → List 逆変換",
        "reverse_convert_subitem3.py": "Subitem3 → List 逆変換",
        "reverse_convert_subitem2.py": "Subitem2 → List 逆変換",
        "reverse_convert_subitem1.py": "Subitem1 → List 逆変換",
        "reverse_convert_item.py": "Item → List 逆変換",
    }
    return descriptions.get(script_name, "逆変換スクリプト")


def run_reverse_pipeline(
    input_path: Path,
    output_path: Path,
    script_dir: Path,
    intermediate_dir: Optional[Path] = None,
    timeout: int = 300,
    progress_callback: Optional[callable] = None
) -> Tuple[bool, Optional[str], Dict[str, any]]:
    """
    逆変換パイプラインを実行
    
    Args:
        input_path: 入力XMLファイルのパス
        output_path: 出力XMLファイルのパス
        script_dir: 逆変換スクリプトディレクトリのパス
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
        "total_steps": len(REVERSE_SCRIPT_ORDER),
        "completed_steps": 0,
        "failed_step": None,
        "steps": []
    }
    
    current_input = input_path
    total_steps = len(REVERSE_SCRIPT_ORDER)
    
    for step_idx, script_name in enumerate(REVERSE_SCRIPT_ORDER, 1):
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
            # Pythonスクリプトを実行（カレントディレクトリをreverse_appに設定）
            result = subprocess.run(
                [sys.executable, str(script_path), str(current_input), str(step_output)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(script_dir)  # カレントディレクトリをreverse_appに設定
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
