# managers/table_manager.py

from .session import db
from .models import TableModel, ListModel, CursorModel
from .wrappers import ListWrapper

from datetime import datetime, timezone
import json
import redis


r = redis.Redis(host="localhost", port=6379, db=0)




class TableManager:
    """
    Менеджер таблицы — управление листами,
    активными листами и базовыми операциями.
    """

    def __init__(self, table_model: TableModel):
        self.table_model = table_model
        self.session = db.session

    # ---------------------------------------------
    # СОЗДАНИЕ / ПОЛУЧЕНИЕ ЛИСТОВ
    # ---------------------------------------------

    def create_list(self, name: str):
        """Возвращает существующий лист или создаёт новый."""
        lst = (
            self.session.query(ListModel)
            .filter_by(table_id=self.table_model.id, name=name)
            .first()
        )

        if not lst:
            lst = ListModel(table_id=self.table_model.id, name=name)
            self.session.add(lst)
            self.session.commit()

        # назначаем активный лист
        if self.table_model.active_list_id != lst.id:
            self.table_model.active_list_id = lst.id
            self.session.commit()

        return ListWrapper(lst)

    def lists(self):
        lst_models = (
            self.session.query(ListModel)
            .filter_by(table_id=self.table_model.id)
            .all()
        )
        return [ListWrapper(lst) for lst in lst_models]

    def get_list_by_id(self, list_id: int):
        lst = (
            self.session.query(ListModel)
            .filter_by(id=list_id, table_id=self.table_model.id)
            .first()
        )
        return ListWrapper(lst) if lst else None

    # ---------------------------------------------
    # АКТИВНЫЙ ЛИСТ
    # ---------------------------------------------

    def get_active_list(self):
        if not self.table_model.active_list_id:
            return None

        lst = self.session.query(ListModel).get(self.table_model.active_list_id)
        return ListWrapper(lst) if lst else None

    def set_active_list(self, name: str):
        lst = (
            self.session.query(ListModel)
            .filter_by(table_id=self.table_model.id, name=name)
            .first()
        )
        if not lst:
            return None

        self.table_model.active_list_id = lst.id
        self.session.commit()
        return ListWrapper(lst)







class CursorManager:
    """Гибридный менеджер курсора — Redis (текущее состояние) + SQL (история)."""

    @staticmethod
    def _redis_key(user_id):         return f"cursor:{user_id}"
    @staticmethod
    def _prec_redis_key(user_id):    return f"prec_cursor:{user_id}"

    # ---------------------------------------------------------
    # УСТАНОВКА КУРСОРА
    # ---------------------------------------------------------

    @classmethod
    def set_cursor(cls, user_id: int, table_id: int, list_id: int, cells: list[str]):
        """Сохраняет текущий cursor → prec_cursor, затем активирует новый."""
        current = cls.get_active(user_id)
        if current:
            r.set(cls._prec_redis_key(user_id), json.dumps(current))

        return cls.activate(user_id, table_id, list_id, cells)

    # ---------------------------------------------------------
    # АКТИВАЦИЯ (Redis + SQL)
    # ---------------------------------------------------------

    @classmethod
    def activate(cls, user_id: int, table_id: int, list_id: int, cells: list[str]):
        now = datetime.now(timezone.utc)

        data = {
            "user_id": user_id,
            "table_id": table_id,
            "list_id": list_id,
            "cells": cells,
            "timestamp": now.isoformat()
        }

        # Текущее состояние — Redis
        r.set(cls._redis_key(user_id), json.dumps(data))

        # История — SQL
        cursor = CursorModel(
            user_id=user_id,
            table_id=table_id,
            list_id=list_id,
            cells=cells,
            created_at=now
        )

        db.session.add(cursor)
        db.session.commit()

        return data

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ КУРСОРОВ
    # ---------------------------------------------------------

    @classmethod
    def get_active(cls, user_id: int):
        raw = r.get(cls._redis_key(user_id))
        return json.loads(raw) if raw else None

    @classmethod
    def get_prec_cursor(cls, user_id: int):
        raw = r.get(cls._prec_redis_key(user_id))
        return json.loads(raw) if raw else None

    @classmethod
    def get_previous(cls, user_id: int):
        """Предыдущий курсор из БД."""
        cursors = (
            db.session.query(CursorModel)
            .filter(CursorModel.user_id == user_id)
            .order_by(CursorModel.id.desc())
            .limit(2)
            .all()
        )
        return cursors[1] if len(cursors) == 2 else None

    # ---------------------------------------------------------
    # ОЧИСТКА (Redis + SQL)
    # ---------------------------------------------------------

    @classmethod
    def clear(cls, user_id: int):
        r.delete(cls._redis_key(user_id))
        r.delete(cls._prec_redis_key(user_id))

        db.session.query(CursorModel).filter_by(user_id=user_id).delete()
        db.session.commit()



