"""基于 Ibis 的数据库连接管理"""

from typing import Any, Literal
import pandas as pd
import ibis
from ibis import BaseBackend
from ibis.expr.types import Table as IbisTable
import logging

logger = logging.getLogger(__name__)

try:  # 避免在未安装 PySpark 时导入失败
    from pyspark.sql import SparkSession  # type: ignore
except ImportError:  # pragma: no cover - 只有缺少依赖时才会触发
    SparkSession = None  # type: ignore


class IbisConnection:
    """基于 Ibis 的数据库连接类
    
    优势：
    1. 统一的 API 支持多种数据库后端
    2. 延迟执行和查询优化
    3. 类型安全的表达式构建
    4. 支持链式操作
    """
    
    def __init__(self, config: dict[str, Any]):
        """初始化 Ibis 连接
        
        Args:
            config: 数据库配置字典
        """
        self.config = config
        self.db_type = config.get('type', 'mysql')
        # 检查是否为 Doris（Doris 兼容 MySQL 协议但不支持事务）
        self.is_doris = config.get('backend_engine') == 'doris' or \
                       config.get('host', '').endswith('.doris') or \
                       'doris' in config.get('database', '').lower()
        self._backend: BaseBackend | None = None
        self._spark_session: "SparkSession" | None = None
        
    def _build_connection_url(self) -> str:
        """构建数据库连接 URL
        
        Returns:
            数据库连接字符串
        """
        if self.db_type == 'mysql':
            return (
                f"mysql://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )
        elif self.db_type == 'postgresql':
            return (
                f"postgresql://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )
        elif self.db_type == 'sqlite':
            return self.config['database']
        elif self.db_type == 'spark':
            return "spark://local"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    # ------------------------------------------------------------------
    # Spark 专用工具方法
    # ------------------------------------------------------------------
    def _get_or_create_spark_session(self) -> "SparkSession":
        if self.db_type != 'spark':
            raise RuntimeError("_get_or_create_spark_session only supports Spark backend")

        if SparkSession is None:
            raise ImportError(
                "pyspark 未安装。请在 Poetry 依赖中加入 pyspark 或通过 pip 安装。"
            )

        if self._spark_session is not None:
            return self._spark_session

        app_name = self.config.get('app_name', 'IbisSparkJob')
        master = self.config.get('master')
        spark_configs = self.config.get('spark_configs', {}) or {}

        builder = SparkSession.builder.appName(app_name)
        if master:
            builder = builder.master(master)
        for key, value in spark_configs.items():
            builder = builder.config(key, value)

        session = builder.getOrCreate()

        database = self.config.get('database')
        if database:
            try:
                session.catalog.setCurrentDatabase(database)
            except Exception as exc:  # pragma: no cover - 取决于 Spark 环境
                logger.warning("Failed to switch Spark database to %s: %s", database, exc)

        self._spark_session = session
        return session

    def _qualify_table_name(self, table_name: str) -> str:
        if self.db_type != 'spark':
            return table_name

        if "." in table_name:
            return table_name

        database = self.config.get('database')
        if database:
            return f"{database}.{table_name}"
        return table_name
    
    def get_backend(self) -> BaseBackend:
        """获取 Ibis 后端（单例模式）
        
        Returns:
            Ibis Backend 对象
        """
        if self._backend is None:
            try:
                if self.db_type == 'mysql':
                    # 对于 Ibis 11.0.0，MySQL 连接需要传递独立参数而不是 URL
                    # 注意：如果后端是 Doris，需要特殊处理事务问题
                    self._backend = ibis.mysql.connect(
                        host=self.config['host'],
                        port=self.config['port'],
                        user=self.config['user'],
                        password=self.config['password'],
                        database=self.config['database'],
                        autocommit=True
                    )
                    
                    # Doris 不支持事务，需要连接后立即清理事务状态
                    if self.is_doris or 'doris' in self.config.get('host', '').lower():
                        try:
                            self._backend.con.commit()  # 确保没有活跃事务
                        except Exception:
                            pass  # 忽略清理事务时的错误
                    
                elif self.db_type == 'postgresql':
                    self._backend = ibis.postgres.connect(
                        host=self.config['host'],
                        port=self.config['port'],
                        user=self.config['user'],
                        password=self.config['password'],
                        database=self.config['database']
                    )
                    
                elif self.db_type == 'sqlite':
                    db_path = self.config['database']
                    self._backend = ibis.sqlite.connect(db_path)

                elif self.db_type == 'spark':
                    spark_session = self._get_or_create_spark_session()
                    self._backend = ibis.pyspark.connect(
                        session=spark_session,
                        database=self.config.get('database')
                    )
                    
                else:
                    raise ValueError(f"Unsupported database type: {self.db_type}")
                
                logger.info(f"Ibis backend created: {self.db_type}")
                
            except Exception as e:
                logger.error(f"Failed to create Ibis backend: {e}")
                raise
        
        return self._backend
    
    def table(self, table_name: str) -> IbisTable:
        """获取表对象
        
        Args:
            table_name: 表名
            
        Returns:
            Ibis Table 对象
        """
        backend = self.get_backend()
        qualified_name = self._qualify_table_name(table_name)
        return backend.table(qualified_name)
    
    def list_tables(self) -> list[str]:
        """列出所有表
        
        Returns:
            表名列表
        """
        backend = self.get_backend()
        return backend.list_tables()
    
    def sql(self, query: str) -> IbisTable:
        """执行原始 SQL 查询
        
        Args:
            query: SQL 查询语句
            
        Returns:
            Ibis Table 表达式
        """
        backend = self.get_backend()
        return backend.sql(query)
    
    def execute_query(self, query: str | IbisTable, 
                     params: dict[str, Any] | None = None) -> pd.DataFrame:
        """执行查询并返回 DataFrame
        
        Args:
            query: SQL 查询语句或 Ibis 表达式
            params: SQL 参数字典（仅用于原始 SQL）
            
        Returns:
            查询结果的 DataFrame
        """
        try:
            backend = self.get_backend()
            
            # 如果是字符串，执行原始 SQL
            if isinstance(query, str):
                # Ibis 原生不支持参数化查询，需要手动替换
                if params:
                    for key, value in params.items():
                        # 简单的参数替换（生产环境建议使用更安全的方式）
                        query = query.replace(f":{key}", repr(value))
                
                # Doris 特殊处理：直接使用底层连接避免 Ibis 的事务问题
                if self.is_doris or 'doris' in self.config.get('host', '').lower():
                    return self._execute_doris_query(query, backend)
                
                result_expr = backend.sql(query)
            else:
                # 如果是 Ibis 表达式，直接使用
                result_expr = query
            
            # 执行查询并转换为 DataFrame
            result = result_expr.to_pandas()
            logger.info(f"Query executed successfully, rows: {len(result)}")
            return result
            
        except Exception as e:
            # 检查是否是 Doris 事务错误
            if 'This is in a transaction, only insert, commit, rollback is acceptable' in str(e):
                logger.warning("Detected Doris transaction limitation, using direct connection")
                return self._execute_doris_query(query, backend)
            
            logger.error(f"Query execution failed: {e}")
            raise
    
    def _execute_doris_query(self, query: str, backend: BaseBackend) -> pd.DataFrame:
        """Doris 专用查询方法，避免使用 Ibis 的事务机制
        
        Args:
            query: SQL 查询语句
            backend: Ibis backend
            
        Returns:
            查询结果的 DataFrame
        """
        try:
            # 直接使用底层 MySQL 连接，绕过 Ibis 的事务处理
            con = backend.con
            
            # 确保连接没有活跃事务
            try:
                con.commit()
            except Exception:
                pass
            
            # 直接执行查询
            import pandas as pd
            with con.cursor() as cursor:
                cursor.execute(query)
                # 获取列名
                columns = [desc[0] for desc in cursor.description]
                # 获取数据
                data = cursor.fetchall()
                result = pd.DataFrame(data, columns=columns)
            
            logger.info(f"Doris query executed successfully, rows: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"Doris direct query failed: {e}")
            raise
    
    def execute_insert(self, table_name: str, data: pd.DataFrame, 
                      if_exists: Literal['fail', 'replace', 'append'] = 'append') -> int:
        """插入数据到数据库表
        
        Args:
            table_name: 目标表名
            data: 要插入的 DataFrame
            if_exists: 表已存在时的操作 ('fail', 'replace', 'append')
            
        Returns:
            插入的行数
        """
        try:
            backend = self.get_backend()

            if self.db_type == 'spark':
                spark_session = self._get_or_create_spark_session()
                mode_map = {
                    'append': 'append',
                    'replace': 'overwrite',
                    'fail': 'error',
                }
                if if_exists not in mode_map:
                    raise ValueError(f"Unsupported if_exists mode for Spark: {if_exists}")

                spark_df = spark_session.createDataFrame(data)
                table_identifier = self._qualify_table_name(table_name)

                (spark_df
                 .write
                 .mode(mode_map[if_exists])
                 .saveAsTable(table_identifier))

                logger.info(
                    "Spark table written: %s, rows: %s, mode: %s",
                    table_identifier,
                    len(data),
                    mode_map[if_exists],
                )
                return len(data)
            
            # Ibis 通过 insert 方法插入数据
            # 但不是所有后端都支持，所以这里使用底层引擎
            if hasattr(backend, 'insert') and if_exists == 'append':
                try:
                    backend.insert(table_name, data)
                except Exception:
                    # 如果 Ibis insert 失败，回退到 SQLAlchemy
                    if hasattr(backend, 'con'):
                        engine = backend.con
                        data.to_sql(
                            table_name,
                            engine,
                            if_exists=if_exists,
                            index=False,
                            chunksize=1000
                        )
                    else:
                        raise
            else:
                # 使用 SQLAlchemy 引擎（兼容性方案）
                if hasattr(backend, 'con'):
                    engine = backend.con
                    data.to_sql(
                        table_name,
                        engine,
                        if_exists=if_exists,
                        index=False,
                        chunksize=1000
                    )
                else:
                    raise NotImplementedError(
                        f"Insert not supported for {self.db_type} backend"
                    )
            
            logger.info(f"Data inserted to {table_name}, rows: {len(data)}, if_exists: {if_exists}")
            return len(data)
            
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            raise
    
    def write_table(self, data: pd.DataFrame, table_name: str, 
                   if_exists: Literal['fail', 'replace', 'append'] = 'append') -> int:
        """写入数据到表（别名方法）
        
        Args:
            data: DataFrame 数据
            table_name: 目标表名
            if_exists: 表存在时的处理方式 ('fail', 'replace', 'append')
            
        Returns:
            写入的行数
        """
        return self.execute_insert(table_name, data, if_exists=if_exists)
    
    def execute_sql(self, sql: str, params: dict[str, Any] | None = None) -> int:
        """执行 SQL 语句（INSERT/UPDATE/DELETE）
        
        Args:
            sql: SQL 语句
            params: SQL 参数字典
            
        Returns:
            影响的行数（Ibis 可能不支持返回影响行数）
        """
        try:
            backend = self.get_backend()

            # 参数替换
            if params:
                for key, value in params.items():
                    sql = sql.replace(f":{key}", repr(value))
            
            if self.db_type == 'spark':
                spark_session = self._get_or_create_spark_session()
                result_df = spark_session.sql(sql)
                rows = result_df.collect()
                affected_rows = len(rows)
                logger.info(
                    "Spark SQL executed successfully, affected rows (approx): %s",
                    affected_rows,
                )
                return affected_rows
            
            # 执行 SQL
            if hasattr(backend, 'raw_sql'):
                result = backend.raw_sql(sql)
            else:
                # 使用底层连接执行
                if hasattr(backend, 'con'):
                    with backend.con.connect() as conn:
                        result = conn.execute(sql)
                        conn.commit()
                        affected_rows = result.rowcount if hasattr(result, 'rowcount') else 0
                        logger.info(f"SQL executed successfully, affected rows: {affected_rows}")
                        return affected_rows
                else:
                    backend.sql(sql).execute()
                    logger.info("SQL executed successfully")
                    return 0
            
            return 0
            
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            raise
    
    def create_table(self, table_name: str, schema: dict[str, str], 
                    overwrite: bool = False) -> None:
        """创建表
        
        Args:
            table_name: 表名
            schema: 表结构字典 {'column_name': 'column_type'}
            overwrite: 是否覆盖已存在的表
        """
        backend = self.get_backend()
        
        if overwrite and table_name in backend.list_tables():
            backend.drop_table(table_name)
        
        # 使用 Ibis 创建表（根据后端支持情况）
        # 这里简化处理，实际使用时可能需要更复杂的逻辑
        logger.info(f"Table creation: {table_name}")
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self._backend:
            # Ibis 某些后端支持 disconnect
            if hasattr(self._backend, 'disconnect'):
                self._backend.disconnect()
            self._backend = None
            logger.info("Ibis backend closed")

        if self._spark_session:
            try:
                self._spark_session.stop()
                logger.info("Spark session stopped")
            except Exception as exc:  # pragma: no cover - 取决于 Spark 环境
                logger.warning("Failed to stop Spark session: %s", exc)
            finally:
                self._spark_session = None
