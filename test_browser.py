import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

print("--- テスト開始 ---")
print("1. ドライバーをダウンロード・確認しています...")

try:
    # ここで止まることが多いです
    service = ChromeService(ChromeDriverManager().install())
    print("★ ドライバー準備OK！")

    print("2. ブラウザを起動します...")
    driver = webdriver.Chrome(service=service)
    print("★ ブラウザ起動OK！")

    print("3. Googleを開きます...")
    driver.get("https://www.google.com")
    print("★ GoogleアクセスOK！")
    
    time.sleep(5)
    print("4. 5秒後に閉じます")
    driver.quit()
    print("--- テスト成功 ---")

except Exception as e:
    print("\n!!!!!!!! エラー発生 !!!!!!!!")
    print(e)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    input("エンターキーを押して終了してください...")