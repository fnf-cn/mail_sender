from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EmailStatus(str, Enum):
    PENDING = "pending"
    SENDING = "sending"
    SUCCESS = "success"
    FAILED = "failed"


class EmailSendRequest(BaseModel):
    """邮件发送请求"""
    to_email: EmailStr = Field(..., description="收件人邮箱")
    subject: str = Field(..., min_length=1, max_length=255, description="邮件主题")
    body: str = Field(..., min_length=1, description="邮件正文")
    attachments: Optional[List[str]] = Field(None, description="附件文件路径列表")

    class Config:
        json_schema_extra = {
            "example": {
                "to_email": "recipient@example.com",
                "subject": "Test Email",
                "body": "This is a test email body",
                "attachments": ["/path/to/file1.pdf", "/path/to/file2.xlsx"]
            }
        }


class EmailResponse(BaseModel):
    """邮件响应"""
    id: int
    to_email: str
    subject: str
    status: EmailStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class EmailListResponse(BaseModel):
    """邮件列表响应"""
    total: int
    items: List[EmailResponse]


class EmailStatusResponse(BaseModel):
    """邮件状态响应"""
    id: int
    to_email: str
    subject: str
    status: EmailStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
