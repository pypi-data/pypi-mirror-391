# Warehouse Core 项目指南

## 📦 项目简介

基于 Ibis 的数据处理核心库，提供统一的数据库连接与数据处理能力。支持 SQLite、MySQL、Spark 等多种数据后端。

## 🚀 快速开始

### 环境要求
- Python 3.11+

### 一键设置
```bash
# 克隆项目后进入目录
cd data-business-warehouse

# 完整项目设置（检查环境+安装依赖+验证）
make setup
```

## 📚 项目结构

```
warehouse-core/
├── Makefile              # 项目管理命令
├── pyproject.toml        # Poetry 配置
├── warehouse_core/       # 核心库代码
│   ├── db/              # 数据库连接与管理
│   ├── engine/          # 作业基类与调度器
│   └── utils/           # 日志等工具
├── examples/             # 示例代码
├── test/                # 测试验证代码
├── config/              # 配置文件
└── data/                # 数据文件
```

## 💻 使用示例

### 1. 数据库连接管理
```python
from warehouse_core.db import DatabaseManager

manager = DatabaseManager()
connection = manager.get_sqlalchemy_connection("sqlite_default")
rows = connection.execute_query("SELECT 1")
```

### 2. 数据处理作业
```python
from warehouse_core.engine import JobBase

class ExampleJob(JobBase):
    def process(self) -> None:
        dataframe = self.query_to_dataframe("SELECT * FROM source_table")
        self.insert("target_table", dataframe)
```

## 🔧 项目管理

### Makefile 命令（推荐）
```bash
# 完整项目设置
make setup

# 安装依赖
make install

# 验证项目功能
make verify

# 运行示例作业
make test

# 初始化数据库
make init

# 清理临时文件
make clean

# 激活虚拟环境
make shell

# 查看所有命令
make help
```

### Poetry 命令
```bash
# 添加依赖
poetry add package-name

# 更新依赖
poetry update

# 查看依赖树
poetry show --tree
```

## 🌐 镜像源配置

项目已配置阿里云镜像源以加速下载：
```bash
https://mirrors.aliyun.com/pypi/simple/
```

### 验证配置
```bash
poetry source show
poetry config --list
```

### 恢复官方源
```bash
poetry config repositories.main https://pypi.org/simple/
```

## 🐳 Docker 部署

### Dockerfile 示例
```dockerfile
FROM python:3.11-slim

# 安装 Poetry
RUN pip install poetry

WORKDIR /app

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 安装依赖
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# 复制项目文件
COPY . .

CMD ["poetry", "run", "python", "your_main.py"]
```

## 📦 依赖配置

### 核心依赖
- **pandas** - 数据处理
- **sqlalchemy** - 数据库抽象层
- **pyyaml** - YAML 配置解析
- **ibis-framework** - 数据分析框架（支持 sqlite、mysql、pyspark）

### 数据库支持
- **SQLite** - 默认支持，轻量级本地数据库
- **MySQL** - 通过 ibis-framework[mysql] 支持
- **Spark** - 通过 ibis-framework[pyspark] 支持

## 📄 打包发布

```bash
# 构建包
poetry build

# 发布到 PyPI
poetry publish --username __token__ --password <pypi-token>
```

## ⚠️ 注意事项

1. **虚拟环境位置**：默认在 `~/.cache/pypoetry/virtualenvs/`
2. **自定义位置**：`poetry config virtualenvs.in-project true`（创建 .venv）
3. **首次安装**：需要 2-5 分钟解析依赖
4. **版本控制**：建议提交 `poetry.lock` 文件

## 🤝 开发工作流

### VS Code 开发环境
项目已配置完整的 VS Code 开发环境：

**调试配置**（.vscode/launch.json）：
- 调试项目验证
- 调试简单作业示例  
- 调试数据库初始化
- 调试当前文件

**任务配置**（.vscode/tasks.json）：
- 项目设置（Ctrl+Shift+P → Tasks: Run Task）
- 安装依赖、验证项目、运行示例等

**推荐扩展**：
- Python、Black、isort、YAML、Makefile Tools

### 示例配置
库中 `examples/` 目录提供：
- SQLite 初始化脚本
- 示例 `db_config.yaml`
- 可作为业务工程的参考模板

### 验证测试
```bash
# 运行完整验证
make verify

# 运行示例测试
make test
```

### Git 提交建议
```bash
git add poetry.lock pyproject.toml
git commit -m "chore: 更新依赖版本"
```

---

**License**: MIT  
**Python 版本**: ^3.11  
**主要依赖**: pandas, sqlalchemy, pyyaml, ibis-framework