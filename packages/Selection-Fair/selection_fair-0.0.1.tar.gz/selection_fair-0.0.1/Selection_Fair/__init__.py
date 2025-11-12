# WeComMsg/__init__.py

# 从核心代码文件中导入需要对外暴露的类/函数
from .Selection_Fair import TableProcessor

# 可选：明确指定包对外暴露的成员（规范导入）
__all__ = ["TableProcessor", "__version__"]