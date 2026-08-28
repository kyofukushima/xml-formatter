"""
逆変換ページ

マークアップされたitem-subitem10までの要素をList要素に逆変換する機能を提供します。
"""
import streamlit as st
from pathlib import Path
import sys
from datetime import datetime
import tempfile
import shutil

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ユーティリティ関数のインポート
from utils.file_handler import save_uploaded_file, validate_xml_file, cleanup_temp_files
from utils.reverse_pipeline import (
    REVERSE_SCRIPT_ORDER,
    get_reverse_script_description,
    run_reverse_pipeline
)
from utils.validation import (
    validate_xml_syntax,
    validate_xml_syntax_with_script,
    validate_text_content,
    format_validation_report
)
from components.xml_preview import preview_xml_file

st.set_page_config(
    page_title="逆変換 - XML変換パイプライン",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化
if 'reverse_uploaded_file_path' not in st.session_state:
    st.session_state.reverse_uploaded_file_path = None
if 'reverse_uploaded_file_name' not in st.session_state:
    st.session_state.reverse_uploaded_file_name = None
if 'reverse_processing' not in st.session_state:
    st.session_state.reverse_processing = False
if 'reverse_processing_result' not in st.session_state:
    st.session_state.reverse_processing_result = None
if 'show_reverse_output_preview' not in st.session_state:
    st.session_state.show_reverse_output_preview = False
if 'reverse_include_paragraph' not in st.session_state:
    st.session_state.reverse_include_paragraph = True
if 'reverse_include_class' not in st.session_state:
    st.session_state.reverse_include_class = True
if 'reverse_include_appdxtable' not in st.session_state:
    st.session_state.reverse_include_appdxtable = True
if 'reverse_include_tablecolumn' not in st.session_state:
    st.session_state.reverse_include_tablecolumn = True
if 'reverse_include_remarks' not in st.session_state:
    st.session_state.reverse_include_remarks = True
if 'reverse_include_newprovision' not in st.session_state:
    st.session_state.reverse_include_newprovision = True
if 'reverse_remove_fullwidth_space' not in st.session_state:
    st.session_state.reverse_remove_fullwidth_space = False
if 'reverse_fullwidth_include_list' not in st.session_state:
    st.session_state.reverse_fullwidth_include_list = False

def main():
    """メイン関数"""
    st.title("🔄 逆変換処理")
    st.markdown("""
    マークアップされたItem要素～Subitem10要素をList要素に逆変換します。
    
    **処理順序**: Subitem10 → Subitem9 → ... → Subitem1 → Item（内側から外側へ）
    """)
    st.markdown("---")
    
    # サイドバー
    with st.sidebar:
        st.header("📋 ナビゲーション")
        st.markdown("""
        - 🏠 **ホーム** (正変換)
        - 🔄 **逆変換** (現在のページ)
        - ⚙️ **設定**
        """)
        
        st.markdown("---")
        
        st.header("ℹ️ 逆変換について")
        st.markdown("""
        **機能**:
        - Item要素 → List要素への逆変換
        - Subitem1～10要素 → List要素への逆変換
        
        **処理順序**:
        内側の階層から外側の階層へ順次処理します。
        
        **出力**:
        - 変換後のXMLファイル
        - 中間処理ファイル（オプション）
        """)
        
        st.markdown("---")
        
        # 実行されるスクリプトの一覧表示
        st.header("📝 実行スクリプト")
        st.info(f"**{len(REVERSE_SCRIPT_ORDER)}個のスクリプト**が順次実行されます")
        
        with st.expander(f"スクリプト一覧 ({len(REVERSE_SCRIPT_ORDER)}個)", expanded=False):
            for idx, script_name in enumerate(REVERSE_SCRIPT_ORDER, 1):
                description = get_reverse_script_description(script_name)
                st.markdown(f"**{idx}. {script_name}**")
                st.caption(description)
    
    # メインコンテンツ
    st.header("📤 ステップ1: XMLファイルのアップロード")
    
    uploaded_file = st.file_uploader(
        "XMLファイルを選択してください",
        type=['xml'],
        help="逆変換処理対象のXMLファイルをアップロードします（最大100MB）",
        key="reverse_file_uploader"
    )
    
    if uploaded_file is not None:
        # ファイル検証
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = Path(tmp_file.name)
        
        is_valid, error_msg = validate_xml_file(tmp_path)
        
        if is_valid:
            st.session_state.reverse_uploaded_file_path = tmp_path
            st.session_state.reverse_uploaded_file_name = uploaded_file.name
            st.success(f"✅ ファイルがアップロードされました: {uploaded_file.name}")
            
            # ファイル情報の表示
            file_size = tmp_path.stat().st_size
            st.info(f"""
            **ファイル情報**:
            - ファイル名: {uploaded_file.name}
            - ファイルサイズ: {file_size / 1024:.2f} KB
            - アップロード日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """)
            
            # XMLプレビュー
            with st.expander("📄 XMLファイルのプレビュー", expanded=False):
                preview_xml_file(tmp_path, max_lines=500)
        else:
            st.error(f"❌ {error_msg}")
            cleanup_temp_files([tmp_path])
            st.session_state.reverse_uploaded_file_path = None
    
    # ステップ2以降はファイルがアップロードされている場合のみ表示
    if st.session_state.reverse_uploaded_file_path is not None:
        st.markdown("---")
        
        # FR-003: 逆変換パイプライン処理の実行
        st.header("🚀 ステップ2: 逆変換処理の実行")
        
        st.info(f"📋 **実行されるスクリプト**: {len(REVERSE_SCRIPT_ORDER)}個（内側から外側へ順次実行）")
        
        # オプション設定
        st.markdown("### ⚙️ オプション設定")
        st.markdown("**Item要素の処理対象となる親要素を選択してください（デフォルト: すべて選択）**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            include_paragraph = st.checkbox(
                "Paragraph",
                value=st.session_state.reverse_include_paragraph,
                help="Paragraph要素内のItem要素を処理対象にします"
            )
            st.session_state.reverse_include_paragraph = include_paragraph
            
            include_class = st.checkbox(
                "Class",
                value=st.session_state.reverse_include_class,
                help="Class要素内のItem要素を処理対象にします"
            )
            st.session_state.reverse_include_class = include_class
            
            include_appdxtable = st.checkbox(
                "AppdxTable",
                value=st.session_state.reverse_include_appdxtable,
                help="AppdxTable要素（別表）内のItem要素を処理対象にします"
            )
            st.session_state.reverse_include_appdxtable = include_appdxtable
        
        with col2:
            include_tablecolumn = st.checkbox(
                "TableColumn",
                value=st.session_state.reverse_include_tablecolumn,
                help="TableColumn要素（テーブルの列）内のItem要素を処理対象にします"
            )
            st.session_state.reverse_include_tablecolumn = include_tablecolumn
            
            include_remarks = st.checkbox(
                "Remarks",
                value=st.session_state.reverse_include_remarks,
                help="Remarks要素（備考）内のItem要素を処理対象にします"
            )
            st.session_state.reverse_include_remarks = include_remarks
            
            include_newprovision = st.checkbox(
                "NewProvision",
                value=st.session_state.reverse_include_newprovision,
                help="NewProvision要素（新設規定）内のItem要素を処理対象にします"
            )
            st.session_state.reverse_include_newprovision = include_newprovision

        # 文頭全角スペース除去オプション（正変換の補填処理と対になる処理）
        st.markdown("**文頭全角スペースの扱い**")

        remove_fullwidth_space = st.checkbox(
            "逆変換前に文頭全角スペースを除去する",
            value=st.session_state.reverse_remove_fullwidth_space,
            help="正変換時に補填された文頭全角スペース（Title要素が空のItem/Subitem等の"
                 "Sentence冒頭、LineBreak=\"true\"のColumn内Sentence冒頭）を除去してから"
                 "逆変換を実行します"
        )
        st.session_state.reverse_remove_fullwidth_space = remove_fullwidth_space

        fullwidth_include_list = st.checkbox(
            "List内のSentenceも除去対象にする",
            value=st.session_state.reverse_fullwidth_include_list,
            disabled=not remove_fullwidth_space,
            help="List/ListSentence内のSentence冒頭の全角スペースも除去します"
                 "（正変換で「List内のSentenceも対象にする」を有効にした場合に合わせてください）"
        )
        st.session_state.reverse_fullwidth_include_list = fullwidth_include_list

        # 処理開始ボタン
        col1, col2 = st.columns([1, 4])
        
        with col1:
            process_button = st.button(
                "逆変換開始",
                type="primary",
                disabled=(
                    st.session_state.reverse_uploaded_file_path is None or
                    st.session_state.reverse_processing
                )
            )
        
        # 処理実行
        if process_button:
            if st.session_state.reverse_uploaded_file_path is None:
                st.error("❌ XMLファイルをアップロードしてください。")
            else:
                st.session_state.reverse_processing = True
                st.session_state.reverse_processing_result = None
                
                # 出力ファイルのパスを決定
                input_path = st.session_state.reverse_uploaded_file_path
                output_dir = project_root / "output"
                output_dir.mkdir(exist_ok=True)
                
                # アップロード時のファイル名を使用して出力ファイル名を決定
                uploaded_file_name = st.session_state.reverse_uploaded_file_name or input_path.name
                # ファイル名から拡張子を除いて「_reverse」を追加
                if uploaded_file_name.endswith('.xml'):
                    output_filename = uploaded_file_name[:-4] + '_reverse.xml'
                else:
                    output_filename = uploaded_file_name + '_reverse.xml'
                output_path = output_dir / output_filename
                
                # 中間ファイル保存ディレクトリ
                uploaded_file_name = st.session_state.reverse_uploaded_file_name or input_path.name
                intermediate_stem = Path(uploaded_file_name).stem
                intermediate_dir = output_dir / "reverse_intermediate_files" / intermediate_stem
                intermediate_dir.mkdir(parents=True, exist_ok=True)
                
                # 進捗バーとステータス表示
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(current_step, total_steps, script_name):
                    """進捗コールバック関数"""
                    progress = current_step / total_steps
                    progress_bar.progress(progress)
                    status_text.info(f"処理中 ({current_step}/{total_steps}): {script_name}")
                
                # 逆変換スクリプトディレクトリ
                reverse_script_dir = project_root / "reverse_app"
                
                # パイプライン実行
                with st.spinner("逆変換パイプライン処理を実行中..."):
                    success, error_msg, execution_log = run_reverse_pipeline(
                        input_path=input_path,
                        output_path=output_path,
                        script_dir=reverse_script_dir,
                        intermediate_dir=intermediate_dir,
                        timeout=300,
                        progress_callback=progress_callback,
                        include_paragraph=st.session_state.reverse_include_paragraph,
                        include_class=st.session_state.reverse_include_class,
                        include_appdxtable=st.session_state.reverse_include_appdxtable,
                        include_tablecolumn=st.session_state.reverse_include_tablecolumn,
                        include_remarks=st.session_state.reverse_include_remarks,
                        include_newprovision=st.session_state.reverse_include_newprovision,
                        remove_fullwidth_space=st.session_state.reverse_remove_fullwidth_space,
                        fullwidth_include_list=st.session_state.reverse_fullwidth_include_list
                    )
                
                st.session_state.reverse_processing = False
                
                if success:
                    progress_bar.progress(1.0)
                    status_text.success("✅ 逆変換処理が完了しました！")
                    
                    # 検証を自動実行
                    validation_results = {}
                    
                    # 構文検証を自動実行
                    if output_path.exists():
                        with st.spinner("構文検証を実行中..."):
                            script_dir = project_root / "scripts"
                            validation_script = script_dir / "validate_xml.py"
                            syntax_valid, syntax_error, syntax_output = validate_xml_syntax_with_script(
                                output_path,
                                validation_script if validation_script.exists() else None
                            )
                            validation_results['syntax'] = {
                                'is_valid': syntax_valid,
                                'error': syntax_error,
                                'output': syntax_output
                            }
                    
                    # テキスト内容検証を自動実行
                    original_file = st.session_state.reverse_uploaded_file_path
                    if original_file and original_file.exists() and output_path.exists():
                        with st.spinner("テキスト内容検証を実行中..."):
                            script_dir = project_root / "scripts"
                            comparison_script = script_dir / "compare_xml_text_content.py"
                            content_valid, content_error, content_output, report_data = validate_text_content(
                                original_file,
                                output_path,
                                comparison_script if comparison_script.exists() else None
                            )
                            validation_results['content'] = {
                                'is_valid': content_valid,
                                'error': content_error,
                                'output': content_output,
                                'report_data': report_data
                            }
                    
                    st.session_state.reverse_processing_result = {
                        "success": True,
                        "output_path": output_path,
                        "execution_log": execution_log,
                        "intermediate_dir": intermediate_dir,
                        "validation_results": validation_results
                    }
                else:
                    status_text.error(f"❌ エラーが発生しました: {error_msg}")
                    st.session_state.reverse_processing_result = {
                        "success": False,
                        "error": error_msg,
                        "execution_log": execution_log
                    }
        
        # 処理結果の表示
        if st.session_state.reverse_processing_result is not None:
            st.markdown("---")
            st.header("📊 処理結果")
            
            result = st.session_state.reverse_processing_result
            
            if result["success"]:
                st.success("✅ 逆変換処理が正常に完了しました")
                
                # 出力ファイル情報
                output_path = result["output_path"]
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    st.info(f"""
                    **出力ファイル情報**:
                    - ファイル名: {output_path.name}
                    - ファイルサイズ: {file_size / 1024:.2f} KB
                    - 保存場所: {output_path}
                    """)
                    
                    # ダウンロードボタン
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="📥 変換結果をダウンロード",
                            data=f.read(),
                            file_name=output_path.name,
                            mime="application/xml",
                            type="primary"
                        )
                    
                    # 出力プレビュー
                    with st.expander("📄 変換結果のプレビュー", expanded=st.session_state.show_reverse_output_preview):
                        preview_xml_file(output_path, max_lines=500)
                
                # 実行ログの表示
                execution_log = result.get("execution_log", {})
                if execution_log:
                    with st.expander("📋 実行ログ", expanded=False):
                        st.json(execution_log)
                
                # 検証結果の表示
                validation_results = result.get("validation_results", {})
                if validation_results:
                    st.markdown("---")
                    st.header("🔍 検証結果")
                    
                    # 構文検証結果
                    if 'syntax' in validation_results:
                        syntax_result = validation_results['syntax']
                        if syntax_result['is_valid']:
                            st.success("✅ XML構文検証: 正常")
                        else:
                            st.error(f"❌ XML構文検証: エラー")
                            if syntax_result['error']:
                                st.error(syntax_result['error'])
                            if syntax_result['output']:
                                st.code(syntax_result['output'], language='text')
                    
                    # テキスト内容検証結果
                    if 'content' in validation_results:
                        content_result = validation_results['content']
                        if content_result['is_valid']:
                            st.success("✅ テキスト内容検証: 正常")
                        else:
                            st.warning("⚠️ テキスト内容検証: 差分あり")
                            if content_result.get('report_data'):
                                report = format_validation_report(content_result['report_data'])
                                st.text(report)
            else:
                st.error("❌ 逆変換処理に失敗しました")
                if "error" in result:
                    st.error(f"**エラー詳細**: {result['error']}")
                
                # 実行ログの表示
                execution_log = result.get("execution_log", {})
                if execution_log:
                    with st.expander("📋 実行ログ", expanded=True):
                        st.json(execution_log)
        
        # 処理中の表示
        if st.session_state.reverse_processing:
            st.info("⏳ 逆変換処理を実行中です。しばらくお待ちください...")


if __name__ == "__main__":
    main()
