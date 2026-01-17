import sys
import os
import time
import requests

# パスを通す（search_engine.pyを読み込むため）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from worker.search_engine import RankScraper

# ==========================================
# ★設定エリア
# Manager（司令塔）のTailscale IPアドレスを入力
MANAGER_IP = "100.125.182.127"  # ← ここを書き換える！！
MANAGER_PORT = 8000
BASE_URL = f"http://{MANAGER_IP}:{MANAGER_PORT}"
# ==========================================

def run_worker_loop():
    print(f"🚀 Worker started. Connecting to {BASE_URL}...")
    
    scraper = RankScraper(show_browser=True) # ブラウザ表示あり
    
    while True:
        try:
            # 1. 仕事をもらいに行く
            response = requests.get(f"{BASE_URL}/get_task", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                task = data.get("task")
                
                if task:
                    print(f"\n🔍 検索開始: {task['keyword']}")
                    
                    # 2. 検索実行
                    result_data = scraper.check_rank(
                        task['keyword'], 
                        task['target_url'], 
                        task['min_sleep'], 
                        task['max_sleep']
                    )
                    
                    # 3. 結果を報告
                    payload = {
                        "keyword": result_data["keyword"],
                        "yahoo_rank": result_data["yahoo_rank"],
                        "google_rank": result_data["google_rank"],
                        "target_url": result_data["target_url"],
                        "check_date": result_data["check_date"]
                    }
                    
                    res = requests.post(f"{BASE_URL}/submit_result", json=payload)
                    if res.status_code == 200:
                        print("✅ 報告完了！次の仕事を待ちます...")
                    else:
                        print("❌ 報告失敗")
                        
                else:
                    # 仕事がない時
                    print(".", end="", flush=True)
                    time.sleep(5) # 5秒待機して再確認
            else:
                print(f"Error: Server returned {response.status_code}")
                time.sleep(10)
                
        except Exception as e:
            print(f"\n⚠️ 通信エラー: {e}")
            print("Managerが起動していないか、IPが間違っている可能性があります。")
            time.sleep(10)

if __name__ == "__main__":
    run_worker_loop()