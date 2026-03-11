# Mail Sender API

一个基于 FastAPI 的异步邮件发送系统，支持标题、收件人、正文和附件。

## 📋 功能特性

✅ **REST API 接口** - 通过 HTTP 端点发送邮件
✅ **异步处理** - 使用 Celery 后台任务异步发送邮件
✅ **数据持久化** - PostgreSQL 数据库保存邮件发送历史
✅ **附件支持** - 支持多个文件附件
✅ **状态追踪** - 实时查询邮件发送状态
✅ **搜索和筛选** - 支持按收件人、主题搜索邮件
✅ **自动重试** - 发送失败自动重试（最多3次）
✅ **错误处理** - 完整的错误日志记录

## 🛠️ 技术栈

| 组件 | 说明 |
|------|------|
| **FastAPI** | 现代 Web 框架 |
| **SQLAlchemy** | Python ORM |
| **PostgreSQL** | 关系数据库 |
| **Celery** | 异步任务队列 |
| **Redis** | 消息代理和缓存 |
| **aiosmtplib** | 异步 SMTP 客户端 |

## 📁 项目结构

```
mail_sender/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── models.py            # 数据库模型
│   ├── schemas.py           # 请求/响应 schema
│   ├── database.py          # 数据库连接
│   ├── email_service.py     # 邮件发送服务
│   ├── tasks.py             # Celery 异步任务
│   └── routes/
│       └── emails.py        # 邮件 API 路由
├── Dockerfile               # Docker 构建文件
├── docker-compose.yml       # 容器编排配置
├── requirements.txt         # Python 依赖
├── .env.example             # 环境变量示例
├── README.md                # 项目说明
├── Instruction.md           # 接口使用指南
└── deploy.md                # 部署指南
```

## 🚀 快速开始

### 部署

详见 [deploy.md](./deploy.md)

### 使用 API

详见 [Instruction.md](./Instruction.md)

## 📧 邮件状态

| 状态 | 说明 |
|------|------|
| `pending` | 待发送 |
| `sending` | 发送中 |
| `success` | 发送成功 |
| `failed` | 发送失败 |

## 📖 API 文档

部署后访问：`http://<服务器IP>:10001/docs`

## 💡 开发建议

1. 在生产环境中确保数据库、Redis 和 SMTP 服务都已配置
2. 使用环境变量管理敏感信息（SMTP 密码等）
3. 定期清理已发送的邮件记录以节省存储空间
4. 监控 Celery 任务队列，确保没有积压

## 📝 License

MIT
