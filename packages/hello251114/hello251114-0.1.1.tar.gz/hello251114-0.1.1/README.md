# hello251114

A simple hello world package for PyPI demonstration.

## Installation

```bash
pip install hello251114
```

## Usage

```bash
hello251114
```

Or in Python:

```python
from hello251114 import greet

print(greet())
```

## License

MIT

class PostgresHelper:

    def __init__(self):
        self.db_connection_string = f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PWD}@{config.POSTGRES_HOST}:{config.POSTGRES_POST}/{config.POSTGRES_DB}"
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None

    def initialize(self):
        """初始化数据库连接"""
        try:
            self.engine = create_engine(
                self.db_connection_string,
                echo=True  # 设置为True可以查看生成的SQL
            )
            self.session_factory = sessionmaker(bind=self.engine)
            logger.info("数据库连接初始化完成")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise