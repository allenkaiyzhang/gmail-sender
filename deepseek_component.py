"""DeepSeek 调用与日志组件（可被其他 Python 文件直接引用）。

功能：
- 调用 DeepSeek Chat API
- 每次问答写入一个独立文本文件，格式：问题：<request>, 回答：<response>
- 将标题、问题、时间保存到表格（CSV），文件不存在时自动创建

示例：
    from deepseek_component import ask_deepseek_and_log

    result = ask_deepseek_and_log(
        api_key="your_deepseek_api_key",
        title="日报润色",
        question="请帮我把这段中文润色成更专业的表达",
    )
    print(result)
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


DEFAULT_API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"


def _ensure_parent_dir(file_path: str) -> None:
    path = Path(file_path)
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def _write_single_qa_text_file(log_txt_dir: str, question: str, response: str, created_at: str) -> str:
    txt_dir = Path(log_txt_dir)
    txt_dir.mkdir(parents=True, exist_ok=True)

    safe_time = created_at.replace(":", "-")
    txt_path = txt_dir / f"qa_{safe_time}.txt"
    txt_path.write_text(f"问题：{question}, 回答：{response}\n", encoding="utf-8")
    return str(txt_path)


def _ensure_csv_table(log_csv_path: str) -> None:
    _ensure_parent_dir(log_csv_path)
    path = Path(log_csv_path)
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["title", "question", "time"])


def _append_table_row(log_csv_path: str, title: str, question: str, created_at: str) -> None:
    _ensure_csv_table(log_csv_path)
    with open(log_csv_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([title, question, created_at])


def ask_deepseek_and_log(
    api_key: str,
    title: str,
    question: str,
    model: str = DEFAULT_MODEL,
    api_url: str = DEFAULT_API_URL,
    timeout: int = 60,
    log_txt_dir: str = "deepseek_qa_logs",
    log_csv_path: str = "deepseek_log_table.csv",
) -> dict[str, Any]:
    """调用 DeepSeek API 并记录日志。"""
    if not api_key:
        raise ValueError("api_key 不能为空")
    if not title:
        raise ValueError("title 不能为空")
    if not question:
        raise ValueError("question 不能为空")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": question}],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    try:
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"DeepSeek 返回格式异常: {data}") from exc

    created_at = datetime.now().isoformat(timespec="seconds")

    qa_text_path = _write_single_qa_text_file(
        log_txt_dir=log_txt_dir,
        question=question,
        response=answer,
        created_at=created_at,
    )
    _append_table_row(log_csv_path=log_csv_path, title=title, question=question, created_at=created_at)

    return {
        "title": title,
        "question": question,
        "answer": answer,
        "time": created_at,
        "qa_text_path": qa_text_path,
    }
