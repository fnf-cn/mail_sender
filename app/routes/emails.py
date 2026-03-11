from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.schemas import EmailSendRequest, EmailResponse, EmailListResponse, EmailStatusResponse
from app.models import Email, EmailStatus
from app.tasks import send_email_task
from app.database import get_db

router = APIRouter(prefix="/api/emails", tags=["emails"])


@router.post("/send", response_model=dict, summary="发送邮件")
async def send_email(
    request: EmailSendRequest,
    db: Session = Depends(get_db),
):
    """
    发送邮件

    - **to_email**: 收件人邮箱
    - **subject**: 邮件主题
    - **body**: 邮件正文
    - **attachments**: 附件文件路径列表（可选）
    """
    try:
        # 保存邮件记录到数据库
        attachment_str = ",".join(request.attachments) if request.attachments else None
        email = Email(
            to_email=request.to_email,
            subject=request.subject,
            body=request.body,
            attachment_paths=attachment_str,
            status=EmailStatus.PENDING,
        )
        db.add(email)
        db.commit()
        db.refresh(email)

        # 将邮件发送任务添加到队列
        send_email_task.delay(
            email_id=email.id,
            to_email=request.to_email,
            subject=request.subject,
            body=request.body,
            attachment_paths=request.attachments,
        )

        return {
            "success": True,
            "message": "Email queued for sending",
            "email_id": email.id,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{email_id}", response_model=EmailStatusResponse, summary="查询邮件发送状态")
def get_email_status(email_id: int, db: Session = Depends(get_db)):
    """
    查询邮件发送状态

    - **email_id**: 邮件 ID
    """
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    return email


@router.get("/", response_model=EmailListResponse, summary="查询邮件列表")
def list_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[EmailStatus] = None,
    db: Session = Depends(get_db),
):
    """
    查询邮件列表

    - **skip**: 跳过的记录数（默认 0）
    - **limit**: 每页记录数（默认 10，最多 100）
    - **status**: 邮件状态筛选（可选）
    """
    query = db.query(Email)

    if status:
        query = query.filter(Email.status == status)

    total = query.count()
    items = query.order_by(Email.created_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "items": items}


@router.get("/search", response_model=EmailListResponse, summary="搜索邮件")
def search_emails(
    to_email: Optional[str] = None,
    subject: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    搜索邮件

    - **to_email**: 收件人邮箱（模糊匹配）
    - **subject**: 邮件主题（模糊匹配）
    - **skip**: 跳过的记录数
    - **limit**: 每页记录数
    """
    query = db.query(Email)

    if to_email:
        query = query.filter(Email.to_email.ilike(f"%{to_email}%"))

    if subject:
        query = query.filter(Email.subject.ilike(f"%{subject}%"))

    total = query.count()
    items = query.order_by(Email.created_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "items": items}
