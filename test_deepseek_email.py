"""测试脚本：输入问题 -> 调用 DeepSeek -> 把回答标题和内容邮件发送到指定邮箱。

支持从 `.env` 文件读取配置（无第三方依赖）。

运行：
    python test_deepseek_email.py
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from deepseek_component import ask_deepseek_and_log
from gmail_sender import send_gmail


def load_env_file(env_path: str = ".env") -> None:
    """从 .env 读取 KEY=VALUE 到环境变量（已存在变量不覆盖）。"""
    path = Path(env_path)
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def _split_csv_env(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def run_once() -> None:
    load_env_file()

    api_key = os.environ["DEEPSEEK_API_KEY"]
    sender = os.environ["GMAIL_SENDER"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    recipient = os.getenv("GMAIL_TO") or input("请输入收件邮箱: ").strip()
    if not recipient:
        raise ValueError("收件邮箱不能为空")

    question = input("请输入提问内容: ").strip()
    if not question:
        raise ValueError("提问内容不能为空")

    title = f"DeepSeek回复_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    result = ask_deepseek_and_log(
        api_key=api_key,
        title=title,
        question=question,
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        api_url=os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions"),
        timeout=int(os.getenv("DEEPSEEK_TIMEOUT", "60")),
        log_txt_dir=os.getenv("DEEPSEEK_LOG_TXT_DIR", "deepseek_qa_logs"),
        log_csv_path=os.getenv("DEEPSEEK_LOG_CSV_PATH", "deepseek_log_table.csv"),
    )

    send_gmail(
        sender=sender,
        app_password=app_password,
        to=[recipient],
        subject=result["title"],
        body=result["answer"],
        cc=_split_csv_env(os.getenv("GMAIL_CC")),
        attachments=None,
    )

    print("已发送邮件")
    print(f"标题: {result['title']}")
    print(f"内容: {result['answer']}")


if __name__ == "__main__":
    run_once()
