"""
邮件发送 API 测试脚本
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:10001"


def send_email(
    to_email: str,
    subject: str,
    body: str,
    attachments: Optional[list] = None,
) -> dict:
    """测试发送邮件接口"""
    url = f"{BASE_URL}/api/emails/send"
    payload = {
        "to_email": to_email,
        "subject": subject,
        "body": body,
    }
    if attachments:
        payload["attachments"] = attachments

    response = requests.post(url, json=payload)
    print(f"POST {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.json()


def get_email_status(email_id: int) -> dict:
    """测试查询邮件状态接口"""
    url = f"{BASE_URL}/api/emails/status/{email_id}"
    response = requests.get(url)
    print(f"GET {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, default=str)}\n")
    return response.json()


def list_emails(skip: int = 0, limit: int = 10, status: Optional[str] = None) -> dict:
    """测试查询邮件列表接口"""
    url = f"{BASE_URL}/api/emails/?skip={skip}&limit={limit}"
    if status:
        url += f"&status={status}"

    response = requests.get(url)
    print(f"GET {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, default=str)}\n")
    return response.json()


def search_emails(
    to_email: Optional[str] = None,
    subject: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
) -> dict:
    """测试搜索邮件接口"""
    url = f"{BASE_URL}/api/emails/search?skip={skip}&limit={limit}"
    if to_email:
        url += f"&to_email={to_email}"
    if subject:
        url += f"&subject={subject}"

    response = requests.get(url)
    print(f"GET {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, default=str)}\n")
    return response.json()


def health_check() -> dict:
    """测试健康检查接口"""
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    print(f"GET {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.json()


if __name__ == "__main__":
    print("=" * 50)
    print("Mail Sender API - Test Script")
    print("=" * 50 + "\n")

    # 1. 健康检查
    print("1. Testing Health Check:")
    health_check()

    # 2. 发送邮件
    print("2. Testing Send Email:")
    result = send_email(
        to_email="test@example.com",
        subject="Test Email",
        body="This is a test email from Mail Sender API",
        attachments=None,  # 可选：["/path/to/file.pdf"]
    )
    email_id = result.get("email_id")

    # 3. 查询邮件状态
    if email_id:
        print(f"3. Testing Get Email Status (ID: {email_id}):")
        import time

        time.sleep(1)  # 等待任务处理
        get_email_status(email_id)

    # 4. 查询邮件列表
    print("4. Testing List Emails:")
    list_emails()

    # 5. 搜索邮件
    print("5. Testing Search Emails:")
    search_emails(to_email="example.com")

    print("=" * 50)
    print("✓ Tests completed!")
    print("=" * 50)
