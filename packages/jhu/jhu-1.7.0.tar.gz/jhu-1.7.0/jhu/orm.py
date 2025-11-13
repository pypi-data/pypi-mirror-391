from datetime import datetime
from dataclasses import dataclass
from math import ceil
from typing import Callable, Any
from urllib.parse import quote_plus
from sqlalchemy import func, select, Select, MappingResult, text
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import BinaryExpression
from pytz import timezone


@dataclass
class ORMCheckRule:
    """规则检验"""
    errcode: Any
    condition: BinaryExpression


@dataclass
class ORMFormatRule:
    """格式化"""
    filed: str
    format: Callable


def format_datetime(dt: datetime) -> str:
    """格式化日期"""
    utc_dt = timezone("UTC").localize(dt)
    shanghai_zone = timezone("Asia/Shanghai")
    target_dt = utc_dt.astimezone(shanghai_zone)

    return target_dt.strftime("%Y-%m-%d %H:%M:%S")


def format_filed(data: dict, rules: list[ORMFormatRule] = []) -> dict:
    """格式化读取的字段"""
    basic_rules = [
        ORMFormatRule("created_at", format_datetime),
        ORMFormatRule("updated_at", format_datetime),
    ]

    basic_rules.extend(rules)

    for obj in basic_rules:
        if filed := data.get(obj.filed, None):
            data[obj.filed] = obj.format(filed)

    return data


class ORM:
    @staticmethod
    def build_engine_url(dialect_dbapi: str, host: str, port: str, username: str = "", passwd: str = "", database: str = "", **kw) -> str:
        """创建sqlalchemy的engine url

        Args:
            dialect_dbapi:数据库方言和数据库API,比如'mysql+pymysql','postgresql'
            host:主机地址
            port:端口号
            username:用户名
            passwd:密码
            database:数据库名
            **kw:数据库的参数

        Return:
            str: 返回格式为:dialect+dbapi://username:passwd@host:port/database?key=value&key=value
        """
        # 拼接用户名以及密码
        username, passwd = map(quote_plus, [username, passwd])
        auth_info = f"{username}:{passwd}" if passwd else username

        # 设置数据库信息
        database = f"/{database}" if database else ""

        # 设置参数信息
        if kw:
            args = '&'.join([f"{k}={kw[k]}" for k in kw])
            param = f"?{args}"
        else:
            param = ""

        # 拼接url
        url = f"{dialect_dbapi}://{auth_info}@{host}:{port}{database}{param}"
        return url

    @staticmethod
    def mapping(session: Session, stmt) -> MappingResult:
        """ORM执行结果mapping"""
        return session.execute(stmt).mappings()

    @staticmethod
    def all(session: Session, stmt: Select, format_rules: list[ORMFormatRule] = []) -> list[dict]:
        """获取所有数据"""
        ds = ORM.mapping(session, stmt)
        result = [format_filed(dict(**one), format_rules) for one in ds]
        return result

    @staticmethod
    def one(session: Session, stmt: Select, format_rules: list[ORMFormatRule] = []) -> dict | None:
        """获取第一行数据"""
        try:
            one = next(ORM.mapping(session, stmt))
            data = format_filed(dict(**one), format_rules)
        except StopIteration:
            return None

        return data

    @staticmethod
    def counts(session: Session, stmt: Select) -> int:
        """获取数据量
        """
        # return session.scalar(stmt)
        # select语句中如果带有group by字段,那么with_only_columns会导致总数计算不正确
        filed_temp = func.count(text("1"))
        if (result := session.scalar(stmt.with_only_columns(filed_temp))) is None:
            result = 0
        return result

    @staticmethod
    def pagination(session: Session, stmt: Select, page_idx: int = 1, page_size: int = 10, order: list | None = None, format_rules: list[ORMFormatRule] = []) -> dict:
        """分页查询数据
        """
        if page_size < 1:
            page_size = 1

        match(page_idx):
            case page_idx if page_idx > 0:
                offset = (page_idx - 1) * page_size
            case _:
                offset = 0
                page_idx = 1

        total = ORM.counts(session, stmt)
        page_total = ceil(total / page_size)
        pagination = {"page_idx": page_idx, "page_size": page_size,
                      "page_total": page_total, "total": total}
        data = {"records": [], "pagination": pagination}

        # 如果总数为零,不需要继续执行查询
        if total == 0:
            return data

        # 配置排序条件
        if order is not None:
            stmt = stmt.order_by(*order)

        # 配置分页条件
        stmt = stmt.offset(offset).limit(page_size)
        data["records"] = ORM.all(session, stmt, format_rules)

        return data

    @staticmethod
    def check(session: Session, rules: list[ORMCheckRule], except_expression: BinaryExpression | None = None) -> str | int | None:
        """规则判断

        Args:
            session: 数据库会话
            rules: 检测规则
            expression: 例外表达式(比如,修改的时候不判断本条数据)

        Return:
            None:检测通过
            str | int:检测未通过,异常代码
        """
        base_stmt = select(1)

        if except_expression is not None:
            base_stmt = base_stmt.where(except_expression)

        for rule in rules:
            stmt = base_stmt.where(rule.condition)
            if ORM.counts(session, stmt) > 0:
                return rule.errcode
