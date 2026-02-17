# gmail-sender

一个**最小可用**的 Python 项目，包含 3 个可复用组件：

1. `gmail_sender.py`：发送 Gmail 邮件（支持标题、抄送、正文、附件）
2. `deepseek_component.py`：调用 DeepSeek API，每个问答写入独立文本文件，并把索引写入 CSV 表格
3. `test_deepseek_email.py`：交互式测试脚本（输入问题后调用 DeepSeek，并将结果邮件发送给指定邮箱）

---

## 目录结构

- `gmail_sender.py`：Gmail 发件函数 `send_gmail(...)`
- `deepseek_component.py`：DeepSeek 调用函数 `ask_deepseek_and_log(...)`
- `test_deepseek_email.py`：串联调用 DeepSeek + Gmail 的示例入口

---

## 环境要求

- Python 3.10+
- 依赖：`requests`

安装依赖：

```bash
pip install requests
```

---

## Gmail 使用说明

Gmail SMTP 常规参数：

- 服务器：`smtp.gmail.com`
- 端口：`465`（SSL）

> 建议使用 Gmail 的 **App Password（应用专用密码）**，不要直接使用账号登录密码。

---

## 1) 发送 Gmail：`send_gmail(...)`

```python
from gmail_sender import send_gmail

send_gmail(
    sender="you@gmail.com",
    app_password="xxxx xxxx xxxx xxxx",
    to=["to@example.com"],
    subject="测试标题",
    body="测试正文",
    cc=["cc@example.com"],
    attachments=["./demo.pdf"],
)
```

### 参数说明

- `sender`: 发件人邮箱
- `app_password`: Gmail 应用专用密码
- `to`: 收件人列表（必填）
- `subject`: 邮件标题
- `body`: 邮件正文
- `cc`: 抄送列表（可选）
- `attachments`: 附件路径列表（可选）

---

## 2) 调用 DeepSeek 并记录日志：`ask_deepseek_and_log(...)`

```python
from deepseek_component import ask_deepseek_and_log

result = ask_deepseek_and_log(
    api_key="your_deepseek_api_key",
    title="日报润色",
    question="请帮我润色这段内容",
)

print(result["answer"])
```

### 默认日志输出

- 文本日志目录：`deepseek_qa_logs/`
  - 每个问答生成一个独立文本文件（如 `qa_2026-01-01T12-00-00.txt`）
  - 文件内容格式：`问题：request, 回答：response`
- 表格日志：`deepseek_log_table.csv`
  - 列：`title,question,time`

### 返回值

```python
{
    "title": "...",
    "question": "...",
    "answer": "...",
    "time": "2026-01-01T12:00:00"
}
```

---

## 使用 .env 管理 DeepSeek 与 Gmail 参数（推荐）

在项目根目录新建 `.env`（可参考 `.env.example`）：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions
DEEPSEEK_TIMEOUT=60
DEEPSEEK_LOG_TXT_DIR=deepseek_qa_logs
DEEPSEEK_LOG_CSV_PATH=deepseek_log_table.csv

GMAIL_SENDER=you@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
GMAIL_TO=target@example.com
GMAIL_CC=cc1@example.com,cc2@example.com
```

说明：
- `test_deepseek_email.py` 会自动读取 `.env`，无需额外安装 `python-dotenv`。
- `GMAIL_TO` 可不填；不填时脚本会在运行时让你手动输入收件邮箱。
- `GMAIL_CC` 支持多个邮箱，使用英文逗号分隔。

---

## 3) 一键测试流程：`test_deepseek_email.py`

该脚本会：

1. 从终端读取“收件邮箱”和“问题”
2. 调用 DeepSeek
3. 自动记录问答文本与 CSV
4. 将“回答标题 + 回答内容”发送到你输入的邮箱

### 先设置环境变量

```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export GMAIL_SENDER="you@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

### 运行

```bash
python test_deepseek_email.py
```

---

## 常见问题

### 1. 报 `ValueError: 参数 to 不能为空`
`send_gmail(...)` 的 `to` 必须至少包含一个邮箱地址。

### 2. DeepSeek 请求失败
请检查：
- API Key 是否正确
- 网络是否可访问 `https://api.deepseek.com`
- 是否触发了 API 限流

### 3. Gmail 登录失败
请检查：
- 是否开启了 2FA 并生成 App Password
- 发件邮箱与 App Password 是否匹配

---

## 安全建议

- 不要把 API Key、邮箱密码硬编码到代码里。
- 建议统一用环境变量或密钥管理服务。
- 若日志里含敏感内容，请限制日志文件访问权限。
