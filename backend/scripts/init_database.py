#!/usr/bin/env python3
"""创建 MySQL 数据库并执行 Alembic 迁移。

用法（在 backend 目录下）：
    python scripts/init_database.py

依赖：
    - MySQL 8 已启动
    - backend/.env 已配置 MYSQL_* 或 DATABASE_URL
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import pymysql
from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(BACKEND_ROOT / ".env")

from app.config import settings  # noqa: E402


def _parse_mysql_settings() -> dict[str, str | int]:
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "password")
    database = os.getenv("MYSQL_DATABASE", "w_ai_learn")

    if settings.database_url:
        parsed = urlparse(settings.database_url.replace("+asyncmy", "").replace("+pymysql", ""))
        if parsed.hostname:
            host = parsed.hostname
        if parsed.port:
            port = parsed.port
        if parsed.username:
            user = parsed.username
        if parsed.password:
            password = parsed.password
        if parsed.path and parsed.path.strip("/"):
            database = parsed.path.strip("/").split("?")[0]

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
    }


def create_database_if_not_exists() -> None:
    cfg = _parse_mysql_settings()
    database = str(cfg.pop("database"))

    print(f"连接 MySQL {cfg['host']}:{cfg['port']} …")
    connection = pymysql.connect(**cfg, charset="utf8mb4")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        connection.commit()
        print(f"数据库 `{database}` 已就绪")
    finally:
        connection.close()


def run_alembic_upgrade() -> None:
    print("执行 Alembic 迁移 alembic upgrade head …")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_ROOT,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    print("迁移完成")


def main() -> None:
    create_database_if_not_exists()
    run_alembic_upgrade()
    print("数据库初始化成功。")


if __name__ == "__main__":
    main()
