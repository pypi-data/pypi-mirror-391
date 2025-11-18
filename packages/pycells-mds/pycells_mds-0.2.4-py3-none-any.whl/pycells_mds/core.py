# pycells.py

from .session import db
from .models import TableModel, ListModel
from pycells_mds.wrappers import TableWrapper
from pycells_mds.wrappers import ListWrapper
from pycells_mds.wrappers import CellWrapper
from pycells_mds.users import (
    register_user,
    login_user,
    safe_register_user
)





class PyCells:
    """
    Глобальный фасад для работы с PyCells.
    Пользователь видит только этот класс.
    """


    # =========================================================
    # USER API (PUBLIC)
    # =========================================================

    def register_user(self, username: str, password: str, email: str | None = None):
        """Регистрация нового пользователя."""
        return register_user(username, password, email)

    def login(self, username: str, password: str) -> int | None:
        """Возвращает user_id при успешной авторизации."""
        return login_user(username, password)

    def safe_register_user(self, username: str, password: str, email: str | None = None):
        """Регистрация только если нет такого пользователя."""
        return safe_register_user(username, password, email)




    # ---------------------------------------------------------
    # TABLE OPERATIONS
    # ---------------------------------------------------------

    def ctable(self, name: str, user_id: int) -> TableWrapper:
        """
        Возвращает существующую таблицу пользователю
        или создаёт её, если не существует.
        """
        table = (
            db.session.query(TableModel)
            .filter_by(name=name, author_id=user_id)
            .first()
        )

        if not table:
            table = TableModel(name=name, author_id=user_id)
            db.session.add(table)
            db.session.commit()

        return TableWrapper(table)

    def get_table(self, name: str, user_id: int) -> TableWrapper | None:
        """Получить таблицу без создания."""
        table = (
            db.session.query(TableModel)
            .filter_by(name=name, author_id=user_id)
            .first()
        )
        return TableWrapper(table) if table else None

    # ---------------------------------------------------------
    # LIST OPERATIONS
    # ---------------------------------------------------------

    def get_list(self, table_name: str, list_name: str, user_id: int) -> ListWrapper | None:
        """Получить лист по таблице и имени."""
        tbl = self.get_table(table_name, user_id)
        if not tbl:
            return None

        lst = (
            db.session.query(ListModel)
            .filter_by(table_id=tbl.table_model.id, name=list_name)
            .first()
        )
        return ListWrapper(lst) if lst else None

    def get_or_create_list(self, table_name: str, list_name: str, user_id: int) -> ListWrapper:
        """Гарантированно вернуть лист."""
        tbl = self.ctable(table_name, user_id)
        return tbl.create_list(list_name)

    # ---------------------------------------------------------
    # CELL OPERATIONS (WRITE, READ, SELECT)
    # ---------------------------------------------------------

    def write(self, table: str, sheet: str, cell: str, value: str, user_id: int):
        """
        Универсальная запись:
            pc.write("Finance", "Main", "A1", "=5+10", user_id)
        """
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.write(cell, value)

    def read(self, table: str, sheet: str, cell: str, user_id: int):
        """
        Универсальное чтение:
            pc.read("Finance", "Main", "A1", user_id)
        """
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.read(cell)

    def select(self, table: str, sheet: str, *cells, user_id: int):
        """
        Вернуть набор ячеек:
            pc.select("Finance", "Main", "A1", "B2", "C3", user_id=user_id)
        """
        lst = self.get_or_create_list(table, sheet, user_id)
        return {name: lst.read(name) for name in cells}

    # ---------------------------------------------------------
    # RE-CALC
    # ---------------------------------------------------------

    def recalc(self, table: str, sheet: str, user_id: int):
        """Пересчитать все ячейки листа."""
        lst = self.get_or_create_list(table, sheet, user_id)
        lst.recalc_all()
        return True
    


    # GROUP OPERATIONS
# ----------------------------------------------------------

    def create_group(self, table: str, sheet: str, name: str, cells: list[str], user_id: int, style: str = ""):
        """Создаёт группу на листе."""
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.add_group(name, cells, style)

    def update_group_style(self, table: str, sheet: str, name: str, style: str, user_id: int):
        """Обновляет стиль существующей группы."""
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.update_group_style(name, style)

    def get_group_cells(self, table: str, sheet: str, name: str, user_id: int):
        """Возвращает список ORM-ячееек, которые входят в группу."""
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.get_group_cells(name)

    def delete_group(self, table: str, sheet: str, name: str, user_id: int):
        """Удаляет группу и очищает group_id у ячеек."""
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.delete_group(name)
    


    # Notes and Style
# ----------------------------------------------------------

    def set_style(self, table, sheet, cell, style, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.set_style(cell, style)

    def get_style(self, table, sheet, cell, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.get_style(cell)

    def set_note(self, table, sheet, cell, note, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.set_note(cell, note)

    def get_note(self, table, sheet, cell, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.get_note(cell)

    def clear_style(self, table, sheet, cell, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.clear_style(cell)

    def clear_note(self, table, sheet, cell, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.clear_note(cell)
    

    def set_group_style(self, name, style):
        group = self.get_group(name)
        if not group:
            return None
        group.style = style
        db.session.commit()
        return group
    

    def update_group_style(self, table, sheet, group, style, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.update_group_style(group, style)
    




