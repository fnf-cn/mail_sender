# Mail Sender API

邮件发送 API - 一个基于 FastAPI 的异步邮件发送系统，支持标题、收件人、正文和附件。

## 功能特性

✅ **REST API 接口** - 通过 HTTP 端点发送邮件
✅ **异步处理** - 使用 Celery 后台任务异步发送邮件
✅ **数据持久化** - PostgreSQL 数据库保存邮件发送历史
✅ **附件支持** - 支持多个文件附件
✅ **状态追踪** - 实时查询邮件发送状态
✅ **搜索和筛选** - 支持按收件人、主题搜索邮件
✅ **自动重试** - 发送失败自动重试
✅ **错误处理** - 完整的错误日志记录

## 技术栈

- **FastAPI** - Web 框架
- **SQLAlchemy** - ORM
- **PostgreSQL** - 数据库
- **Celery** - 异步任务队列
- **Redis** - 消息代理和缓存
- **aiosmtplib** - SMTP 客户端

## 安装

### 1. 克隆项目并安装依赖

```bash
cd mail_sender
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填写你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置：
- PostgreSQL 数据库连接
- SMTP 邮件服务器设置
- Redis 连接
- API 端口

示例：
```
DATABASE_URL=postgresql://fnfadmin:fnfadmin123@172.16.72.73:5433/mail_sender
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
REDIS_URL=redis://localhost:6379/0
API_PORT=10001
```

### 3. 初始化数据库

```bash
python -c "from app.database import init_db; init_db()"
```

## 快速开始

### 启动 Celery Worker

```bash
celery -A app.tasks worker --loglevel=info
```

### 启动 FastAPI 服务

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 10001 --reload
```

服务启动后，访问 http://localhost:10001/docs 查看 API 文档。

## API 端点

### 1. 发送邮件

```http
POST /api/emails/send
```

请求体：
```json
{
  "to_email": "recipient@example.com",
  "subject": "Test Email",
  "body": "This is a test email body",
  "attachments": ["/path/to/file1.pdf", "/path/to/file2.xlsx"]
}
```

响应：
```json
{
  "success": true,
  "message": "Email queued for sending",
  "email_id": 1
}
```

### 2. 查询邮件发送状态

```http
GET /api/emails/status/{email_id}
```

响应：
```json
{
  "id": 1,
  "to_email": "recipient@example.com",
  "subject": "Test Email",
  "status": "success",
  "created_at": "2024-01-15T10:30:00",
  "sent_at": "2024-01-15T10:30:05",
  "error_message": null
}
```

### 3. 查询邮件列表

```http
GET /api/emails/?skip=0&limit=10&status=success
```

参数：
- `skip` (int, 可选) - 跳过的记录数，默认 0
- `limit` (int, 可选) - 每页记录数，默认 10，最多 100
- `status` (string, 可选) - 邮件状态（pending/sending/success/failed）

### 4. 搜索邮件

```http
GET /api/emails/search?to_email=example.com&subject=test
```

参数：
- `to_email` (string, 可选) - 收件人邮箱（模糊匹配）
- `subject` (string, 可选) - 邮件主题（模糊匹配）
- `skip` (int, 可选) - 跳过的记录数
- `limit` (int, 可选) - 每页记录数

### 5. 健康检查

```http
GET /health
```

## 邮件状态

- **pending** - 待发送
- **sending** - 发送中
- **success** - 发送成功
- **failed** - 发送失败

## 项目结构

```
mail_sender/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── models.py            # SQLAlchemy 数据库模型
│   ├── schemas.py           # Pydantic 请求/响应 schema
│   ├── database.py          # 数据库连接
│   ├── email_service.py     # 邮件发送服务
│   ├── tasks.py             # Celery 异步任务
│   └── routes/
│       ├── __init__.py
│       └── emails.py        # 邮件相关 API 路由
├── .env.example             # 环境变量示例
├── requirements.txt         # Python 依赖
└── README.md               # 项目文档
```

## 配置说明

### SMTP 配置

支持任何支持 SMTP 的邮件服务，常见配置：

**Gmail:**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # 需要生成应用专用密码
```

**企业邮箱（腾讯）:**
```
SMTP_HOST=smtp.exmail.qq.com
SMTP_PORT=465
```

**Outlook:**
```
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
```

### Redis 配置

Celery 需要 Redis 作为消息代理。确保 Redis 服务已启动：

```bash
redis-server
```

## 错误处理

- **邮件发送失败自动重试** - 最多重试 3 次，每次间隔 60 秒
- **附件验证** - 如果附件文件不存在，会记录警告但继续发送邮件
- **SMTP 连接错误** - 自动记录错误并更新邮件状态为失败

## 日志

应用使用 Python 标准 logging 模块，日志级别为 INFO。

在 FastAPI 中查看日志：
```
2024-01-15 10:30:00,123 - app.tasks - INFO - Email sent successfully to recipient@example.com
```

## 常见问题

**Q: 如何查看发送失败的原因？**
A: 查询邮件状态时，`error_message` 字段会显示具体的错误信息。

**Q: 附件文件大小有限制吗？**
A: 取决于 SMTP 服务器配置，通常支持 25MB 以内的文件。

**Q: 如何修改重试策略？**
A: 在 `tasks.py` 中修改 `send_email_task` 的 `max_retries` 和 `countdown` 参数。

## 开发建议

1. 在生产环境中，确保数据库、Redis 和 SMTP 服务都已配置
2. 使用环境变量管理敏感信息（SMTP 密码等）
3. 定期清理已发送的邮件记录以节省存储空间
4. 监控 Celery 任务队列，确保没有积压

## License

MIT
