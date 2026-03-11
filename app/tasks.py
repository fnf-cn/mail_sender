import asyncio
from celery import Celery
from app.config import get_settings
from app.email_service import EmailService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Email, EmailStatus, Base
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

# 初始化 Celery
celery_app = Celery(
    "mail_sender",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# 配置 Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# 初始化数据库
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(bind=True, max_retries=3)
def send_email_task(
    self,
    email_id: int,
    to_email: str,
    subject: str,
    body: str,
    attachment_paths: list = None,
):
    """
    异步邮件发送任务

    Args:
        email_id: 邮件数据库 ID
        to_email: 收件人
        subject: 主题
        body: 正文
        attachment_paths: 附件列表
    """
    db = SessionLocal()
    try:
        # 更新邮件状态为发送中
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            logger.error(f"Email record not found: {email_id}")
            return

        email.status = EmailStatus.SENDING
        db.commit()

        # 发送邮件
        email_service = EmailService()
        result = asyncio.run(
            email_service.send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                attachment_paths=attachment_paths,
            )
        )

        # 更新邮件状态
        if result["success"]:
            email.status = EmailStatus.SUCCESS
            email.sent_at = datetime.utcnow()
            logger.info(f"Email {email_id} sent successfully")
        else:
            email.status = EmailStatus.FAILED
            email.error_message = result.get("error", "Unknown error")
            logger.error(f"Email {email_id} failed: {email.error_message}")

        db.commit()

    except Exception as exc:
        email = db.query(Email).filter(Email.id == email_id).first()
        if email:
            email.status = EmailStatus.FAILED
            email.error_message = str(exc)
            db.commit()

        logger.error(f"Task failed for email {email_id}: {str(exc)}")

        # 重试
        try:
            self.retry(exc=exc, countdown=60)  # 60 秒后重试
        except Exception as retry_exc:
            logger.error(f"Task {self.request.id} failed: {str(retry_exc)}")

    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)
