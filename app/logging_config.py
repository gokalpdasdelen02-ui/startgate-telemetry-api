import sys
from pathlib import Path

from loguru import logger

LOG_DIR = Path("logs")


def setup_logging() -> None:
    LOG_DIR.mkdir(exist_ok=True)

    # logurunun varsayılan çıktısını kaldıran komut.
    logger.remove()

    # terminalde okunabilir çıktıyı sağlayan kod.
    logger.add(
        sys.stdout,
        level="INFO",
        serialize=False,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}:{function}:{line}</cyan>\n"
            "<level>{message}</level> | {extra}\n"
        ),
        backtrace=False,
        diagnose=False,
    )

    # dosyada yapılandırılmış json çıktısı
    logger.add(
        LOG_DIR / "app.json",
        level="INFO",
        serialize=True,
        backtrace=False,
        diagnose=False,
        rotation="10 MB",
        retention="7 Days",
    )
