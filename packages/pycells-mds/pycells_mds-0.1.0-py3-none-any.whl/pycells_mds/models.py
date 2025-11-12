from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean,
    ForeignKey, DateTime, func, UniqueConstraint, event, JSON
)
from sqlalchemy.orm import relationship, sessionmaker, Session
from datetime import datetime, timezone
from .base import Base
import re





# ========================== MODELS ===========================

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tables = relationship("TableModel", back_populates="author", cascade="all, delete")




class ListModel(Base):
    __tablename__ = "pycells_lists"
    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey("pycells_tables.id", ondelete="CASCADE"))
    name = Column(String(50))
    password = Column(String(255), nullable=True)
    style = Column(Text, nullable=True, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    table = relationship("TableModel", back_populates="lists", foreign_keys=[table_id])
    cells = relationship("CellModel", back_populates="list", cascade="all, delete")

    __table_args__ = (UniqueConstraint("table_id", "name", name="_list_name_uc"),)



    def get_dependencies(self):
        """Возвращает словарь зависимостей: {имя_ячейки: [ячейки_от_которых_зависит]}"""
        deps = {}
        for cell in self.cells:
            if cell.data and isinstance(cell.data, str) and cell.data.startswith('='):
                refs = re.findall(r'\b[A-Z]+\d+\b', cell.data)  # находит ссылки типа A1, B2
                deps[cell.name] = refs
        return deps

    def recalc_cell(self, cell_name, visited=None, deps=None, cell_map=None):
        """
        Рекурсивный пересчёт ячейки и всех зависимых от неё.
        Оптимизировано: 
        - зависимости вычисляются один раз,
        - быстрый доступ к ячейкам через словарь.
        """
        if visited is None:
            visited = set()
        if deps is None:
            deps = self.get_dependencies()
        if cell_map is None:
            cell_map = {c.name: c for c in self.cells}

        if cell_name in visited:
            # Можно добавить лог или исключение для циклов
            # print(f"Цикл обнаружен: {cell_name}")
            return

        visited.add(cell_name)

        cell = cell_map.get(cell_name)
        if not cell or not cell.data:
            return

        # вычисляем значение
        try:
            value = self.read(cell.name).evaluate()
            cell.data = value
        except Exception:
            pass

        # пересчитываем зависимые
        for dep_name, refs in deps.items():
            if cell_name in refs:
                self.recalc_cell(dep_name, visited, deps, cell_map)









class TableModel(Base):
    __tablename__ = "pycells_tables"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    password = Column(String(255), nullable=True)
    style = Column(Text, nullable=True, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    visible_name_in_search = Column(Boolean, default=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("UserModel", back_populates="tables")

    # Ссылка на активный лист
    active_list_id = Column(Integer, ForeignKey("pycells_lists.id", ondelete="SET NULL"), nullable=True)
    active_list = relationship("ListModel", foreign_keys=[active_list_id])


    __table_args__ = (
        UniqueConstraint('author_id', 'name', name='uix_user_table_name'),
    )


    # Все листы таблицы
    lists = relationship(
        "ListModel",
        back_populates="table",
        cascade="all, delete-orphan",
        passive_deletes=True,  # отключает активное удаление объектов при каскаде
        foreign_keys=[ListModel.table_id]
    )




class CellModel(Base):
    __tablename__ = "pycells_cells"

    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey("pycells_tables.id"))
    list_id = Column(Integer, ForeignKey("pycells_lists.id"))
    cell_id = Column(String(255), nullable=True, unique=True)
    name = Column(String(50))
    data = Column(Text, nullable=True)
    style = Column(Text, nullable=True, default="")
    note = Column(Text, nullable=True)
    group_id = Column(Integer, ForeignKey("pyt_tab_groups.id"), nullable=True)

    #group = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    list = relationship("ListModel", back_populates="cells")

    __table_args__ = (UniqueConstraint("list_id", "name", name="_cell_name_uc"),)

    @classmethod
    def id_show(cls, session: Session, name: str, list_id: int = None, table_id: int = None):
        """Возвращает cell_id ячейки по имени, учитывая лист и таблицу"""
        query = session.query(cls).filter_by(name=name)
        if list_id is not None:
            query = query.filter_by(list_id=list_id)
        if table_id is not None:
            query = query.join(ListModel).filter(ListModel.table_id == table_id)

        cell = query.first()
        if not cell:
            return f"[Ошибка] Ячейка '{name}' не найдена"
        return cell.cell_id or f"[Нет cell_id для {name}]"

    

    @classmethod
    def build_structure(cls, session: Session, list_id: int, sheet=None):
        """Строит иерархию всех непустых ячеек строго по cell_id из базы."""
        cells = session.query(cls).filter(
            cls.list_id == list_id,
            cls.data.isnot(None),
            cls.data != ""
        ).all()

        structure = {}

        for cell in cells:
            parts = cell.cell_id.split(".")
            level = structure
            for part in parts[:-1]:
                level = level.setdefault(part, {})

            last_key = parts[-1]

            # Всегда берём значение из базы, sheet.read() не используем для ключей
            value = cell.data

            level[last_key] = {
                "name": cell.name,
                "cell_id": cell.cell_id,
                "data": value,
                "style": cell.style,
                "note": cell.note,
            }

        return structure
    


    @classmethod
    def evaluate_structure(cls, structure, session, list_id):
        from pycells_mds.core import CellWrapper
        results = {}

        def recurse(level):
            for key, val in level.items():
                if isinstance(val, dict) and "cell_id" in val:
                    # Найти ячейку в БД
                    cell = session.query(cls).filter_by(list_id=list_id, name=val["name"]).first()
                    if cell:
                        wrap = CellWrapper(session, None, cell)  # sheet/list можно None
                        results[val["cell_id"]] = wrap.evaluate()
                elif isinstance(val, dict):
                    recurse(val)

        recurse(structure)
        return results




@event.listens_for(CellModel, "after_insert")
def generate_cell_id_after_insert(mapper, connection, target):
    if target.cell_id:  # если передан вручную, ничего не делаем
        return
    session = Session.object_session(target)
    list_obj = session.query(ListModel).filter_by(id=target.list_id).first()
    table_obj = session.query(TableModel).filter_by(id=list_obj.table_id).first()
    new_cell_id = f"{table_obj.name}.{list_obj.name}.{target.id:02d}.00.1"
    connection.execute(
        CellModel.__table__.update()
        .where(CellModel.id == target.id)
        .values(cell_id=new_cell_id)
    )


@event.listens_for(CellModel, "before_update")
def regenerate_cell_id(mapper, connection, target):
    if target.cell_id and not target.cell_id.startswith("DemoTable"):  # или другой фильтр
        return  # пропускаем, если cell_id задан вручную
    session = Session.object_session(target)
    list_obj = session.query(ListModel).filter_by(id=target.list_id).first()
    table_obj = session.query(TableModel).filter_by(id=list_obj.table_id).first()
    target.cell_id = f"{table_obj.name}.{list_obj.name}.{target.id:02d}.00.1"







class GroupModel(Base):
    __tablename__ = "pyt_tab_groups"
    id = Column(Integer, primary_key=True)
    list_id = Column(Integer, ForeignKey("pycells_lists.id"))
    name = Column(String(50))
    style = Column(Text, default="")
    datetime = Column(DateTime, default=datetime.now(timezone.utc))
    
    list = relationship("ListModel", backref="groups", lazy="dynamic")
    cells = relationship("CellModel", backref="group", lazy="dynamic")  # <-- это нужно для list_api.update_group_style






class CursorModel(Base):
    __tablename__ = "pyttabs_cursors"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    table_id = Column(Integer, ForeignKey("pycells_tables.id"))
    list_id = Column(Integer, ForeignKey("pycells_lists.id"))
    cells = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    table = relationship("TableModel")
    list = relationship("ListModel")


