"""
XML変換パイプライン処理システム - Streamlit Webアプリケーション

エントリポイント（ナビゲーションルーター）
各ページの実体は app_pages/ 配下にあります。
ホーム選択時は、ナビゲーションの下（サイドバー内）にホームページ自身の
個別設定（変換スクリプトの選択等）が表示されます。
"""
import streamlit as st

page = st.navigation({
    "": [
        st.Page("app_pages/home.py", title="ホーム", icon="🏠", default=True),
        st.Page("app_pages/reverse_conversion.py", title="逆変換", icon="🔄"),
        st.Page("app_pages/list_check.py", title="List有無判定", icon="📊"),
        st.Page("app_pages/fullwidth_space_tool.py",
                title="文頭スペース補填", icon="🈳"),
        st.Page("app_pages/delivery_check.py", title="納品前検証", icon="✅"),
    ],
    "設定": [
        st.Page("app_pages/settings.py", title="ラベル設定管理", icon="⚙️"),
        st.Page("app_pages/fullwidth_space_settings.py",
                title="全角スペース補填設定", icon="🔤"),
        st.Page("app_pages/enumeration_settings.py",
                title="列記List保護設定", icon="📑"),
    ],
})

page.run()
