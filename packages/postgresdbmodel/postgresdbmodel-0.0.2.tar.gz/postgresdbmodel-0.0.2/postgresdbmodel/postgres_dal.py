from sqlalchemy import select, insert, update, delete
from sqlalchemy.sql import Select
from sqlalchemy.engine import Connection
from typing import Any
from pydbinterface import DBInterface
import datetime
from .sqlalchemy_data_mapper import DataMapper

class PostgresDAL(DBInterface):
    def __init__(self, mapper: DataMapper, connection: Connection):
        self.mapper = mapper
        self.connection = connection
        self._transaction = None
    def _build_statement(self, base_stmt, where):
        if where is None:
            return base_stmt
        elif isinstance(where, Select):
            return where
        elif isinstance(where, dict):
            stmt = base_stmt
            for k, v in where.items():
                stmt = stmt.where(self.mapper.table.c[k] == v)
            return stmt
        else:
            raise TypeError("The 'where' parameter must be a dict or SQLAlchemy Select")

    def create(self, data: Any) -> Any:
        if not isinstance(data, dict):
            raise TypeError("The 'data' parameter must be a dict")
        data = self.mapper.dict_to_row(data)
        if 'created_at' in self.mapper.table.c:
            data['created_at'] = datetime.datetime.now(datetime.timezone.utc)
        stmt = insert(self.mapper.table).values(**data).returning(self.mapper.table)
        result = self.connection.execute(stmt)
        if not self._transaction:
            self.commit_transaction()
        return dict(result.fetchone()._mapping)

    def read(self, where: Any) -> Any:
        base_stmt = select(self.mapper.table)
        stmt = self._build_statement(base_stmt, where)
        result = self.connection.execute(stmt)
        if not self._transaction:
            self.commit_transaction()
        return [dict(row._mapping) for row in result.fetchall()]

    def update(self, where: Any, data: Any) -> Any:
        if not isinstance(data, dict):
            raise TypeError("The 'data' parameter must be a dict")
        data = self.mapper.dict_to_row(data)
        if 'updated_at' in self.mapper.table.c:
            data['updated_at'] = datetime.datetime.now(datetime.timezone.utc)
        base_stmt = update(self.mapper.table).values(**data).returning(self.mapper.table)
        stmt = self._build_statement(base_stmt, where)
        result = self.connection.execute(stmt)
        if not self._transaction:
            self.commit_transaction()
        return [dict(row._mapping) for row in result.fetchall()]

    def delete(self, where: Any) -> Any:
        base_stmt = delete(self.mapper.table).returning(self.mapper.table)
        stmt = self._build_statement(base_stmt, where)
        result = self.connection.execute(stmt)
        if not self._transaction:
            self.commit_transaction()
        return [dict(row._mapping) for row in result.fetchall()]

    def begin_transaction(self):
        if hasattr(self.connection, 'begin'):
            self._transaction = self.connection.begin()
        else:
            raise NotImplementedError("The connection does not support explicit transactions.")

    def commit_transaction(self):
        if self._transaction:
            self._transaction.commit()
            self._transaction = None
        else:
            self.connection.commit()

    def rollback_transaction(self):
        if self._transaction:
            self._transaction.rollback()
            self._transaction = None
        else:
            self.connection.rollback()
