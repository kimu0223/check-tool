import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import unquote

class RankScraper:
    def __init__(self, show_browser=True):
        self.show_browser = show_browser
        
        # User-Agentリスト（毎回違うブラウザのふりをするための変装セット）
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]

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
        
        # ★リストからランダムに1つ選んでセット（変装）
        ua = random.choice(self.user_agents)
        options.add_argument(f"user-agent={ua}")

        # スイッチがOFFならブラウザ画面を出さない（ヘッドレス）
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
        try:
            found_decoded = unquote(found_url)
            target_clean = target_url.replace("https://", "").replace("http://", "").rstrip("/")
            if target_clean in found_decoded:
                if found_decoded.startswith("http") and target_clean not in found_decoded.split("/")[2]:
                    return False
                return True
        except: return False
        return False

    def check_rank(self, keyword, target_url, min_sleep=3, max_sleep=6):
        driver = self._get_driver()
        
        result = {
            "keyword": keyword, 
            "yahoo_rank": "エラー",
            "target_url": target_url,
            "status": "Failed", 
            "check_date": time.strftime('%Y-%m-%d %H:%M:%S')
        }

        if not driver: return result
        
        # ★設定: Yahooのみ50位まで（5ページ）
        MAX_PAGES = 5

        try:
            # --- Yahoo検索のみ実行 ---
            y_rank = "圏外"
            try:
                driver.get(f"https://search.yahoo.co.jp/search?p={keyword}")
                self._random_sleep(min_sleep, max_sleep)
                y_found = False
                y_current_count = 0
                
                for page in range(MAX_PAGES):
                    elements = driver.find_elements(By.CSS_SELECTOR, ".sw-Card")
                    for el in elements:
                        try:
                            title = el.find_elements(By.CSS_SELECTOR, ".sw-Card__title > a")
                            if not title: continue
                            url = title[0].get_attribute("href")
                            y_current_count += 1
                            if self._is_match(url, target_url):
                                y_rank = str(y_current_count)
                                y_found = True
                                break
                        except: continue
                    
                    if y_found: break
                    
                    if page < (MAX_PAGES - 1):
                        try:
                            next_btn = driver.find_element(By.CSS_SELECTOR, ".Pagenation__next > a")
                            driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                            time.sleep(2)
                            next_btn.click()
                            self._random_sleep(min_sleep, max_sleep)
                        except: break
            except: pass

            result["yahoo_rank"] = y_rank
            result["status"] = "Success"

        finally:
            try: driver.quit()
            except: pass

        return result