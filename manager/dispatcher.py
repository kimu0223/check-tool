# manager/dispatcher.py
import sys
import os

# workerフォルダをインポートできるようにする
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from worker.search_engine import RankScraper

class TaskManager:
    """
    中央管理システム（司令塔）
    今はローカルで実行するが、将来的にはここで「空いているWorker（スマホ）」を選んで
    Tailscale経由で命令を飛ばすロジックに拡張する。
    """
    def __init__(self):
        pass

    def execute_task(self, keyword, target_url, min_s, max_s, show_browser=False):
        """
        タスクを実行する
        Currently: ローカルのRankScraperを直接呼ぶ
        Future: APIリクエストなどをここに記述
        """
        # ★将来の拡張ポイント: ここでWorkerを選択するロジックが入る
        # worker = self.select_best_worker()
        # return worker.run(...)

        # 現状はローカル実行
        scraper = RankScraper(show_browser=show_browser)
        return scraper.check_rank(keyword, target_url, min_s, max_s)