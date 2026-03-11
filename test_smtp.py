"""
SMTP 配置测试脚本 - 快速验证邮件发送配置
支持多种 SMTP 连接方式，适配企业邮件服务器
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import sys

# 加载 .env 文件
load_dotenv()

# 获取 SMTP 配置
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Mail Sender")

# 测试邮件配置
TO_EMAIL = "yuanbiny@fnfcorp.com"
TEST_SUBJECT = "SMTP 配置测试邮件"
TEST_BODY = """
这是一封 SMTP 配置测试邮件。

如果你收到这封邮件，说明以下配置成功：
- SMTP 服务器连接成功
- 用户认证成功
- 邮件发送成功

邮件配置信息：
- SMTP 服务器: {smtp_host}
- SMTP 端口: {smtp_port}
- 发件人: {from_email}

祝贺！你的邮件系统配置成功！🎉
""".format(
    smtp_host=SMTP_HOST,
    smtp_port=SMTP_PORT,
    from_email=SMTP_FROM_EMAIL,
)


def test_smtp_connection():
    """测试 SMTP 连接 - 支持多种连接方式"""
    print("=" * 70)
    print("SMTP 配置测试 - 企业邮件服务器")
    print("=" * 70)
    print()

    # 打印配置信息
    print("📋 配置信息：")
    print(f"  SMTP 服务器: {SMTP_HOST}")
    print(f"  SMTP 端口: {SMTP_PORT}")
    print(f"  用户: {SMTP_USER}")
    print(f"  发件人: {SMTP_FROM_EMAIL} ({SMTP_FROM_NAME})")
    print(f"  测试收件人: {TO_EMAIL}")
    print()

    # 验证配置完整性
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL]):
        print("❌ 配置不完整，请检查 .env 文件:")
        print(f"  SMTP_HOST: {'✓' if SMTP_HOST else '✗'}")
        print(f"  SMTP_PORT: {'✓' if SMTP_PORT else '✗'}")
        print(f"  SMTP_USER: {'✓' if SMTP_USER else '✗'}")
        print(f"  SMTP_PASSWORD: {'✓' if SMTP_PASSWORD else '✗'}")
        print(f"  SMTP_FROM_EMAIL: {'✓' if SMTP_FROM_EMAIL else '✗'}")
        return False

    # 尝试多种连接方式
    connection_methods = []

    # 方法 1: TLS (STARTTLS) - 通常用于 587 端口
    if SMTP_PORT == 587:
        connection_methods.append({
            "name": "SMTP + STARTTLS (587 端口)",
            "port": 587,
            "use_tls": True,
            "use_ssl": False,
        })

    # 方法 2: SSL - 通常用于 465 端口
    if SMTP_PORT == 465:
        connection_methods.append({
            "name": "SMTP + SSL (465 端口)",
            "port": 465,
            "use_tls": False,
            "use_ssl": True,
        })

    # 方法 3: 无加密 - 用于企业内网或 25 端口
    connection_methods.append({
        "name": "纯 SMTP (无加密)",
        "port": SMTP_PORT,
        "use_tls": False,
        "use_ssl": False,
    })

    # 方法 4: 强制尝试另一种 TLS 方式
    if SMTP_PORT not in [465, 587]:
        connection_methods.append({
            "name": f"SMTP + STARTTLS ({SMTP_PORT} 端口)",
            "port": SMTP_PORT,
            "use_tls": True,
            "use_ssl": False,
        })

    # 尝试每种连接方式
    for method in connection_methods:
        print(f"🔄 尝试连接方式: {method['name']}")
        print("-" * 70)

        try:
            # 步骤 1: 连接
            print(f"  📡 步骤 1: 连接到 {SMTP_HOST}:{method['port']}...")

            if method["use_ssl"]:
                # SSL 连接
                context = ssl.create_default_context()
                smtp = smtplib.SMTP_SSL(
                    SMTP_HOST,
                    method["port"],
                    context=context,
                    timeout=10,
                )
                print(f"    ✓ SSL 连接成功")
            else:
                # 普通连接
                smtp = smtplib.SMTP(SMTP_HOST, method["port"], timeout=10)
                print(f"    ✓ 连接成功")

                # 步骤 2: STARTTLS (如果需要)
                if method["use_tls"]:
                    print(f"  🔒 步骤 2: 启动 TLS 加密...")
                    context = ssl.create_default_context()
                    smtp.starttls(context=context)
                    print(f"    ✓ TLS 加密已启动")

            # 步骤 3: 认证
            print(f"  🔑 步骤 3: 用户认证 ({SMTP_USER})...")
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            print(f"    ✓ 认证成功")

            # 步骤 4: 发送邮件
            print(f"  📧 步骤 4: 发送测试邮件到 {TO_EMAIL}...")
            message = MIMEMultipart()
            message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
            message["To"] = TO_EMAIL
            message["Subject"] = TEST_SUBJECT
            message.attach(MIMEText(TEST_BODY, "plain", "utf-8"))

            smtp.send_message(message)
            print(f"    ✓ 邮件发送成功")

            # 关闭连接
            smtp.quit()

            # 成功！
            print()
            print("=" * 70)
            print("✅ 所有测试通过！SMTP 配置成功！")
            print("=" * 70)
            print()
            print("📌 成功的连接方式:")
            print(f"  {method['name']}")
            print()
            print("📌 下一步：")
            print("  1. ✓ 检查邮箱 (yuanbiny@fnfcorp.com) 确认收到测试邮件")
            print("  2. ✓ 如果收到邮件，说明配置完全正确")
            print("  3. 启动完整的邮件服务:")
            print()
            print("     # 终端 1: 启动 Redis")
            print("     redis-server")
            print()
            print("     # 终端 2: 启动 Celery Worker")
            print("     celery -A app.tasks worker --loglevel=info")
            print()
            print("     # 终端 3: 启动 FastAPI")
            print("     python -m uvicorn app.main:app --host 0.0.0.0 --port 10001 --reload")
            print()
            print("     # 浏览器: 访问 API 文档")
            print("     http://localhost:10001/docs")
            print()
            return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"    ✗ 认证失败: {str(e)}")
            print()
            continue

        except smtplib.SMTPException as e:
            print(f"    ✗ SMTP 错误: {str(e)}")
            print()
            continue

        except Exception as e:
            error_str = str(e)
            if "timed out" in error_str.lower():
                print(f"    ✗ 连接超时: {error_str}")
            elif "connection refused" in error_str.lower():
                print(f"    ✗ 连接被拒绝: {error_str}")
            else:
                print(f"    ✗ 错误: {error_str}")
            print()
            continue

    # 所有方法都失败
    print("=" * 70)
    print("❌ 所有连接方式都失败！")
    print("=" * 70)
    print()
    print("🔧 排查步骤:")
    print()
    print("1️⃣ 验证 SMTP 服务器信息:")
    print(f"   • 服务器地址: {SMTP_HOST}")
    print(f"   • 端口号: {SMTP_PORT}")
    print(f"   • 用户名: {SMTP_USER}")
    print(f"   • 密码: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else '(未设置)'}")
    print()
    print("2️⃣ 网络连接测试:")
    print(f"   # Windows 测试连接")
    print(f"   Test-NetConnection -ComputerName {SMTP_HOST} -Port {SMTP_PORT}")
    print()
    print(f"   # Linux/Mac 测试连接")
    print(f"   telnet {SMTP_HOST} {SMTP_PORT}")
    print()
    print("3️⃣ 常见 SMTP 配置:")
    print("   • Gmail: smtp.gmail.com:587 (需要应用专用密码)")
    print("   • Office 365: smtp.office365.com:587")
    print("   • QQ 邮箱: smtp.qq.com:587")
    print("   • 企业邮箱: 咨询 IT 部门获取服务器地址和端口")
    print()
    print("4️⃣ 防火墙和代理:")
    print("   • 确保防火墙允许出站邮件协议 (SMTP)")
    print("   • 如果在公司网络，检查是否需要配置代理")
    print()
    print("5️⃣ 修改 .env 文件尝试其他端口:")
    print("   • 如果当前使用 587，尝试改为 465")
    print("   • 如果当前使用 465，尝试改为 587")
    print("   • 企业邮箱可能使用 25 端口")
    print()
    return False


def main():
    """主函数"""
    try:
        result = test_smtp_connection()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
