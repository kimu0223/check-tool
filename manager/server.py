from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# 簡易的なメモリ内データベース（今日はここを使います）
# 将来的にはSQLiteと連動させますが、まずは「通信」の成功を目指します
app = FastAPI()

# 仕事の待ち行列
task_queue = []
# 完了した仕事の結果
results_store = []

class Task(BaseModel):
    keyword: str
    target_url: str
    min_sleep: int
    max_sleep: int

class Result(BaseModel):
    keyword: str
    yahoo_rank: str
    google_rank: str
    target_url: str
    check_date: str

@app.get("/")
def read_root():
    return {"message": "GRC-Manager API is Running!"}

# --- 1. 仕事を追加する（Manager用） ---
@app.post("/add_tasks")
def add_tasks(tasks: List[Task]):
    global task_queue
    task_queue.extend(tasks)
    return {"message": f"{len(tasks)} tasks added", "current_queue": len(task_queue)}

# --- 2. 仕事を取りに行く（Worker用） ---
@app.get("/get_task")
def get_task():
    global task_queue
    if not task_queue:
        return {"task": None}  # 仕事なし
    
    # 先頭の仕事を取り出して渡す
    task = task_queue.pop(0)
    return {"task": task}

# --- 3. 結果を報告する（Worker用） ---
@app.post("/submit_result")
def submit_result(result: Result):
    global results_store
    results_store.append(result)
    print(f"✅ 受信: {result.keyword} (Y:{result.yahoo_rank} / G:{result.google_rank})")
    return {"status": "ok"}

# --- 4. 結果一覧を見る（確認用） ---
@app.get("/results")
def get_results():
    return results_store