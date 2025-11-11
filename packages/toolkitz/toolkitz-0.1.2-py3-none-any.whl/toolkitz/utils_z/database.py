
from sqlalchemy import Column, Integer, String, Text, DateTime, text, UniqueConstraint, Boolean, func, Float, Double
from sqlalchemy.orm import declarative_base

PromptBase = declarative_base()


class UseCase(PromptBase):
    __tablename__ = 'ai_usecase' # 数据库中的表名，你可以改成你希望的名字

    __table_args__ = (
            UniqueConstraint('time',name='time_double_uc'),
            # 'name' 参数是可选的，用于给数据库中的约束指定一个名称，方便管理和调试
        )
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True, # 自动递增
        nullable=False,     # 不能为空
        comment="Primary key ID"
    )

    level = Column(
        String(255),        # VARCHAR 类型，长度 255
        nullable=False,     # 不能为空    # 必须是唯一的，这会创建唯一索引
        comment="level"
    )
    time = Column(
        Double,
        nullable=False,      # 不能为空
        comment="时间戳"
    )

    timestamp = Column(
        DateTime,
        nullable=False,      # 不能为空
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=text('CURRENT_TIMESTAMP'),
        comment="时间戳"
    )

    filepath = Column(
        String(255),             # TEXT 类型，适用于长文本
        nullable=False,     # 不能为空
        comment="文件路径"
    )


    function = Column(
        String(255),             # TEXT 类型，适用于长文本
        nullable=False,     # 不能为空
        comment="函数"
    )

    lines = Column(
        String(255),             # TEXT 类型，适用于长文本
        nullable=False,     # 不能为空
        comment="函数"
    )
    input_data = Column(
        Text,      # TEXT 类型，适用于长文本
        nullable=False,     # 不能为空
        comment="输入"
    )

    output_data = Column(
        Text,               # TEXT 类型，适用于长文本
        nullable=False,     # 不能为空
        comment="输出"
    )

    is_deleted = Column(Boolean, default=False, server_default=text('0')) 

    # 定义 __repr__ 方法以便打印对象时有清晰的表示
    def __repr__(self):
        return (f"<UseCase(id={self.id},"
                f"function='{self.function}...', input_data='{self.input_data}')>"
                f"output_data='{self.output_data}...'>")

