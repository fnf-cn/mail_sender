import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import List, Optional
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """邮件发送服务"""

    def __init__(self):
        self.settings = get_settings()

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachment_paths: Optional[List[str]] = None,
    ) -> dict:
        """
        发送邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            body: 邮件正文
            attachment_paths: 附件文件路径列表

        Returns:
            发送结果字典
        """
        try:
            # 创建邮件
            message = MIMEMultipart()
            message["From"] = f"{self.settings.smtp_from_name} <{self.settings.smtp_from_email}>"
            message["To"] = to_email
            message["Subject"] = subject

            # 添加邮件正文（自动检测 HTML）
            content_type = "html" if body.strip().startswith("<") else "plain"
            message.attach(MIMEText(body, content_type, "utf-8"))

            # 添加附件
            if attachment_paths:
                for file_path in attachment_paths:
                    try:
                        self._attach_file(message, file_path)
                    except Exception as e:
                        logger.warning(f"Failed to attach file {file_path}: {str(e)}")

            # 发送邮件
            async with aiosmtplib.SMTP(
                hostname=self.settings.smtp_host,
                port=self.settings.smtp_port,
            ) as smtp:
                await smtp.login(self.settings.smtp_user, self.settings.smtp_password)
                await smtp.send_message(message)

            logger.info(f"Email sent successfully to {to_email}")
            return {"success": True, "message": "Email sent successfully"}

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to send email to {to_email}: {error_msg}")
            return {"success": False, "error": error_msg}

    def _attach_file(self, message: MIMEMultipart, file_path: str) -> None:
        """
        添加附件到邮件

        Args:
            message: MIMEMultipart 对象
            file_path: 文件路径
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Attachment file not found: {file_path}")

        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        filename = os.path.basename(file_path)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        message.attach(part)


async def get_email_service() -> EmailService:
    """获取邮件服务实例"""
    return EmailService()
