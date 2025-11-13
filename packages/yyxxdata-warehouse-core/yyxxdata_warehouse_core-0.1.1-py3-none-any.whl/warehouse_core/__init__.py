"""Warehouse Core Library

提供数据库访问、Ibis 集成以及作业处理的基础能力。
"""

from warehouse_core.utils.logger import configure_logging

# 初始化默认日志配置
configure_logging(level="INFO")

from warehouse_core.db.manager import DatabaseManager
from warehouse_core.db.connection import DatabaseConnection
from warehouse_core.db.ibis_connection import IbisConnection
from warehouse_core.engine.job_base import JobBase

__all__ = [
    "DatabaseManager",
    "DatabaseConnection", 
    "IbisConnection",
    "JobBase",
]
