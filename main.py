import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from database import engine
from setup import setup

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

if __name__ == '__main__':
    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    application = setup()

    application.run_polling()
