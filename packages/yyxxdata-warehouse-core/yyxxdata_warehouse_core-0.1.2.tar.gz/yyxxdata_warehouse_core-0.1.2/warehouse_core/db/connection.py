"""数据库连接管理"""

from typing import Any
from contextlib import contextmanager
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """数据库连接类 - 支持多种数据库类型"""
    
    def __init__(self, config: dict[str, Any]):
        """初始化数据库连接
        
        Args:
            config: 数据库配置字典
        """
        self.config = config
        self.db_type = config.get('type', 'mysql')
        self._engine: Engine | None = None
        
    def _build_connection_url(self) -> str:
        """构建数据库连接 URL
        
        Returns:
            数据库连接字符串
        """
        if self.db_type == 'mysql':
            return (
                f"mysql+pymysql://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
                f"?charset={self.config.get('charset', 'utf8mb4')}"
            )
        elif self.db_type == 'postgresql':
            return (
                f"postgresql+psycopg2://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )
        elif self.db_type == 'sqlite':
            return f"sqlite:///{self.config['database']}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def get_engine(self) -> Engine:
        """获取数据库引擎（单例模式）
        
        Returns:
            SQLAlchemy Engine 对象
        """
        if self._engine is None:
            connection_url = self._build_connection_url()
            pool_size = self.config.get('pool_size', 5)
            pool_recycle = self.config.get('pool_recycle', 3600)
            
            self._engine = create_engine(
                connection_url,
                poolclass=QueuePool,
                pool_size=pool_size,
                pool_recycle=pool_recycle,
                pool_pre_ping=True,  # 连接前检查
                echo=False
            )
            logger.info(f"Database engine created: {self.db_type}")
        
        return self._engine
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）
        
        Yields:
            数据库连接对象
        """
        engine = self.get_engine()
        connection = engine.connect()
        try:
            yield connection
        finally:
            connection.close()
    
    def execute_query(self, sql: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        """执行 SQL 查询并返回 DataFrame
        
        Args:
            sql: SQL 查询语句
            params: SQL 参数字典
            
        Returns:
            查询结果的 DataFrame
        """
        try:
            with self.get_connection() as conn:
                if params:
                    result = pd.read_sql(text(sql), conn, params=params)
                else:
                    result = pd.read_sql(text(sql), conn)
                logger.info(f"Query executed successfully, rows: {len(result)}")
                return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_insert(self, table_name: str, data: pd.DataFrame, 
                      if_exists: str = 'append') -> int:
        """插入数据到数据库表
        
        Args:
            table_name: 目标表名
            data: 要插入的 DataFrame
            if_exists: 表已存在时的操作 ('fail', 'replace', 'append')
            
        Returns:
            插入的行数
        """
        try:
            engine = self.get_engine()
            rows = data.to_sql(
                table_name,
                engine,
                if_exists=if_exists,
                index=False,
                chunksize=1000
            )
            logger.info(f"Data inserted to {table_name}, rows: {len(data)}")
            return len(data)
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            raise
    
    def execute_sql(self, sql: str, params: dict[str, Any] | None = None) -> int:
        """执行 SQL 语句（INSERT/UPDATE/DELETE）
        
        Args:
            sql: SQL 语句
            params: SQL 参数字典
            
        Returns:
            影响的行数
        """
        try:
            with self.get_connection() as conn:
                if params:
                    result = conn.execute(text(sql), params)
                else:
                    result = conn.execute(text(sql))
                conn.commit()
                affected_rows = result.rowcount
                logger.info(f"SQL executed successfully, affected rows: {affected_rows}")
                return affected_rows
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logger.info("Database connection closed")
