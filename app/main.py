from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database import init_db
from app.routes import emails

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭事件处理"""
    # 启动事件
    logger.info("Starting Mail Sender Application")
    init_db()
    logger.info("Database initialized")
    yield
    # 关闭事件
    logger.info("Shutting down Mail Sender Application")


# 创建 FastAPI 应用
app = FastAPI(
    title="Mail Sender API",
    description="邮件发送 API - 支持标题、收件人、正文、附件",
    version="1.0.0",
    lifespan=lifespan,
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(emails.router)


@app.get("/", tags=["root"])
def read_root():
    """根路由"""
    return {
        "message": "Mail Sender API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["health"])
def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
