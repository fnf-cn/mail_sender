# Mail Sender API - Docker 部署指南

## 目录

1. [前置要求](#前置要求)
2. [快速部署](#快速部署)
3. [详细步骤](#详细步骤)
4. [配置说明](#配置说明)
5. [容器管理](#容器管理)
6. [内网访问](#内网访问)
7. [故障排查](#故障排查)
8. [性能调优](#性能调优)

---

## 前置要求

- Docker 已安装（版本 20.0+）
- Docker Compose 已安装（版本 1.29+）
- PostgreSQL 数据库已准备（本地或远程）
- SMTP 邮件服务器可用

### 检查安装

```bash
docker --version
docker-compose --version
```

---

## 快速部署

### 3 步快速启动

**1. 配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填写 SMTP 和数据库信息
```

**2. 启动服务**

```bash
docker-compose up -d
```

**3. 验证服务**

```bash
curl http://172.16.72.73:10001/health
# 返回 {"status":"healthy"} 表示成功
```

---

## 详细步骤

### 步骤 1：准备项目文件

确保项目目录结构如下：

```
mail_sender/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .env                 # 本地配置（git 忽略）
├── requirements.txt
└── app/
    ├── main.py
    ├── config.py
    ├── models.py
    ├── database.py
    ├── email_service.py
    ├── tasks.py
    ├── schemas.py
    └── routes/
        └── emails.py
```

### 步骤 2：配置环境变量

**复制环境变量模板**

```bash
cp .env.example .env
```

**编辑 .env 文件**

```bash
vim .env
```

**必需配置项**

```ini
# 数据库配置
DATABASE_URL=postgresql://fnfadmin:fnfadmin123@172.16.72.73:5433/mail_sender

# SMTP 配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Mail Sender

# API 配置
API_HOST=0.0.0.0
API_PORT=10001
DEBUG=False
```

### 步骤 3：SMTP 服务配置示例

根据你使用的邮件服务，配置相应的参数：

#### Gmail

```ini
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

> ⚠️ **注意**：Gmail 需要生成应用专用密码，不是普通密码。
> 访问 https://myaccount.google.com/apppasswords 生成。

#### 腾讯企业邮箱

```ini
SMTP_HOST=smtp.exmail.qq.com
SMTP_PORT=465
SMTP_USER=your-email@qq.com
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=your-email@qq.com
```

#### Outlook

```ini
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=your-email@outlook.com
```

#### 阿里企业邮箱

```ini
SMTP_HOST=smtp.qiye.aliyun.com
SMTP_PORT=465
SMTP_USER=your-email@aliyun.com
SMTP_PASSWORD=your-client-password
SMTP_FROM_EMAIL=your-email@aliyun.com
```

### 步骤 4：启动容器

**后台启动（推荐）**

```bash
docker-compose up -d
```

**前台启动（查看日志）**

```bash
docker-compose up
```

**验证启动成功**

```bash
docker-compose ps
```

输出应显示所有容器均为 `Up` 状态：

```
NAME                   STATUS
mail-sender-api        Up 2 minutes
mail-sender-redis      Up 2 minutes
mail-sender-celery     Up 2 minutes
```

### 步骤 5：验证服务

```bash
# 健康检查
curl http://172.16.72.73:10001/health

# 查看 API 文档
# 在浏览器访问：http://172.16.72.73:10001/docs

# 查看日志
docker-compose logs fastapi
```

---

## 配置说明

### docker-compose.yml 说明

```yaml
version: '3.8'

services:
  # Redis - 消息代理
  redis:
    image: redis:7-alpine
    container_name: mail-sender-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI 应用
  fastapi:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mail-sender-api
    ports:
      - "10001:10001"
    environment:
      - DATABASE_URL=postgresql://user:pass@host:port/db
      - REDIS_URL=redis://redis:6379/0
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - SMTP_FROM_EMAIL=${SMTP_FROM_EMAIL}
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:10001/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Celery Worker - 异步任务
  celery:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mail-sender-celery
    environment:
      - DATABASE_URL=postgresql://user:pass@host:port/db
      - REDIS_URL=redis://redis:6379/0
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - SMTP_FROM_EMAIL=${SMTP_FROM_EMAIL}
    depends_on:
      redis:
        condition: service_healthy
    command: celery -A app.tasks worker --loglevel=info

volumes:
  redis_data:
```

### 环境变量详解

| 变量 | 说明 | 示例 |
|------|------|------|
| `DATABASE_URL` | PostgreSQL 连接字符串 | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis 连接字符串 | `redis://redis:6379/0` |
| `SMTP_HOST` | SMTP 服务器地址 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP 端口 | `587` 或 `465` |
| `SMTP_USER` | SMTP 用户名 | `your-email@gmail.com` |
| `SMTP_PASSWORD` | SMTP 密码 | `your-app-password` |
| `SMTP_FROM_EMAIL` | 发送者邮箱 | `your-email@gmail.com` |
| `SMTP_FROM_NAME` | 发送者名称 | `Mail Sender` |
| `API_HOST` | API 监听地址 | `0.0.0.0` |
| `API_PORT` | API 监听端口 | `10001` |
| `DEBUG` | 调试模式 | `False` |

---

## 容器管理

### 查看容器状态

```bash
# 查看所有容器
docker-compose ps

# 查看详细信息
docker-compose ps -a
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f fastapi
docker-compose logs -f celery
docker-compose logs -f redis

# 查看最后 100 行日志
docker-compose logs --tail 100
```

### 重启容器

```bash
# 重启所有容器
docker-compose restart

# 重启特定容器
docker-compose restart fastapi
docker-compose restart celery
docker-compose restart redis

# 停止并重新启动
docker-compose down
docker-compose up -d
```

### 停止服务

```bash
# 停止容器（保留数据）
docker-compose stop

# 删除容器（清除容器，保留数据卷）
docker-compose down

# 删除容器和所有数据（谨慎！）
docker-compose down -v
```

### 进入容器调试

```bash
# 进入 FastAPI 容器
docker-compose exec fastapi /bin/sh

# 进入 Celery 容器
docker-compose exec celery /bin/sh

# 进入 Redis 容器
docker-compose exec redis /bin/sh

# 在容器内执行命令
docker-compose exec fastapi python -c "from app.database import init_db; init_db()"
```

---

## 内网访问

### 确保内网其他电脑可访问

#### 1. 验证 Docker 配置

检查 `docker-compose.yml` 中的端口配置：

```yaml
fastapi:
  ports:
    - "10001:10001"  # ✅ 允许所有网络访问
```

#### 2. 获取服务器 IP

```bash
# 查询内网 IP
hostname -I

# 或详细查看
ip addr show | grep "inet "
```

示例输出：
```
192.168.1.100
10.0.0.50
172.16.72.73
```

#### 3. 内网其他电脑测试连接

```bash
# ping 测试网络连通性
ping 172.16.72.73

# 测试服务可用性
curl http://172.16.72.73:10001/health

# 在浏览器访问 API 文档
# http://172.16.72.73:10001/docs
```

#### 4. 防火墙配置

如果无法连接，可能是防火墙阻止，需要开放 10001 端口：

**Ubuntu/Debian：**

```bash
sudo ufw allow 10001
sudo ufw enable

# 查看防火墙状态
sudo ufw status
```

**CentOS/RHEL：**

```bash
sudo firewall-cmd --add-port=10001/tcp --permanent
sudo firewall-cmd --reload

# 查看防火墙状态
sudo firewall-cmd --list-ports
```

**Windows：**

在 Windows Defender 防火墙中允许端口 10001。

---

## 故障排查

### 问题 1：容器无法启动

**检查日志**

```bash
docker-compose logs fastapi
docker-compose logs celery
docker-compose logs redis
```

**常见原因：**
- 依赖的服务未就绪
- 环境变量配置错误
- 磁盘空间不足

**解决方案：**

```bash
# 重新构建镜像
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 问题 2：数据库连接失败

**检查 DATABASE_URL**

```bash
cat .env | grep DATABASE_URL
```

**验证数据库连接**

```bash
docker-compose exec fastapi python -c "
from app.database import get_db
db = next(get_db())
print('Database connection successful!')
"
```

**常见原因：**
- 数据库地址或凭证错误
- 数据库服务未启动
- 防火墙阻止

### 问题 3：SMTP 连接失败

**检查 SMTP 配置**

```bash
cat .env | grep SMTP
```

**查看错误日志**

```bash
docker-compose logs celery | grep -i smtp
```

**常见原因：**
- SMTP 用户名或密码错误
- SMTP 端口错误（Gmail 用 587，部分服务用 465）
- 防火墙阻止 SMTP 端口

### 问题 4：邮件一直是 PENDING 状态

**检查 Celery Worker 是否运行**

```bash
docker-compose ps celery

# 应输出：mail-sender-celery   Up (healthy)
```

**检查 Redis 连接**

```bash
docker-compose exec celery python -c "
from celery import current_app
print('Redis connection:', current_app.connection())
"
```

**查看任务队列**

```bash
docker-compose exec redis redis-cli

# 在 redis-cli 中执行：
LLEN celery
LLEN celery-default
```

### 问题 5：磁盘空间满

**清理 Docker**

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的数据卷
docker volume prune
```

### 问题 6：无法从内网其他电脑访问

**检查清单**

```bash
# 1. 服务是否运行
docker-compose ps

# 2. 端口是否监听
netstat -tuln | grep 10001

# 3. 防火墙是否开放
sudo ufw status

# 4. 网络连通性
ping 172.16.72.73

# 5. HTTP 连接
curl -v http://172.16.72.73:10001/health
```

---

## 性能调优

### 1. 调整 Celery 并发数

编辑 `docker-compose.yml`：

```yaml
celery:
  command: celery -A app.tasks worker --loglevel=info --concurrency=4
```

> 并发数建议为 CPU 核心数。

### 2. 调整 Redis 持久化

编辑 `docker-compose.yml`：

```yaml
redis:
  command: redis-server --appendonly yes --appendfsync everysec
```

> `appendfsync` 选项：
> - `always` - 每次写操作都持久化（最安全，最慢）
> - `everysec` - 每秒持久化（推荐）
> - `no` - 不持久化（最快，但可能丢失数据）

### 3. 调整 FastAPI 工作进程

编辑 `docker-compose.yml`：

```yaml
fastapi:
  command: python -m uvicorn app.main:app --host 0.0.0.0 --port 10001 --workers 4
```

> 工作进程数建议为 (CPU 核心数 × 2) + 1。

### 4. 监控资源使用

```bash
# 查看容器资源使用情况
docker stats

# 输出示例：
# CONTAINER CPU %  MEM USAGE / LIMIT  NET I/O
# mail-sender-api  0.5%   256MiB / 2GiB  ...
```

---

## 生产环境检查清单

- [ ] 关闭 DEBUG 模式（`DEBUG=False`）
- [ ] 更改默认密码
- [ ] 开放防火墙 10001 端口
- [ ] 验证 SMTP 和数据库连接
- [ ] 设置日志转储和轮转
- [ ] 配置备份策略
- [ ] 部署监控告警
- [ ] 配置反向代理（Nginx/Apache）
- [ ] 使用 SSL/TLS 加密通信
- [ ] 设置自动重启策略

### 配置自动重启

编辑 `docker-compose.yml`：

```yaml
services:
  fastapi:
    restart_policy:
      condition: on-failure
      delay: 5s
      max_attempts: 3
```

---

## 备份和恢复

### 备份数据库

```bash
# 备份 PostgreSQL 数据
docker-compose exec fastapi pg_dump -U fnfadmin -d mail_sender > backup_$(date +%Y%m%d).sql

# 备份大小
du -h backup_*.sql
```

### 恢复数据库

```bash
# 恢复数据
docker-compose exec fastapi psql -U fnfadmin -d mail_sender < backup_20240115.sql
```

### 备份自动化脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/mail_sender"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec fastapi pg_dump -U fnfadmin -d mail_sender > $BACKUP_DIR/db_$DATE.sql

# 保留最近 7 天的备份
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql"
```

---

## 下一步

- 查看 [Instruction.md](./Instruction.md) 了解如何使用 API
- 查看 [README.md](./README.md) 了解项目信息
