import streamlit as st
import pandas as pd
from scraper import RankScraper
import time
from datetime import datetime
import os
from fpdf import FPDF
import glob 
from concurrent.futures import ThreadPoolExecutor
import threading
import random

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="fpdf")

# --- 設定 ---
DB_FILE = "ranking_data.db"

# --- グローバル変数 ---
high_rank_counter = 0
counter_lock = threading.Lock()

# --- ページ設定 ---
st.set_page_config(
    page_title="検索順位チェックツール",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- PDF生成関数 ---
def create_pdf(df):
    local_font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    if not os.path.exists(local_font_dir): return "NO_FOLDER"
    ttf_files = glob.glob(os.path.join(local_font_dir, "*.ttf"))
    if not ttf_files: return "NO_FILE"
    font_path = ttf_files[0]

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('Japanese', '', font_path, uni=True)
        pdf.set_font('Japanese', '', 11)
        pdf.set_font_size(16)
        pdf.cell(0, 10, '検索順位レポート', 0, 1, 'C')
        pdf.ln(5)

        pdf.set_font_size(10)
        pdf.set_fill_color(240, 240, 240)
        headers = ['キーワード', 'Yahoo順位', '対象URL']
        col_widths = [60, 30, 100]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C', 1)
        pdf.ln()

        pdf.set_font_size(9)
        for _, row in df.iterrows():
            pdf.cell(col_widths[0], 8, str(row['キーワード'])[:25], 1, 0, 'L')
            pdf.cell(col_widths[1], 8, str(row['Yahoo順位']), 1, 0, 'C')
            pdf.cell(col_widths[2], 8, str(row['対象URL'])[:50], 1, 0, 'L')
            pdf.ln()
        
        if pdf.get_y() > 250: pdf.add_page()
        pdf.set_y(-20)
        pdf.set_font_size(10)
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        pdf.cell(0, 10, f'実施日時: {current_date}', 0, 0, 'R')
        return pdf.output(dest='S').encode('latin1')
    except: return "ERROR"

# --- テキスト生成関数 ---
def generate_report_text(df, target_url):
    def rank_to_int(val): return int(val) if str(val).isdigit() else 9999
    text = "【順位データ】※返信不要、現在テスト運用中です。\n\nお疲れ様です。\n【ロングテールキーワード】のキーワードを元に既存サイトの順位チェックをしたものになります。\nご参考までにお送り致します。\n\n\n"
    text += f"{target_url}\n\n"
    text += "Y=Yahoo!\n\n"
    df['sort_key'] = df['Yahoo順位'].apply(rank_to_int)
    for _, row in df.sort_values(by='sort_key').iterrows():
        y = str(row['Yahoo順位'])
        y_d = f"{y}位" if y.isdigit() else y
        text += f"Y：{y_d}　{row['キーワード']}\n"
    return text

# --- スクレイピングタスク ---
def scrape_keyword_task(args):
    global high_rank_counter
    kw, url, min_s, max_s = args
    
    scraper = RankScraper(show_browser=True)
    data = scraper.check_rank(kw, url, min_s, max_s)
    
    # 連続上位ランク時の微調整
    rank_str = data["yahoo_rank"]
    is_top10 = False
    if rank_str.isdigit() and int(rank_str) <= 10:
        is_top10 = True
            
    with counter_lock:
        if is_top10:
            high_rank_counter += 1
            if high_rank_counter >= 5:
                time.sleep(10)
                high_rank_counter = 0
        else:
            high_rank_counter = 0

    # 指定された秒数分待機
    time.sleep(random.uniform(min_s, max_s))
            
    return data

# --- メイン画面 ---
st.title("検索順位チェックツール")
st.markdown("Yahoo! の検索順位を一括チェックします。（50位まで調査）")

# ブロック検知時の警告表示エリア
block_alert = st.empty()

with st.sidebar:
    st.header("設定・入力")
    target_url = st.text_input("対象URL (部分一致)", placeholder="例: example.com")
    keywords_text = st.text_area("キーワード (1行に1つ)", height=200, placeholder="藤岡市 整体\n...")
    
    st.markdown("### 待機時間設定 (秒)")
    c1, c2 = st.columns(2)
    # ★変更: デフォルトを 8秒〜10秒 に設定
    with c1: min_sleep = st.number_input("最小", value=8, min_value=1)
    with c2: max_sleep = st.number_input("最大", value=10, min_value=1)
    
    st.info("💡 32キーワード経過時に2分休憩が入ります。")
    st.info("💡 完了後は次の開始ボタンが3分間ロックされます。")
    st.markdown("---")
    
    # 開始ボタン制御エリア
    start_btn_area = st.empty()
    start_btn = start_btn_area.button("順位チェック開始", type="primary", width='stretch')
    
    stop_btn = st.button("中断", type="secondary", width='stretch')

# ステート管理
if 'is_running' not in st.session_state: st.session_state.is_running = False
if 'results' not in st.session_state: st.session_state.results = []
if 'should_cooldown' not in st.session_state: st.session_state.should_cooldown = False

if stop_btn:
    st.session_state.is_running = False
    st.warning("中断しました。")

# --- チェック実行処理 ---
if start_btn and not st.session_state.is_running:
    # 警告クリア・初期化
    block_alert.empty()
    high_rank_counter = 0
    st.session_state.should_cooldown = False 
    
    if not target_url or not keywords_text.strip():
        st.sidebar.error("URLとキーワードを入力してください。")
    else:
        st.session_state.is_running = True
        st.session_state.results = []
        
        keywords = [k.strip() for k in keywords_text.split('\n') if k.strip()]
        total_keywords = len(keywords)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        table_placeholder = st.empty()

        BATCH_SIZE = 2
        
        with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
            for i in range(0, total_keywords, BATCH_SIZE):
                if not st.session_state.is_running: break
                
                # 32キーワード目（16ループ目）で強制的に2分休憩
                if i == 32:
                    rest_time = 120 # 2分間
                    for r in range(rest_time, 0, -1):
                        status_text.warning(f"☕ [中間休憩] 32件を超えました。ブロック回避のため休憩中... 残り {r} 秒")
                        time.sleep(1)
                        if not st.session_state.is_running: break
                    if not st.session_state.is_running: break

                batch_keywords = keywords[i : i + BATCH_SIZE]
                status_text.text(f"チェック中 ({i+1}〜{min(i+BATCH_SIZE, total_keywords)}/{total_keywords}): {', '.join(batch_keywords)}")
                
                args_list = [(kw, target_url, min_sleep, max_sleep) for kw in batch_keywords]
                
                results = list(executor.map(scrape_keyword_task, args_list))
                
                for data in results:
                    # エラー判定
                    if data["yahoo_rank"] == "エラー":
                        block_alert.error(
                            "ブロックされた可能性があります。\n"
                            "数時間お時間空けて頂くか、PCをシャットダウン、Wi-Fiを変えてみて再度試してください。"
                        )

                    st.session_state.results.append({
                        "キーワード": data["keyword"],
                        "Yahoo順位": data["yahoo_rank"],
                        "対象URL": data["target_url"],
                        "取得日時": data["check_date"]
                    })
                
                progress_bar.progress(min((i + BATCH_SIZE) / total_keywords, 1.0))
                temp_df = pd.DataFrame(st.session_state.results)
                table_placeholder.dataframe(temp_df.iloc[::-1], width='stretch')

        if st.session_state.is_running:
            status_text.success("✅ 全キーワードのチェックが完了しました。")
            st.session_state.should_cooldown = True 

        st.session_state.is_running = False

# --- 結果表示 ---
if st.session_state.results:
    st.divider()
    st.subheader("チェック結果一覧")
    df_final = pd.DataFrame(st.session_state.results)
    st.dataframe(df_final, width='stretch', hide_index=True)

    c_dl1, c_dl2 = st.columns(2)
    csv = df_final.to_csv(index=False).encode('utf-8-sig')
    with c_dl1:
        st.download_button("CSVでダウンロード", csv, f"ranking_{datetime.now():%Y%m%d}.csv", "text/csv", width='stretch')
    with c_dl2:
        pdf_result = create_pdf(df_final)
        if pdf_result in ["NO_FOLDER", "NO_FILE", "ERROR"]:
            st.error("PDF作成エラー: fontsフォルダを確認してください")
        else:
            st.download_button("PDFレポートをダウンロード", pdf_result, f"report_{datetime.now():%Y%m%d}.pdf", "application/pdf", width='stretch')

    st.divider()
    st.subheader("報告用テキスト（コピーボタン付き）")
    st.code(generate_report_text(df_final.copy(), target_url), language='text')

# --- 完了後のクールダウン処理 ---
if st.session_state.should_cooldown:
    start_btn_area.empty()
    
    info_area = st.sidebar.empty()
    final_rest = 180 # 3分間
    
    for r in range(final_rest, 0, -1):
        info_area.error(f"🛑 [安全停止] 次のチェックまで IP休憩中... 残り {r} 秒")
        time.sleep(1)
    
    info_area.success("🆗 クールダウン完了！再開可能です。")
    time.sleep(2)
    info_area.empty()
    
    st.session_state.should_cooldown = False
    st.rerun()