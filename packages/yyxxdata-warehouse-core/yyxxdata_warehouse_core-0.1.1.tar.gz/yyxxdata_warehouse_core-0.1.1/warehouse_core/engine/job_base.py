"""数据仓库作业基类 - 优化版本，专注 Ibis 数据处理封装"""

from typing import Any, Literal
import pandas as pd
import logging
import sys
from pathlib import Path
from abc import ABC, abstractmethod
from ibis.expr.types import Table as IbisTable
from warehouse_core.db.manager import DatabaseManager

logger = logging.getLogger(__name__)


class JobBase(ABC):
    """数据仓库作业基类 - 优化版本
    
    专注于 Ibis 数据处理封装，提供简洁高效的数据操作接口。
    
    核心功能：
    - 统一的数据库连接管理
    - Ibis 表达式操作封装
    - 数据读取/写入便捷方法
    - 基础的日志记录
    - 自动项目路径管理
    
    核心方法：
    - read_table(): 读取表数据
    - write_table(): 写入数据到表
    - table(): 获取 Ibis 表表达式
    - execute_sql(): 执行 SQL 查询
    - filter_table(): 过滤表数据
    
    便捷方法：
    - list_tables(): 列出所有表
    - table_exists(): 检查表是否存在
    - count_rows(): 统计表行数
    
    使用示例：
    ```python
    from warehouse_core import JobBase
    
    # 方式1：使用默认配置文件
    class MyJob(JobBase):
        def process(self):
            # 读取数据
            df = self.read_table('source_data')
            
            # 数据转换
            df['new_column'] = df['existing_column'] * 2
            
            # 写入数据
            self.write_table(df, 'target_data')
    
    # 方式2：使用自定义配置文件
    job = MyJob(db_name="mysql_prod", config_path="custom_config.yaml")
    job.run()
    
    # 方式3：直接传入配置对象
    config = {
        "databases": {
            "mysql_prod": {
                "type": "mysql",
                "host": "localhost",
                "port": 3306,
                "user": "user",
                "password": "password",
                "database": "warehouse"
            }
        }
    }
    job = MyJob(db_name="mysql_prod", config_object=config)
    job.run()
    ```
    """
    
    def __init__(self, db_name: str = 'sqlite_default', config_path: str | None = None, config_object: dict[str, Any] | None = None):
        """初始化作业基类
        
        Args:
            db_name: 数据库连接名称
            config_path: 配置文件路径（可选，默认使用 config/db_config.yaml）
            config_object: 配置字典（可选，直接传入配置对象，优先级高于 config_path）
        """
        # 自动添加项目根目录到 Python 路径
        self._ensure_project_path()
        
        self.db_name = db_name
        self.config_path = config_path
        self.config_object = config_object
        
        # 设置日志
        self.logger = logger
        
        # 使用单例 DatabaseManager，动态加载配置
        self._db_manager = DatabaseManager()
        self._db_manager.load_config(config_path=config_path, config_object=config_object)
        
        # 使用 Ibis 连接
        self.ibis_conn = self._db_manager.get_ibis_connection(db_name)
        
        self.logger.info(f"JobBase initialized with database: {db_name}")

    # ========== 核心数据操作方法 ==========
    
    def read_table(self, table_name: str, limit: int | None = None) -> pd.DataFrame:
        """读取表数据
        
        Args:
            table_name: 表名
            limit: 限制行数
            
        Returns:
            DataFrame
        """
        self.logger.info(f"Reading table: {table_name}")
        if limit:
            self.logger.info(f"Limit: {limit} rows")
        
        # 获取 Ibis 表对象
        table = self.ibis_conn.table(table_name)
        
        # 如果有限制，应用 limit
        if limit:
            table = table.limit(limit)
        
        # 执行查询并返回 DataFrame
        df = table.execute()
        self.logger.info(f"Read {len(df)} rows from {table_name}")
        return df
    
    def write_table(self, data: pd.DataFrame, table_name: str, 
                   if_exists: Literal['fail', 'replace', 'append'] = 'append') -> int:
        """写入数据到表
        
        Args:
            data: DataFrame 数据
            table_name: 目标表名
            if_exists: 表存在时的处理方式 ('fail', 'replace', 'append')
            
        Returns:
            写入的行数
        """
        self.logger.info(f"Writing {len(data)} rows to table: {table_name}")
        result = self.ibis_conn.write_table(data, table_name, if_exists=if_exists)
        self.logger.info(f"Successfully wrote {result} rows")
        return result
    
    def table(self, table_name: str) -> IbisTable:
        """获取 Ibis 表对象
        
        Args:
            table_name: 表名
            
        Returns:
            Ibis 表达式
        """
        self.logger.info(f"Getting table object: {table_name}")
        return self.ibis_conn.table(table_name)
    
    def execute_sql(self, sql: str) -> pd.DataFrame:
        """执行 SQL 查询
        
        Args:
            sql: SQL 语句
            
        Returns:
            查询结果的 DataFrame
        """
        self.logger.info(f"Executing SQL: {sql[:100]}...")
        return self.ibis_conn.execute_query(sql)
    
    # ========== 便捷方法 ==========
    
    def list_tables(self) -> list[str]:
        """列出所有表
        
        Returns:
            表名列表
        """
        tables = self.ibis_conn.list_tables()
        self.logger.info(f"Available tables: {tables}")
        return tables
    
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在
        
        Args:
            table_name: 表名
            
        Returns:
            是否存在
        """
        return table_name in self.list_tables()
    
    def count_rows(self, table_name: str) -> int:
        """统计表行数
        
        Args:
            table_name: 表名
            
        Returns:
            行数
        """
        table = self.table(table_name)
        count = table.count().execute()
        self.logger.info(f"Table {table_name} has {count} rows")
        return count
    
    # ========== Ibis 高级操作 ==========
    
    def filter_table(self, table_name: str, **filters) -> IbisTable:
        """过滤表数据
        
        Args:
            table_name: 表名
            **filters: 过滤条件，格式为 column=value
            
        Returns:
            过滤后的 Ibis 表达式
        """
        self.logger.info(f"Filtering table {table_name} with conditions: {filters}")
        
        table = self.table(table_name)
        
        for column, value in filters.items():
            if isinstance(value, (list, tuple)):
                # IN 条件
                table = table.filter(getattr(table, column).isin(value))
            else:
                # 等值条件
                table = table.filter(getattr(table, column) == value)
        
        return table
    
    # ========== 作业执行框架 ==========
    
    @abstractmethod
    def process(self):
        """业务逻辑处理方法 - 子类必须实现
        
        子类需要在这个方法中实现具体的数据处理逻辑。
        可以使用 self.read_table(), self.write_table() 等方法进行数据操作。
        """
        pass
    
    def run(self):
        """运行作业
        
        执行作业的生命周期：
        1. 记录开始日志
        2. 调用 process() 方法
        3. 记录完成日志
        4. 处理异常
        """
        try:
            self.logger.info(f"Job started: {self.__class__.__name__}")
            self.process()
            self.logger.info(f"Job completed: {self.__class__.__name__}")
        except Exception as e:
            self.logger.error(f"Job failed: {self.__class__.__name__}, error: {e}")
            raise
    
    def _ensure_project_path(self):
        """确保项目根目录在 Python 路径中
        
        自动检测并添加项目根目录到 sys.path，使得业务代码无需手动处理路径问题。
        """
        try:
            # 获取当前文件所在目录的父目录（项目根目录）
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            
            # 转换为字符串路径
            project_root_str = str(project_root)
            
            # 检查是否已经在 sys.path 中
            if project_root_str not in sys.path:
                sys.path.insert(0, project_root_str)
                logger.info(f"已添加项目路径到 Python 路径: {project_root_str}")
            else:
                logger.debug(f"项目路径已存在于 Python 路径中: {project_root_str}")
                
        except Exception as e:
            logger.warning(f"自动添加项目路径时出现问题: {e}")
            # 不抛出异常，继续执行初始化