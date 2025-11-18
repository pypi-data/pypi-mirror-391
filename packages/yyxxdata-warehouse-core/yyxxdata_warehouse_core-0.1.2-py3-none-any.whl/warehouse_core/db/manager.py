"""数据库管理器 - 统一管理 SQLAlchemy 与 Ibis 连接"""

from __future__ import annotations

from typing import Any
import logging
import os
import yaml

from warehouse_core.db.connection import DatabaseConnection
from warehouse_core.db.ibis_connection import IbisConnection

logger = logging.getLogger(__name__)

BackendConnection = DatabaseConnection | IbisConnection


class DatabaseManager:
    """数据库管理器 - 单例模式

    负责：
    1. 读取指定路径的数据库配置文件或配置对象
    2. 懒加载并缓存 Ibis 或 SQLAlchemy 连接
    3. 提供类型安全的获取接口
    
    Args:
        config_path: 配置文件路径（可选）
        config_object: 配置字典对象（可选，优先级高于 config_path）
    """

    _instance: "DatabaseManager" | None = None

    def __new__(cls, config_path: str | None = None, config_object: dict[str, Any] | None = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path: str | None = None, config_object: dict[str, Any] | None = None):
        # 每次初始化都刷新配置路径，便于调用方覆盖配置文件位置
        self._config_file_path: str | None = config_path

        if getattr(self, "_initialized", False):
            return

        self._connections: dict[tuple[str, str], BackendConnection] = {}
        self._db_configs: dict[str, dict[str, Any]] = {}
        self._default_use_ibis: bool = True  # 默认使用 Ibis

        # 加载配置：优先使用配置对象，否则使用配置文件
        if config_object is not None:
            self.load_config_from_dict(config_object)
        else:
            self._load_config()
        
        self._initialized: bool = True

    # ------------------------------------------------------------------
    # 配置加载与缓存
    # ------------------------------------------------------------------
    def _config_path(self) -> str:
        if self._config_file_path:
            # 使用调用方提供的配置路径（相对或绝对路径）
            if os.path.isabs(self._config_file_path):
                return self._config_file_path
            else:
                # 相对路径：相对于当前工作目录
                return os.path.abspath(self._config_file_path)
        else:
            # 默认路径：从 warehouse_core/db/manager.py 向上找到项目根目录
            current_dir = os.path.dirname(__file__)  # warehouse_core/db/
            warehouse_core_dir = os.path.dirname(current_dir)  # warehouse_core/
            project_root = os.path.dirname(warehouse_core_dir)  # 项目根目录
            return os.path.join(project_root, "config", "db_config.yaml")

    def _load_config(self) -> None:
        config_path = self._config_path()

        if not os.path.exists(config_path):
            logger.warning("Database config file not found: %s", config_path)
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                raw_config = yaml.safe_load(f) or {}
        except Exception as exc:
            logger.error("Failed to load database config: %s", exc)
            raise

        databases = raw_config.get("databases", {})
        for db_name, db_config in databases.items():
            self._db_configs[db_name] = db_config
            logger.debug("Database config registered: %s", db_name)

        # 从配置文件中读取默认后端设置
        self._default_use_ibis = raw_config.get("default_use_ibis", True)

    def load_config_from_dict(self, config_object: dict[str, Any]) -> None:
        """从配置字典加载数据库配置
        
        Args:
            config_object: 配置字典，格式应与 YAML 配置文件相同
        """
        databases = config_object.get("databases", {})
        for db_name, db_config in databases.items():
            self._db_configs[db_name] = db_config
            logger.debug("Database config registered from dict: %s", db_name)

        # 从配置对象中读取默认后端设置
        self._default_use_ibis = config_object.get("default_use_ibis", True)

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------
    def _make_cache_key(self, db_name: str, backend: str) -> tuple[str, str]:
        return db_name, backend

    def _get_config(self, db_name: str) -> dict[str, Any]:
        if db_name not in self._db_configs:
            raise ValueError(f"Database configuration not found: {db_name}")
        return self._db_configs[db_name]

    def _resolve_backend(self, db_name: str, prefer_ibis: bool | None) -> str:
        config = self._get_config(db_name)
        use_ibis = config.get("use_ibis", self._default_use_ibis)
        if prefer_ibis is not None:
            use_ibis = prefer_ibis
        return "ibis" if use_ibis else "sqlalchemy"

    def _create_connection(self, db_name: str, backend: str) -> BackendConnection:
        config = self._get_config(db_name)
        if backend == "ibis":
            logger.info("Creating Ibis connection: %s", db_name)
            return IbisConnection(config)

        logger.info("Creating SQLAlchemy connection: %s", db_name)
        return DatabaseConnection(config)

    def _get_or_create_connection(
        self,
        db_name: str,
        prefer_ibis: bool | None = None
    ) -> BackendConnection:
        backend = self._resolve_backend(db_name, prefer_ibis)
        cache_key = self._make_cache_key(db_name, backend)

        if cache_key not in self._connections:
            self._connections[cache_key] = self._create_connection(db_name, backend)

        return self._connections[cache_key]

    def _evict_cached_connections(self, db_name: str) -> None:
        keys_to_delete = [key for key in self._connections if key[0] == db_name]
        for cache_key in keys_to_delete:
            connection = self._connections.pop(cache_key)
            try:
                connection.close()
            except Exception as exc:
                logger.warning("Failed to close connection %s: %s", cache_key, exc)

    # ------------------------------------------------------------------
    # 对外接口
    # ------------------------------------------------------------------
    def list_connections(self) -> dict[str, dict[str, Any]]:
        """返回当前已注册的数据库配置字典"""
        return dict(self._db_configs)

    def get_connection(
        self,
        db_name: str = "mysql_default",
        prefer_ibis: bool | None = None
    ) -> BackendConnection:
        """获取数据库连接（根据配置或调用方偏好选择实现）"""
        return self._get_or_create_connection(db_name, prefer_ibis)

    def get_ibis_connection(self, db_name: str = "mysql_default") -> IbisConnection:
        connection = self._get_or_create_connection(db_name, prefer_ibis=True)
        if not isinstance(connection, IbisConnection):
            raise TypeError(f"Connection {db_name} is not an Ibis connection")
        return connection

    def get_sqlalchemy_connection(self, db_name: str = "mysql_default") -> DatabaseConnection:
        connection = self._get_or_create_connection(db_name, prefer_ibis=False)
        if not isinstance(connection, DatabaseConnection):
            raise TypeError(f"Connection {db_name} is not a SQLAlchemy connection")
        return connection

    def add_connection(
        self,
        db_name: str,
        config: dict[str, Any],
        use_ibis: bool | None = None,
        replace: bool = True
    ) -> BackendConnection:
        """动态添加或更新数据库配置并返回连接实例"""
        if use_ibis is not None:
            config = dict(config)
            config["use_ibis"] = use_ibis

        if replace or db_name not in self._db_configs:
            self._db_configs[db_name] = config
        else:
            merged = dict(self._db_configs[db_name])
            merged.update(config)
            self._db_configs[db_name] = merged

        # 清理旧连接，确保新配置生效
        self._evict_cached_connections(db_name)

        return self._get_or_create_connection(db_name, prefer_ibis=use_ibis)

    def close_connection(
        self,
        db_name: str,
        prefer_ibis: bool | None = None
    ) -> None:
        """关闭特定连接并从缓存中移除"""
        backend = self._resolve_backend(db_name, prefer_ibis)
        cache_key = self._make_cache_key(db_name, backend)
        connection = self._connections.pop(cache_key, None)
        if connection is None:
            return
        try:
            connection.close()
            logger.info("Database connection closed: %s (%s)", db_name, backend)
        except Exception as exc:
            logger.warning("Failed to close connection %s: %s", db_name, exc)

    def close_all(self) -> None:
        """关闭所有数据库连接并清理缓存"""
        for connection in self._connections.values():
            try:
                connection.close()
            except Exception as exc:
                logger.warning("Failed to close connection: %s", exc)
        self._connections.clear()

    def load_config(self, config_path: str | None = None, config_object: dict[str, Any] | None = None) -> None:
        """统一加载配置的方法
        
        Args:
            config_path: 配置文件路径（可选）
            config_object: 配置字典对象（可选，优先级高于 config_path）
        """
        # 更新配置路径
        self._config_file_path = config_path
        
        # 清理现有连接缓存
        self.close_all()
        self._db_configs.clear()
        
        # 加载新配置
        if config_object is not None:
            self.load_config_from_dict(config_object)
            logger.info("load config from dict")
        elif config_path is not None:
            self._load_config()
            logger.info(f"load config from config path: {config_path}")
        else:
            # 使用默认配置
            self._load_config()

    def reload_configs(self) -> None:
        """重新加载配置文件（主要用于测试或动态刷新场景）"""
        self.load_config(self._config_file_path)
