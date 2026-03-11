# Mail Sender API - 接口使用指南

## 基础信息

- **服务地址**：`http://172.16.72.73:10001`
- **API 基础路径**：`/api/emails`
- **API 文档**：`http://172.16.72.73:10001/docs`（可视化 API 文档）

## API 端点列表

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/emails/send` | 发送邮件 |
| GET | `/api/emails/status/{email_id}` | 查询邮件发送状态 |
| GET | `/api/emails/` | 获取邮件列表 |
| GET | `/api/emails/search` | 搜索邮件 |
| GET | `/health` | 健康检查 |

---

## 1. 发送邮件

### 请求

```http
POST /api/emails/send
Content-Type: application/json
```

### 请求体参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `to_email` | string | ✅ | 收件人邮箱地址 |
| `subject` | string | ✅ | 邮件主题 |
| `body` | string | ✅ | 邮件正文（支持 HTML） |
| `attachments` | array | ❌ | 附件文件路径列表 |

### 示例

**curl：**
```bash
curl -X POST http://172.16.72.73:10001/api/emails/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "recipient@example.com",
    "subject": "测试邮件",
    "body": "这是一个测试邮件",
    "attachments": []
  }'
```

**Python：**
```python
import requests

url = "http://172.16.72.73:10001/api/emails/send"
payload = {
    "to_email": "recipient@example.com",
    "subject": "测试邮件",
    "body": "这是一个测试邮件",
    "attachments": []
}

response = requests.post(url, json=payload)
print(response.json())
```

**JavaScript (Node.js)：**
```javascript
fetch('http://172.16.72.73:10001/api/emails/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    to_email: 'recipient@example.com',
    subject: '测试邮件',
    body: '这是一个测试邮件',
    attachments: []
  })
})
.then(response => response.json())
.then(data => console.log(data))
```

**PHP：**
```php
$url = 'http://172.16.72.73:10001/api/emails/send';
$data = [
    'to_email' => 'recipient@example.com',
    'subject' => '测试邮件',
    'body' => '这是一个测试邮件',
    'attachments' => []
];

$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL => $url,
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => json_encode($data),
    CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
    CURLOPT_RETURNTRANSFER => true
]);

$response = curl_exec($ch);
echo $response;
curl_close($ch);
```

**Java：**
```java
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import com.google.gson.JsonObject;

CloseableHttpClient httpClient = HttpClients.createDefault();
HttpPost httpPost = new HttpPost("http://172.16.72.73:10001/api/emails/send");

JsonObject json = new JsonObject();
json.addProperty("to_email", "recipient@example.com");
json.addProperty("subject", "测试邮件");
json.addProperty("body", "这是一个测试邮件");
json.add("attachments", new JsonArray());

httpPost.setEntity(new StringEntity(json.toString()));
httpPost.setHeader("Content-Type", "application/json");

httpClient.execute(httpPost);
httpClient.close();
```

### 响应

**成功 (200)：**
```json
{
  "success": true,
  "message": "Email queued for sending",
  "email_id": 1
}
```

**失败 (400)：**
```json
{
  "detail": "Invalid email address"
}
```

---

## 2. 查询邮件发送状态

### 请求

```http
GET /api/emails/status/{email_id}
```

### URL 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `email_id` | integer | 邮件 ID |

### 示例

**curl：**
```bash
curl http://172.16.72.73:10001/api/emails/status/1
```

**Python：**
```python
import requests

response = requests.get("http://172.16.72.73:10001/api/emails/status/1")
print(response.json())
```

### 响应

**成功 (200)：**
```json
{
  "id": 1,
  "to_email": "recipient@example.com",
  "subject": "测试邮件",
  "body": "这是一个测试邮件",
  "status": "success",
  "attachment_paths": null,
  "created_at": "2024-01-15T10:30:00.123456",
  "sent_at": "2024-01-15T10:30:05.456789",
  "error_message": null
}
```

**未找到 (404)：**
```json
{
  "detail": "Email not found"
}
```

---

## 3. 获取邮件列表

### 请求

```http
GET /api/emails/?skip=0&limit=10&status=success
```

### 查询参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `skip` | integer | 0 | 跳过的记录数 |
| `limit` | integer | 10 | 每页记录数（最多100） |
| `status` | string | - | 邮件状态（pending/sending/success/failed） |

### 示例

**curl：**
```bash
# 查询最新的10封邮件
curl "http://172.16.72.73:10001/api/emails/?skip=0&limit=10"

# 查询已发送的邮件
curl "http://172.16.72.73:10001/api/emails/?status=success"

# 查询失败的邮件，分页获取
curl "http://172.16.72.73:10001/api/emails/?status=failed&skip=20&limit=10"
```

**Python：**
```python
import requests

params = {
    'skip': 0,
    'limit': 10,
    'status': 'success'
}
response = requests.get("http://172.16.72.73:10001/api/emails/", params=params)
print(response.json())
```

### 响应

**成功 (200)：**
```json
{
  "total": 100,
  "items": [
    {
      "id": 1,
      "to_email": "recipient@example.com",
      "subject": "测试邮件",
      "body": "这是一个测试邮件",
      "status": "success",
      "created_at": "2024-01-15T10:30:00.123456",
      "sent_at": "2024-01-15T10:30:05.456789",
      "error_message": null
    }
  ]
}
```

---

## 4. 搜索邮件

### 请求

```http
GET /api/emails/search?to_email=example.com&subject=test
```

### 查询参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `to_email` | string | 收件人邮箱（模糊匹配） |
| `subject` | string | 邮件主题（模糊匹配） |
| `skip` | integer | 跳过的记录数（默认0） |
| `limit` | integer | 每页记录数（默认10，最多100） |

### 示例

**curl：**
```bash
# 按收件人搜索
curl "http://172.16.72.73:10001/api/emails/search?to_email=example.com"

# 按主题搜索
curl "http://172.16.72.73:10001/api/emails/search?subject=test"

# 组合搜索
curl "http://172.16.72.73:10001/api/emails/search?to_email=example.com&subject=test&limit=20"
```

**Python：**
```python
import requests

params = {
    'to_email': 'example.com',
    'subject': 'test',
    'limit': 20
}
response = requests.get("http://172.16.72.73:10001/api/emails/search", params=params)
print(response.json())
```

### 响应

**成功 (200)：**
```json
{
  "total": 5,
  "items": [
    {
      "id": 1,
      "to_email": "user@example.com",
      "subject": "test email",
      "body": "...",
      "status": "success",
      "created_at": "2024-01-15T10:30:00.123456",
      "sent_at": "2024-01-15T10:30:05.456789",
      "error_message": null
    }
  ]
}
```

---

## 5. 健康检查

### 请求

```http
GET /health
```

### 示例

**curl：**
```bash
curl http://172.16.72.73:10001/health
```

### 响应

**成功 (200)：**
```json
{
  "status": "healthy"
}
```

---

## 邮件状态说明

| 状态 | 说明 |
|------|------|
| **pending** | 邮件已接收，等待发送 |
| **sending** | 正在发送邮件 |
| **success** | 邮件发送成功 |
| **failed** | 邮件发送失败 |

---

## 错误处理

### 常见错误

| 状态码 | 错误信息 | 说明 |
|--------|---------|------|
| 400 | Invalid email address | 邮箱格式不正确 |
| 404 | Email not found | 邮件 ID 不存在 |
| 500 | Internal server error | 服务器内部错误 |

### 查看错误详情

当邮件发送失败时，查询邮件状态会返回 `error_message` 字段，包含具体错误信息：

```bash
curl http://172.16.72.73:10001/api/emails/status/1
```

响应中的 `error_message` 字段说明失败原因：
- "SMTP connection failed" - SMTP 连接失败
- "Authentication failed" - 认证失败
- "File not found: /path/to/file" - 附件文件不存在
- "Unknown error" - 未知错误

---

## 集成示例

### 批量发送邮件

**Python：**
```python
import requests

BASE_URL = "http://172.16.72.73:10001"

recipients = [
    "user1@example.com",
    "user2@example.com",
    "user3@example.com"
]

for email in recipients:
    response = requests.post(f"{BASE_URL}/api/emails/send", json={
        "to_email": email,
        "subject": "批量邮件",
        "body": "您好，这是一封批量邮件",
        "attachments": []
    })

    data = response.json()
    print(f"Sent to {email}, email_id: {data['email_id']}")
```

### 监控邮件发送状态

**Python：**
```python
import requests
import time

BASE_URL = "http://172.16.72.73:10001"
email_id = 1

while True:
    response = requests.get(f"{BASE_URL}/api/emails/status/{email_id}")
    data = response.json()

    print(f"Status: {data['status']}")

    if data['status'] in ['success', 'failed']:
        if data['error_message']:
            print(f"Error: {data['error_message']}")
        break

    time.sleep(5)  # 每5秒检查一次
```

---

## 常见问题

**Q: 邮件多久会发送？**
A: 邮件被提交后，会立即加入队列，通常在几秒内发送。实际发送时间取决于网络和 SMTP 服务器。

**Q: 附件有大小限制吗？**
A: 取决于 SMTP 服务器，通常支持 25MB 以内的文件。

**Q: 发送失败会自动重试吗？**
A: 会的，发送失败后会自动重试最多 3 次，每次间隔 60 秒。

**Q: 如何发送 HTML 邮件？**
A: 直接在 `body` 字段中使用 HTML 代码即可。

**Q: 能否发送多个附件？**
A: 可以，在 `attachments` 数组中添加多个文件路径。
