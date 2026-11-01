import re
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import BIGINT, Column, DateTime, Integer, String, func, inspect
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseTableModel(Base):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "__tablename__") or cls.__tablename__ is None:
            # 将类名转为下划线分隔的小写
            name = cls.__name__
            # 将驼峰转为下划线
            table_name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
            cls.__tablename__ = table_name

    __abstract__ = True

    __operation__ = False

    id = Column(BIGINT, primary_key=True, autoincrement=True, nullable=False, comment="主键ID")
    is_deleted = Column(Integer, nullable=False, default=0, index=True, comment="是否删除 0:否 1:是")
    create_time = Column(
        DateTime,
        default=func.now(),
        comment="创建时间"
    )
    update_time = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )
    operator = Column(String(32), nullable=True, comment="操作人")

    def to_dict(self, exclude: list[str] | None = None, extra: dict | None = None):

        state = inspect(self)

        # 未加载字段（访问会触发SQL）
        unloaded = state.unloaded
    
        default_exclude = {"is_deleted"}
        if exclude:
            default_exclude.update(exclude)
    
        result = {}
    
        for column in state.mapper.column_attrs:
            key = column.key
    
            # 排除字段
            if key in default_exclude:
                continue
            
            # 避免触发懒加载
            if key in unloaded:
                continue
            
            value = getattr(self, key)
    
            if isinstance(value, Enum):
                value = value.value
            elif isinstance(value, (date, datetime)):
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, Decimal):
                value = float(value)
    
            result[key] = value
    
        if extra:
            result.update(extra)
    
        return result

    # def __getitem__(self, key):
    #     return getattr(self, key)
    #
    # def __setitem__(self, key, value):
    #     return setattr(self, key, value)