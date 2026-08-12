"""
XML変換パイプライン処理システム - Streamlit Webアプリケーション

メインアプリケーションファイル
"""
import streamlit as st
from pathlib import Path
import sys
from datetime import datetime
import tempfile
import shutil
import subprocess
import zipfile
import io

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ユーティリティ関数のインポート
from utils.file_handler import save_uploaded_file, validate_xml_file, cleanup_temp_files
from utils.pipeline import (
    get_available_scripts,
    get_script_description,
    run_pipeline,
    ENUMERATION_AWARE_SCRIPTS
)
from utils.validation import (
    validate_xml_syntax,
    validate_xml_syntax_with_script,
    validate_text_content,
    format_validation_report
)
from utils.label_analyzer import analyze_xml_labels
from components.xml_preview import preview_xml_file

# ページ設定
st.set_page_config(
    page_title="XML変換パイプライン",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化
if 'uploaded_file_path' not in st.session_state:
    st.session_state.uploaded_file_path = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'processing_result' not in st.session_state:
    st.session_state.processing_result = None
if 'selected_scripts' not in st.session_state:
    st.session_state.selected_scripts = []
if 'show_output_preview' not in st.session_state:
    st.session_state.show_output_preview = False
if 'apply_fullwidth_space' not in st.session_state:
    st.session_state.apply_fullwidth_space = False
if 'fullwidth_space_include_list' not in st.session_state:
    st.session_state.fullwidth_space_include_list = False
if 'fullwidth_space_exclude_paren' not in st.session_state:
    st.session_state.fullwidth_space_exclude_paren = False
if 'preserve_enumeration' not in st.session_state:
    st.session_state.preserve_enumeration = False
if 'preserve_linebreak_list' not in st.session_state:
    st.session_state.preserve_linebreak_list = False

def main():
    """メイン関数"""
    st.title("📄 XML変換パイプライン処理システム")
    st.markdown("---")
    
    # サイドバー
    with st.sidebar:
        st.header("📋 ナビゲーション")
        st.markdown("""
        - 🏠 **ホーム** (現在のページ)
        - 🔄 **逆変換**
        - ⚙️ **設定**
        - 📋 **履歴** (準備中)
        """)
        
        st.markdown("---")
        
        # FR-002: 変換スクリプトの選択
        st.header("⚙️ 変換スクリプトの選択")
        
        script_dir = project_root / "scripts"
        available_scripts = get_available_scripts(script_dir)
        
        if not available_scripts:
            st.warning("⚠️ 変換スクリプトが見つかりません。")
        else:
            # デフォルトで推奨順序のスクリプトを選択
            if not st.session_state.selected_scripts:
                st.session_state.selected_scripts = available_scripts[:15]  # 推奨順序の15個
            
            selected_scripts = st.multiselect(
                "実行するスクリプトを選択",
                options=available_scripts,
                default=st.session_state.selected_scripts,
                help="実行する変換スクリプトを選択します（複数選択可能）"
            )
            
            st.session_state.selected_scripts = selected_scripts
            
            # 選択されたスクリプト数の表示
            if selected_scripts:
                st.success(f"✅ {len(selected_scripts)}個のスクリプトが選択されています")
                
                # 選択されたスクリプトの一覧（折りたたみ可能）
                with st.expander(f"選択されたスクリプト ({len(selected_scripts)}個)", expanded=False):
                    for idx, script_name in enumerate(selected_scripts, 1):
                        description = get_script_description(script_name)
                        st.markdown(f"**{idx}. {script_name}**")
                        st.caption(description)
            else:
                st.warning("⚠️ 少なくとも1つのスクリプトを選択してください。")

        st.markdown("---")

        # 列記List保護オプション（告示データ整備方針パターン20D対応）
        st.header("📑 列記Listの保護")
        preserve_enumeration = st.checkbox(
            "列記のList（Column構成）を変換せず保持する",
            value=st.session_state.preserve_enumeration,
            help="Columnが2つ以上のListのうち、1つ目がラベル（番号等）で2つ目がテキストの"
                 "「番号+見出し」構成のみを変換対象とし、1つ目と2つ目の種別が同一"
                 "（テキスト同士・ラベル同士）のListは列記とみなして変換せずそのまま残します。"
                 "Columnが1つのListは従来どおり変換されます。"
                 "従来データの変換結果が変わるため、告示データ整備方針に沿ったデータの場合のみONにしてください。"
        )
        st.session_state.preserve_enumeration = preserve_enumeration

        preserve_linebreak_list = st.checkbox(
            "LineBreak付きColumnを含むListを変換せず保持する",
            value=st.session_state.preserve_linebreak_list,
            help="LineBreak=\"true\"のColumn（改行して表示する指示）を含むListを変換対象から除外します。"
                 "変換するとColumnラッパーが捨てられLineBreak属性（改行表現）が失われるため、"
                 "告示データ整備方針に沿ってLineBreakを使用しているデータではONを推奨します。"
        )
        st.session_state.preserve_linebreak_list = preserve_linebreak_list

        st.markdown("---")

        # 文頭全角スペース補填オプション（告示マークアップ修正案対応）
        st.header("🔤 文頭全角スペース補填")
        apply_fullwidth_space = st.checkbox(
            "変換後に文頭全角スペースを補填する",
            value=st.session_state.apply_fullwidth_space,
            help="Title要素が空のItem/Subitem1～10のSentence冒頭、および"
                 "LineBreak=\"true\"のColumn内Sentence冒頭に全角スペースを挿入します。"
                 "テキスト内容検証は補填前のファイルに対して実行されます。"
        )
        st.session_state.apply_fullwidth_space = apply_fullwidth_space

        fullwidth_space_include_list = st.checkbox(
            "List内のSentenceも対象にする",
            value=st.session_state.fullwidth_space_include_list,
            disabled=not apply_fullwidth_space,
            help="List/ListSentence内のSentence冒頭にも全角スペースを挿入します"
                 "（整備方針資料上「要確認」のためデフォルトは対象外）"
        )
        st.session_state.fullwidth_space_include_list = fullwidth_space_include_list

        fullwidth_space_exclude_paren = st.checkbox(
            "「（」で始まるSentenceは対象外にする",
            value=st.session_state.fullwidth_space_exclude_paren,
            disabled=not apply_fullwidth_space,
            help="「（注）…」等の括弧書きで始まるSentenceに全角スペースを挿入しません。"
                 "括弧書きを字下げするかどうかは告示ごとの官報体裁に合わせて選択してください。"
        )
        st.session_state.fullwidth_space_exclude_paren = fullwidth_space_exclude_paren

        # page_linkはマルチページ実行時のみ有効（テストランナー等では利用不可）
        try:
            st.page_link(
                "pages/04_🔤_全角スペース補填設定.py",
                label="XML例を確認しながら設定する",
                icon="🔤"
            )
        except Exception:
            st.caption("XML例は「全角スペース補填設定」ページで確認できます。")

        st.markdown("---")
        st.header("ℹ️ 情報")
        st.markdown("""
        **バージョン**: 1.3.0
        
        **機能**:
        - XMLファイルのアップロード
        - ラベル種類の判定（自動実行）
        - 変換スクリプトの選択
        - パイプライン処理の実行
        - 検証機能
        - ラベル設定管理
        """)
    
    # メインコンテンツ
    st.header("📤 ステップ1: XMLファイルのアップロード")
    
    # FR-001: XMLファイルのアップロード
    uploaded_file = st.file_uploader(
        "XMLファイルを選択してください",
        type=['xml'],
        help="処理対象のXMLファイルをアップロードします（最大100MB）"
    )
    
    if uploaded_file is not None:
        # ファイル検証
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = Path(tmp_file.name)
        
        is_valid, error_msg = validate_xml_file(tmp_path)
        
        if is_valid:
            st.session_state.uploaded_file_path = tmp_path
            st.session_state.uploaded_file_name = uploaded_file.name
            st.success(f"✅ ファイルがアップロードされました: {uploaded_file.name}")
            
            # ファイル情報の表示
            file_size = tmp_path.stat().st_size
            st.info(f"""
            **ファイル情報**:
            - ファイル名: {uploaded_file.name}
            - ファイルサイズ: {file_size / 1024:.2f} KB
            - アップロード日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """)
            
            # FR-010: XMLプレビュー
            with st.expander("📄 XMLファイルのプレビュー", expanded=False):
                preview_xml_file(tmp_path, max_lines=500)
            
            # ラベル種類の判定を自動実行
            with st.spinner("ラベル種類を判定中..."):
                try:
                    result_df, has_column_list = analyze_xml_labels(tmp_path)
                    if has_column_list:
                        st.session_state.label_analysis_result = result_df
                        st.session_state.has_column_list = True
                    else:
                        st.session_state.label_analysis_result = None
                        st.session_state.has_column_list = False
                except Exception as e:
                    st.warning(f"⚠️ ラベル種類の判定中にエラーが発生しました: {e}")
                    st.session_state.label_analysis_result = None
                    st.session_state.has_column_list = None
        else:
            st.error(f"❌ {error_msg}")
            cleanup_temp_files([tmp_path])
            st.session_state.uploaded_file_path = None
    
    # ステップ2以降はファイルがアップロードされている場合のみ表示
    if st.session_state.uploaded_file_path is not None:
        st.markdown("---")
        
        # ラベル種類判定セクション
        # ラベル種類判定の結果をセッション状態に初期化
        if 'label_analysis_result' not in st.session_state:
            st.session_state.label_analysis_result = None
        if 'has_column_list' not in st.session_state:
            st.session_state.has_column_list = None
        
        # expanderで表示/非表示を切り替え
        with st.expander("🔍 ラベルの種類を確認する", expanded=False):
            # ColumnありのList要素がない場合
            if st.session_state.has_column_list is False:
                st.info("columnありのList要素なし")
            elif st.session_state.label_analysis_result is not None:
                result_df = st.session_state.label_analysis_result
                
                # 不明な値の件数をチェック
                unknown_count = len(result_df[result_df['ラベル要素'] == '不明'])
                if unknown_count > 0:
                    st.warning(f"⚠️ 不明な値が{unknown_count}個あります")
                
                # 結果テーブルの表示
                st.subheader("判定結果")
                st.dataframe(
                    result_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # CSVダウンロードボタン
                csv = result_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 結果をCSVでダウンロード",
                    data=csv,
                    file_name=f"{Path(st.session_state.uploaded_file_name).stem}_label_analysis.csv",
                    mime="text/csv"
                )
            else:
                st.info("ラベル種類の判定結果がありません。ファイルをアップロードしてください。")
        
        st.markdown("---")
        
        # FR-003: パイプライン処理の実行
        st.header("🚀 ステップ2: パイプライン処理の実行")
        
        # サイドバーで選択されたスクリプトの確認メッセージ
        if st.session_state.selected_scripts:
            st.info(f"📋 **選択されたスクリプト**: {len(st.session_state.selected_scripts)}個（サイドバーで変更可能）")
        else:
            st.warning("⚠️ サイドバーで変換スクリプトを選択してください。")
        
        # 処理開始ボタン
        col1, col2 = st.columns([1, 4])
        
        with col1:
            process_button = st.button(
                "処理開始",
                type="primary",
                disabled=(
                    st.session_state.uploaded_file_path is None or
                    not st.session_state.selected_scripts or
                    st.session_state.processing
                )
            )
        
        # 処理実行
        if process_button:
            if st.session_state.uploaded_file_path is None:
                st.error("❌ XMLファイルをアップロードしてください。")
            elif not st.session_state.selected_scripts:
                st.error("❌ 変換スクリプトを選択してください。")
            else:
                st.session_state.processing = True
                st.session_state.processing_result = None
                
                # 出力ファイルのパスを決定
                input_path = st.session_state.uploaded_file_path
                output_dir = project_root / "output"
                output_dir.mkdir(exist_ok=True)
                
                # アップロード時のファイル名を使用して出力ファイル名を決定
                uploaded_file_name = st.session_state.uploaded_file_name or input_path.name
                # ファイル名から拡張子を除いて「_final」を追加
                if uploaded_file_name.endswith('.xml'):
                    output_filename = uploaded_file_name[:-4] + '_final.xml'
                else:
                    output_filename = uploaded_file_name + '_final.xml'
                output_path = output_dir / output_filename
                
                # 中間ファイル保存ディレクトリ
                # アップロード時のファイル名（拡張子なし）を使用
                uploaded_file_name = st.session_state.uploaded_file_name or input_path.name
                intermediate_stem = Path(uploaded_file_name).stem
                intermediate_dir = output_dir / "intermediate_files" / intermediate_stem
                intermediate_dir.mkdir(parents=True, exist_ok=True)
                
                # 進捗バーとステータス表示
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(current_step, total_steps, script_name):
                    """進捗コールバック関数"""
                    progress = current_step / total_steps
                    progress_bar.progress(progress)
                    status_text.info(f"処理中 ({current_step}/{total_steps}): {script_name}")
                
                # List保護オプションがONの場合、対応スクリプトにフラグを渡す
                preserve_flags = []
                if st.session_state.preserve_enumeration:
                    preserve_flags.append('--preserve-enumeration')
                if st.session_state.preserve_linebreak_list:
                    preserve_flags.append('--preserve-linebreak-list')
                extra_args_by_script = None
                if preserve_flags:
                    extra_args_by_script = {
                        script_name: preserve_flags
                        for script_name in st.session_state.selected_scripts
                        if script_name in ENUMERATION_AWARE_SCRIPTS
                    }

                # パイプライン実行
                with st.spinner("パイプライン処理を実行中..."):
                    success, error_msg, execution_log = run_pipeline(
                        input_path=input_path,
                        output_path=output_path,
                        scripts=st.session_state.selected_scripts,
                        script_dir=script_dir,
                        intermediate_dir=intermediate_dir,
                        timeout=300,
                        progress_callback=progress_callback,
                        extra_args_by_script=extra_args_by_script
                    )

                # 文頭全角スペース補填（(a)方式: テキスト内容検証は補填前のファイルに対して実施）
                text_validation_target = output_path
                fullwidth_space_applied = False
                if success and st.session_state.apply_fullwidth_space:
                    pre_space_path = intermediate_dir / f"{intermediate_stem}_before_fullwidth_space.xml"
                    postprocess_script = script_dir / "postprocess_fullwidth_space.py"
                    try:
                        shutil.copy(output_path, pre_space_path)
                        cmd = [sys.executable, str(postprocess_script),
                               str(pre_space_path), str(output_path)]
                        if st.session_state.fullwidth_space_include_list:
                            cmd.append('--include-list')
                        if st.session_state.fullwidth_space_exclude_paren:
                            cmd.append('--exclude-paren')
                        with st.spinner("文頭全角スペースを補填中..."):
                            pp_result = subprocess.run(
                                cmd, capture_output=True, text=True, timeout=300
                            )
                        if pp_result.returncode != 0:
                            success = False
                            error_msg = "文頭全角スペース補填に失敗しました"
                            if pp_result.stderr:
                                error_msg += f"\nエラー詳細: {pp_result.stderr}"
                        else:
                            # テキスト内容検証は補填前のファイルと比較する
                            text_validation_target = pre_space_path
                            fullwidth_space_applied = True
                    except Exception as e:
                        success = False
                        error_msg = f"文頭全角スペース補填でエラーが発生しました: {e}"

                st.session_state.processing = False
                
                if success:
                    progress_bar.progress(1.0)
                    status_text.success("✅ パイプライン処理が完了しました！")
                    
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
                    original_file = st.session_state.uploaded_file_path
                    if original_file and original_file.exists() and output_path.exists():
                        with st.spinner("テキスト内容検証を実行中..."):
                            script_dir = project_root / "scripts"
                            comparison_script = script_dir / "compare_xml_text_content.py"
                            content_valid, content_error, content_output, report_data = validate_text_content(
                                original_file,
                                text_validation_target,
                                comparison_script if comparison_script.exists() else None
                            )
                            validation_results['content'] = {
                                'is_valid': content_valid,
                                'error': content_error,
                                'output': content_output,
                                'report_data': report_data
                            }
                    
                    st.session_state.processing_result = {
                        "success": True,
                        "output_path": output_path,
                        "execution_log": execution_log,
                        "intermediate_dir": intermediate_dir,
                        "validation_results": validation_results,
                        "fullwidth_space_applied": fullwidth_space_applied
                    }
                else:
                    status_text.error(f"❌ エラーが発生しました: {error_msg}")
                    st.session_state.processing_result = {
                        "success": False,
                        "error": error_msg,
                        "execution_log": execution_log
                    }
                    
                    # エラー詳細の表示
                    if execution_log and execution_log.get("steps"):
                        with st.expander("エラー詳細", expanded=True):
                            for step_info in execution_log["steps"]:
                                if not step_info.get("success", False):
                                    st.error(f"ステップ {step_info['step']}: {step_info['script']}")
                                    if step_info.get("error"):
                                        st.code(step_info["error"], language=None)
        
        st.markdown("---")
        
        # FR-007, FR-008, FR-009: 検証機能（自動実行・自動表示）
        st.header("🔍 ステップ3: 検証")
        
        if st.session_state.processing_result and st.session_state.processing_result.get("success"):
            validation_results = st.session_state.processing_result.get("validation_results", {})
            
            # 左右カラムで検証結果を表示
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 XML構文検証")
                st.markdown("処理済みXMLファイルの構文が正しいかどうかを検証します。")
                
                if 'syntax' in validation_results:
                    syntax_result = validation_results['syntax']
                    if syntax_result['is_valid']:
                        st.success("✅ XML構文は正しいです。")
                        if syntax_result.get('output'):
                            with st.expander("検証結果の詳細", expanded=False):
                                st.code(syntax_result['output'], language=None)
                    else:
                        st.error(f"❌ {syntax_result.get('error', '構文エラーが検出されました')}")
                        if syntax_result.get('output'):
                            with st.expander("検証結果の詳細", expanded=True):
                                st.code(syntax_result['output'], language=None)
                else:
                    st.info("検証結果がありません。")
            
            with col2:
                st.subheader("📝 テキスト内容検証")
                st.markdown("元のXMLファイルと処理後のXMLファイルのテキスト内容が一致しているか検証します。")
                if st.session_state.processing_result.get("fullwidth_space_applied"):
                    st.caption("※ 全角スペース補填**前**のファイルに対して検証しています（補填による差分は検証対象外）")
                
                if 'content' in validation_results:
                    content_result = validation_results['content']
                    if content_result['is_valid']:
                        st.success("✅ テキスト内容は一致しています。")
                        if content_result.get('report_data'):
                            with st.expander("検証結果の詳細", expanded=False):
                                st.text(format_validation_report(content_result['report_data']))
                    else:
                        st.error(f"❌ {content_result.get('error', 'テキスト内容の不一致が検出されました')}")
                        if content_result.get('report_data'):
                            with st.expander("検証結果の詳細", expanded=True):
                                st.text(format_validation_report(content_result['report_data']))
                                if content_result['report_data'].get("errors"):
                                    st.error(f"**エラー数**: {len(content_result['report_data']['errors'])}")
                else:
                    st.info("検証結果がありません。")
        else:
            st.info("処理が完了すると、ここに検証結果が自動的に表示されます。")
        
        st.markdown("---")
        
        # FR-004: 処理済みXMLファイルのダウンロード
        st.header("📥 ステップ4: 処理済みXMLファイルのダウンロード")
        
        if st.session_state.processing_result and st.session_state.processing_result.get("success"):
            output_path = st.session_state.processing_result["output_path"]
            
            if output_path.exists():
                with open(output_path, 'rb') as f:
                    st.download_button(
                        label="📥 処理済みXMLファイルをダウンロード",
                        data=f.read(),
                        file_name=output_path.name,
                        mime="application/xml"
                    )
                
                st.info(f"**出力ファイル**: {output_path.name}")
                
                # FR-010: XMLプレビュー
                show_preview = st.checkbox("📄 処理済みXMLファイルをプレビュー", value=False)
                if show_preview:
                    with st.expander("📄 処理済みXMLファイルのプレビュー", expanded=True):
                        preview_xml_file(output_path, max_lines=500)
            else:
                st.warning("⚠️ 出力ファイルが見つかりません。")
        else:
            st.info("処理が完了すると、ここにダウンロードボタンが表示されます。")
        
        st.markdown("---")
        
        # FR-011: 中間ファイルのダウンロード
        st.subheader("📦 ステップ4-1: 中間ファイルのダウンロード")
        
        if st.session_state.processing_result and st.session_state.processing_result.get("success"):
            intermediate_dir = st.session_state.processing_result.get("intermediate_dir")
            
            if intermediate_dir and Path(intermediate_dir).exists():
                intermediate_path = Path(intermediate_dir)
                intermediate_files = sorted(intermediate_path.glob("*.xml"))
                
                if intermediate_files:
                    st.info(f"**中間ファイル数**: {len(intermediate_files)}個")
                    
                    # ZIPファイルとして一括ダウンロード
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for file_path in intermediate_files:
                            zip_file.write(file_path, file_path.name)
                    
                    zip_buffer.seek(0)
                    zip_filename = f"{intermediate_path.name}_intermediate_files.zip"
                    
                    st.download_button(
                        label="📦 すべての中間ファイルをZIPでダウンロード",
                        data=zip_buffer.getvalue(),
                        file_name=zip_filename,
                        mime="application/zip",
                        key="download_all_intermediate"
                    )
                    
                    st.markdown("---")
                    
                    # ファイル一覧を表示
                    with st.expander("📋 中間ファイル一覧（個別ダウンロード）", expanded=False):
                        for idx, file_path in enumerate(intermediate_files, 1):
                            file_size = file_path.stat().st_size
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                st.text(f"{idx}. {file_path.name}")
                            
                            with col2:
                                st.caption(f"{file_size / 1024:.2f} KB")
                            
                            with col3:
                                with open(file_path, 'rb') as f:
                                    st.download_button(
                                        label="📥",
                                        data=f.read(),
                                        file_name=file_path.name,
                                        mime="application/xml",
                                        key=f"download_intermediate_{idx}"
                                    )
                    
                    st.caption("💡 ZIPファイルで一括ダウンロードするか、個別にダウンロードできます")
                else:
                    st.info("中間ファイルは生成されていません。")
            else:
                st.info("中間ファイルディレクトリが見つかりません。")
        else:
            st.info("処理が完了すると、ここに中間ファイル一覧が表示されます。")
        
        st.markdown("---")
    
    # ヘルプセクション
    with st.expander("📚 ヘルプ", expanded=False):
        st.markdown("""
        ### 使い方
        
        1. **XMLファイルのアップロード**
           - 「ファイルを選択」ボタンをクリックしてXMLファイルを選択
           - ファイルサイズは最大100MBまで
        
        2. **変換スクリプトの選択**
           - 実行したい変換スクリプトを選択（複数選択可能）
           - デフォルトで推奨順序のスクリプトが選択されています
        
        3. **パイプライン処理の実行**
           - 「処理開始」ボタンをクリック
           - 処理中は進捗バーで進捗を確認できます
        
        4. **結果のダウンロード**
           - 処理が完了すると、ダウンロードボタンが表示されます
           - クリックして処理済みXMLファイルをダウンロード
        
        ### トラブルシューティング
        
        - **ファイルがアップロードできない**: ファイルサイズが100MBを超えていないか確認してください
        - **処理が失敗する**: エラー詳細を確認し、入力XMLファイルの形式を確認してください
        - **スクリプトが見つからない**: scriptsディレクトリに変換スクリプトが存在するか確認してください
        """)

if __name__ == "__main__":
    main()

