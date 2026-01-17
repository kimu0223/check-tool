import streamlit as st
import requests
import pandas as pd
import time

# ==========================================
# ★設定エリア
# Manager自身の中にあるAPIサーバー宛なので localhost でOK
API_URL = "http://127.0.0.1:8000"
# ==========================================

st.title("GRC 順位チェック司令室 🚀")

# --- サイドバー：検索設定 ---
st.sidebar.header("検索設定")
target_url = st.sidebar.text_input("対象URL (部分一致)", "example.com")
min_sleep = st.sidebar.number_input("最小待機(秒)", 5, 300, 5)
max_sleep = st.sidebar.number_input("最大待機(秒)", 10, 600, 10)

# --- メインエリア：キーワード入力 ---
st.subheader("キーワード入力")
keywords_text = st.text_area("1行に1つキーワードを入力", "藤岡市 整体\n群馬県 SEO")

# --- 実行ボタン ---
if st.button("検索開始 (Workerへ指令を送信)"):
    keywords = [k.strip() for k in keywords_text.split("\n") if k.strip()]
    
    if not keywords:
        st.warning("キーワードを入力してください")
    else:
        # 1. タスクデータの作成
        tasks = []
        for kw in keywords:
            tasks.append({
                "keyword": kw,
                "target_url": target_url,
                "min_sleep": min_sleep,
                "max_sleep": max_sleep
            })
        
        # 2. APIサーバーへ送信 (POST)
        try:
            res = requests.post(f"{API_URL}/add_tasks", json=tasks)
            if res.status_code == 200:
                st.success(f"📨 {len(tasks)} 件の指令を送信しました！Workerが動き出します。")
            else:
                st.error(f"送信エラー: {res.status_code}")
        except Exception as e:
            st.error(f"サーバーに繋がりません。start_manager.bat を実行していますか？\nエラー: {e}")

st.markdown("---")

# --- 結果のモニタリング表示 ---
st.subheader("📡 リアルタイム結果 (自動更新)")

if st.button("最新結果を取得"):
    st.rerun()

try:
    # サーバーから結果一覧をもらう (GET)
    res = requests.get(f"{API_URL}/results")
    if res.status_code == 200:
        data = res.json()
        if data:
            df = pd.DataFrame(data)
            # 見やすく並べ替え
            st.dataframe(df[["check_date", "keyword", "yahoo_rank", "google_rank", "target_url"]])
        else:
            st.info("まだ結果はありません。Workerが収集中です...")
    else:
        st.error("結果の取得に失敗しました")
except:
    st.warning("サーバーと通信できません")