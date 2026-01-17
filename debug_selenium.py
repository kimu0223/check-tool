from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# PC A の IP
PC_A_IP = "192.168.50.206"
PROXY_PORT = "3128"

print("🔥 Selenium起動テスト開始...")

options = Options()

# 1. プロキシ設定（http:// なしで IP:Port だけ書くのが一番トラブルが少ない）
options.add_argument(f'--proxy-server={PC_A_IP}:{PROXY_PORT}')

# 2. 自分自身への通信をプロキシから除外する（ここを具体的に書く！）
options.add_argument('--proxy-bypass-list=127.0.0.1,localhost')

# 3. エラー回避のおまじない
options.add_argument('--ignore-certificate-errors')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

try:
    print("   Chromeを起動します...")
    driver = webdriver.Chrome(options=options)
    print("✅ 起動成功！")
    
    print("   Googleにアクセスします...")
    driver.get("https://www.google.com")
    print(f"✅ アクセス成功！ タイトル: {driver.title}")
    
    time.sleep(5)
    driver.quit()
    print("🎉 テスト完了。この設定なら動きます！")
    
except Exception as e:
    print(f"❌ 失敗: {e}")