import time
import random
import os
import sys

# 親ディレクトリをパスに追加して shared を読み込めるようにする
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import unquote
from shared.user_agents import get_random_ua

class RankScraper:
    def __init__(self, show_browser=True):
        self.show_browser = show_browser

    def _get_driver(self):
        options = Options()
        
        # --- ステルス設定 ---
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,900")
        options.add_argument("--log-level=3")
        
        # 偽装UAの取得
        ua = get_random_ua()
        options.add_argument(f"user-agent={ua}")

        if not self.show_browser:
            options.add_argument("--headless") 

        try:
            return webdriver.Chrome(options=options)
        except Exception as e:
            print(f"★ブラウザ起動エラー: {e}")
            return None

    def _random_sleep(self, min_s, max_s): 
        time.sleep(random.uniform(min_s, max_s))

    def _is_match(self, found_url, target_url):
        """URLが一致するか判定する"""
        try:
            found_decoded = unquote(found_url)
            target_clean = target_url.replace("https://", "").replace("http://", "").rstrip("/")
            if target_clean in found_decoded:
                return True
        except: return False
        return False

    def check_rank(self, keyword, target_url, min_sleep=3, max_sleep=6):
        driver = self._get_driver()
        
        # 結果格納用辞書（初期値）
        result = {
            "keyword": keyword, 
            "yahoo_rank": "圏外",
            "yahoo_hits": "-",  # DB用のダミー
            "google_rank": "圏外", # ★追加
            "google_hits": "-",  # DB用のダミー
            "target_url": target_url,
            "status": "Failed", 
            "check_date": time.strftime('%Y-%m-%d %H:%M:%S')
        }

        if not driver: return result
        
        MAX_PAGES = 5 # 5ページ（50位）までチェック

        try:
            # ==========================================
            # 1. Yahoo! 検索
            # ==========================================
            try:
                driver.get(f"https://search.yahoo.co.jp/search?p={keyword}")
                self._random_sleep(min_sleep, max_sleep)
                
                y_found = False
                y_count = 0
                
                for page in range(MAX_PAGES):
                    elements = driver.find_elements(By.CSS_SELECTOR, ".sw-Card")
                    for el in elements:
                        try:
                            if "スポンサー" in el.text or "広告" in el.text: continue
                            title = el.find_elements(By.CSS_SELECTOR, ".sw-Card__title > a")
                            if not title: continue
                            
                            url = title[0].get_attribute("href")
                            y_count += 1
                            if y_count > 50: break

                            if self._is_match(url, target_url):
                                result["yahoo_rank"] = str(y_count)
                                y_found = True
                                break
                        except: continue
                    
                    if y_found or y_count >= 50: break
                    
                    if page < (MAX_PAGES - 1):
                        try:
                            next_btn = driver.find_element(By.CSS_SELECTOR, ".Pagenation__next > a")
                            driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                            time.sleep(1)
                            next_btn.click()
                            self._random_sleep(min_sleep, max_sleep)
                        except: break
            except Exception as e:
                print(f"Yahoo Error: {e}")

            # ==========================================
            # 2. Google 検索（★ここを追加）
            # ==========================================
            # Yahooの後、少し休憩（人間らしさの演出）
            self._random_sleep(min_sleep, max_sleep)

            try:
                driver.get(f"https://www.google.com/search?q={keyword}&hl=ja")
                self._random_sleep(min_sleep, max_sleep)
                
                g_found = False
                g_count = 0
                
                for page in range(MAX_PAGES):
                    # Googleの検索結果コンテナ（div.g）
                    elements = driver.find_elements(By.CSS_SELECTOR, "div.g")
                    
                    for el in elements:
                        try:
                            links = el.find_elements(By.TAG_NAME, "a")
                            if not links: continue
                            url = links[0].get_attribute("href")
                            
                            # Google自身のリンクやキャッシュ等は除外
                            if not url.startswith("http"): continue
                            if "google.com" in url: continue
                            
                            g_count += 1
                            if g_count > 50: break

                            if self._is_match(url, target_url):
                                result["google_rank"] = str(g_count)
                                g_found = True
                                break
                        except: continue

                    if g_found or g_count >= 50: break

                    # 次へボタン (id="pnnext")
                    if page < (MAX_PAGES - 1):
                        try:
                            next_btn = driver.find_element(By.ID, "pnnext")
                            driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                            time.sleep(1)
                            next_btn.click()
                            self._random_sleep(min_sleep, max_sleep)
                        except: break
            except Exception as e:
                print(f"Google Error: {e}")

            result["status"] = "Success"

        finally:
            try: driver.quit()
            except: pass

        return result