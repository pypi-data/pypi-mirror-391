from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .base import Base
from .models import TableModel, ListModel, CellModel, CursorModel, GroupModel
from .users import register_user, login_user
import datetime as dt
import json
import redis
import re
import numpy as np



def ETEXT(x, fmt: str = None):
    import re

    # --- Если строка с %, вычисляем как число ---
    if isinstance(x, str):
        x = x.strip()
        # Процент
        if x.endswith("%"):
            try:
                x = float(x[:-1]) / 100
            except:
                pass
        # Степень: "2^3"
        elif "^" in x:
            try:
                base, exp = x.split("^")
                x = float(base) ** float(exp)
            except:
                pass
        else:
            try:
                x = float(x)
            except:
                pass

    # --- Если число ---
    if isinstance(x, (int, float)):
        if fmt == "0":          
            return f"{int(round(x))}"
        elif fmt == "0.0":      
            return f"{x:.1f}"
        elif fmt == "0.00":     
            return f"{x:.2f}"
        elif fmt == "0%":       
            return f"{round(x*100)}%"
        elif fmt == "0.0%":     
            return f"{x*100:.1f}%"
        elif fmt == "#,##0":    
            return f"{int(round(x)):,}"
        else:
            try:                
                return format(x, fmt)
            except:
                return str(x)

    # --- Если дата ---
    elif isinstance(x, (dt.date, dt.datetime)):
        mapping = {
            "dd.mm.yyyy": "%d.%m.%Y",
            "dd/mm/yyyy": "%d/%m/%Y",
            "yyyy-mm-dd": "%Y-%m-%d",
            "yyyy/mm/dd": "%Y/%m/%d",
        }
        py_fmt = mapping.get(fmt.lower())
        if py_fmt:
            return x.strftime(py_fmt)
        else:
            return str(x)

    # --- Всё остальное ---
    else:
        return str(x)





GLOBAL_NS = {
    # --- Арифметика и агрегаты ---
    "SUM": lambda lst: np.sum(lst) if isinstance(lst, (list, np.ndarray)) else lst,
    "MAX": lambda lst: np.max(lst) if isinstance(lst, (list, np.ndarray)) else lst,
    "MIN": lambda lst: np.min(lst) if isinstance(lst, (list, np.ndarray)) else lst,
    "AVERAGE": lambda lst: np.mean(lst) if isinstance(lst, (list, np.ndarray)) else lst,

    # --- Математика ---
    "ABS": np.abs,
    "ROUND": np.round,
    "POWER": lambda a, b: np.power(a, b),
    "PERCENT": lambda x: x / 100,
    "INT": lambda x: int(float(x)) if str(x).replace('.', '', 1).lstrip('-').isdigit() else 0,
    "VALUE": lambda x: float(x) if str(x).replace('.', '', 1).lstrip('-').isdigit() else 0.0,

    # --- Логика ---
    "IF": lambda cond, a, b: a if cond else b,

    # --- Текстовые функции ---
    "CONCAT": lambda *args: "".join(str(a) for a in args if a is not None),
    "TEXTJOIN": lambda sep, *args: sep.join(str(a) for a in args if a is not None),
    "LEFT": lambda text, n=1: str(text)[:int(n)],
    "RIGHT": lambda text, n=1: str(text)[-int(n):],
    "LEN": lambda text: len(str(text)),
    "LOWER": lambda text: str(text).lower(),
    "UPPER": lambda text: str(text).upper(),
    "TRIM": lambda text: str(text).strip(),
    # --- TEXT: числа и даты с форматом ---
    "TEXT": lambda x, fmt=None: (
        x.strftime(fmt) if isinstance(x, (dt.date, dt.datetime)) and fmt else
        format(x, fmt) if fmt and isinstance(x, (int, float)) else
        str(x)
    ),
    # --- Excel--TEXT() ---
    "ETEXT": ETEXT,

    # --- Даты и время ---
    "TODAY": lambda: dt.date.today(),
    "NOW": lambda: dt.datetime.now(),
    "YEAR": lambda d: d.year if isinstance(d, (dt.date, dt.datetime)) else None,
    "MONTH": lambda d: d.month if isinstance(d, (dt.date, dt.datetime)) else None,
    "DAY": lambda d: d.day if isinstance(d, (dt.date, dt.datetime)) else None,
    "HOUR": lambda d: d.hour if isinstance(d, dt.datetime) else 0,
    "MINUTE": lambda d: d.minute if isinstance(d, dt.datetime) else 0,
    "SECOND": lambda d: d.second if isinstance(d, dt.datetime) else 0,
    "DATE": lambda y, m, d: dt.date(int(y), int(m), int(d)),
    "DATEDIF": lambda d1, d2: abs((d2 - d1).days) if all(isinstance(x, (dt.date, dt.datetime)) for x in (d1, d2)) else None,

    # --- Numpy для диапазонов ---
    "np": np,
}


def register_func(name, func):
    GLOBAL_NS[name.upper()] = func


r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def auth_flow(session, db):
    """
    Логин/регистрация + выбор таблицы и листа.
    Возвращает tuple: (user_id, sheet)
    """

    # 1. Авторизация
    while True:
        choice = input("Выберите действие: [1] Войти, [2] Зарегистрироваться: ").strip()
        if choice not in ("1", "2"):
            print("Некорректный выбор. Введите 1 или 2.")
            continue

        username = input("Имя пользователя: ").strip()
        password = input("Пароль: ").strip()
        email = None

        if choice == "2":  # регистрация
            email = input("Email (необязательно): ").strip()
            user = register_user(session, username, password, email or None)
            print(f"Пользователь '{username}' зарегистрирован.")
            user_id = user.id
            break
        elif choice == "1":  # вход
            user_id = login_user(session, username, password)
            if user_id is None:
                print("Неверный логин или пароль, попробуйте снова.")
                continue
            print(f"Добро пожаловать, {username}!")
            break

    # 2. Выбор таблицы
   
    sheet = choose_table(session, user_id, db)
    return user_id, sheet




def choose_table(session, user_id, db):

    # Получаем все таблицы пользователя
    user_tables = session.query(TableModel).filter_by(author_id=user_id).all()
    print("\nВаши таблицы:")
    for t in user_tables:
        active_mark = " (активная)" if t.active_list_id else ""
        print(f"{t.id}: {t.name} ({'видна' if t.visible_name_in_search else 'скрыта'}){active_mark}")

    table_choice = input("Введите ID таблицы или имя новой таблицы: ").strip()

    # Если ввели число — выбираем существующую
    if table_choice.isdigit():
        table = session.query(TableModel).filter_by(id=int(table_choice), author_id=user_id).first()
        if table is None:
            print("Таблица с таким ID не найдена.")
            return choose_table(session, user_id, db)
    else:
        # создаём новую
        table = TableModel(name=table_choice, author_id=user_id)
        session.add(table)
        session.commit()
        print(f"Создана новая таблица '{table_choice}'.")

    # Создаём или получаем PyTTabs таблицу
    tbl = db.ctable(table.name, user_id)  # <-- передаем user_id

    # Получаем список листов в таблице
    lists = tbl.lists()
    if lists:
        print("\nДоступные листы:")
        for i, lst in enumerate(lists, 1):
            active_mark = " (активный)" if table.active_list_id == lst.list_model.id else ""
            print(f"{i}: {lst.list_model.name}{active_mark}")

        choice = input("Выберите лист по номеру или нажмите Enter для активного/нового: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(lists):
            sheet = lists[int(choice)-1]
        elif table.active_list_id:
            # используем активный лист
            sheet = tbl.get_list_by_id(table.active_list_id)
        else:
            sheet = tbl.create_list("MainSheet")
    else:
        # Создаём новый лист по умолчанию
        sheet = tbl.create_list("MainSheet")

    # Сохраняем активный лист
    table.active_list_id = sheet.list_model.id
    session.commit()

    print(f"Выбрана таблица '{table.name}', лист '{sheet.list_model.name}'")
    return sheet





class PyCells:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def ctable(self, name):
        return TableManager(self.session, name)
    



class TableManager:
    def __init__(self, session, name):
        self.session = session
        self.name = name

    def create_list(self, name):
        new_list = ListModel(name=name, table_id=self.table.id)
        self.session.add(new_list)
        self.table.active_list_id = new_list.id  # ← обновляем активный лист
        self.session.commit()
        return ListWrapper(new_list)





class Sheet:
    def __init__(self, session, list_model, user_id=None):
        self.session = session
        self.list_model = list_model
        self.user_id = user_id  # Если указан, связываем с курсором

    def write(self, name, cell_id=None, data=None):
        # Проверка через курсор
        if self.user_id is not None:
            cursor = CursorManager.get_active(self.user_id)
            if cursor:
                # если ячейка не активна в текущем курсоре — запрет
                if name not in cursor['cells']:
                    raise PermissionError(f"Ячейка {name} не активна в текущем курсоре")

        # Дальше обычная логика записи
        cell = (
            self.session.query(CellModel)
            .filter_by(list_id=self.list_model.id, name=name)
            .first()
        )

        if not cell:
            cell = CellModel(list_id=self.list_model.id, name=name, cell_id=cell_id, data=str(data))
            self.session.add(cell)
        else:
            if cell_id:
                cell.cell_id = cell_id
            cell.data = str(data)

        self.session.commit()
        return CellWrapper(self.session, self, cell)

    def read(self, name):
        # Проверка через курсор
        if self.user_id is not None:
            cursor = CursorManager.get_active(self.user_id)
            if cursor:
                if name not in cursor['cells']:
                    raise PermissionError(f"Ячейка {name} не входит в активный курсор")

        # Обычное чтение
        cell = self.session.query(CellModel).filter_by(list_id=self.list_model.id, name=name).first()
        if cell:
            return CellWrapper(self.session, self, cell)
        return None
    


    def set_cell_style(self, cell_name, style):
        """
        Устанавливает стиль ячейки. Принимает либо строку CSS, либо dict.
        """
        cell = (
            self.session.query(CellModel)
            .filter_by(list_id=self.list_model.id, name=cell_name)
            .first()
        )
        if not cell:
            raise ValueError(f"Ячейка {cell_name} не найдена")

        if isinstance(style, dict):
            cell.style = json.dumps(style, ensure_ascii=False)
        else:
            cell.style = style

        self.session.commit()
        return cell

    



    def set_group_style(self, cell_name, style, apply_to_group=False):
        """
        Устанавливает стиль для ячейки и при необходимости — всей группы.
        """
        cell = self.session.query(CellModel).filter_by(
            list_id=self.list_model.id, name=cell_name
        ).first()
        if not cell:
            raise ValueError(f"Ячейка {cell_name} не найдена")

        # Определяем финальный формат
        style_json = json.dumps(style, ensure_ascii=False) if isinstance(style, dict) else style
        cell.style = style_json

        if apply_to_group and cell.group_id:
            self.session.query(CellModel).filter_by(
                group_id=cell.group_id
            ).update({"style": style_json})

            # Можно также обновить саму группу:
            group = self.session.query(GroupModel).get(cell.group_id)
            if group:
                group.style = style_json

        self.session.commit()
        return cell



    def get_cell_style(self, cell_name):
        """Возвращает стиль ячейки из БД."""
        cell = self.session.query(CellModel).filter_by(
            list_id=self.list_model.id,
            name=cell_name
        ).first()
        return cell.style if cell else {}
    



    def get_group_style(self, cell_name):
        """
        Возвращает стиль группы, к которой принадлежит ячейка.
        Если у ячейки нет группы — вернёт None.
        """
        cell = self.session.query(CellModel).filter_by(
            list_id=self.list_model.id,
            name=cell_name
        ).first()
        if not cell or not cell.group_id:
            return None

        group = self.session.query(GroupModel).get(cell.group_id)
        return group.style if group else None






    def write_cursor(self, db_session, user_id, cell_name, cell_id, value):
        """
        Записывает данные в ячейку через активный курсор.
        Всегда перезаписывает cell_id на переданный.
        """
        cursor = CursorManager.get_active(user_id)
        if not cursor:
            raise ValueError("Нет активного курсора для пользователя")

        if cell_name not in cursor["cells"]:
            raise PermissionError(f"Ячейка '{cell_name}' не активна в текущем курсоре")

        cell = (
            self.session.query(CellModel)
            .filter_by(list_id=self.list_model.id, name=cell_name)
            .first()
        )

        if not cell:
            # Создаём новую ячейку с указанным cell_id
            cell = CellModel(
                list_id=self.list_model.id,
                name=cell_name,
                cell_id=cell_id,
                data=str(value)
            )
            self.session.add(cell)
        else:
            # ⚠️ Всегда перезаписываем cell_id
            cell.cell_id = cell_id
            cell.data = str(value)

        self.session.commit()

        # Рекурсивный пересчёт зависимых
        lw = ListWrapper(self.session, self.list_model)
        lw.update_dependents_recursive(cell_name)

        return CellWrapper(self.session, self, cell)



    


class List:
    def __init__(self, db_session, list_model):
        self.db = db_session
        self.model = list_model

    def create_group(self, name, style=""):
        g = GroupModel(list_id=self.model.id, name=name, style=style)
        self.db.add(g)
        self.db.commit()
        return g

    def add_to_group(self, id_cell, group_name):
        """Добавляет ячейку в группу и наследует стиль группы."""
        cell = self.db.query(CellModel).filter_by(id_cell=id_cell, list_id=self.model.id).first()
        group = self.db.query(GroupModel).filter_by(list_id=self.model.id, name=group_name).first()
        if not cell or not group:
            raise ValueError("cell or group not found")
        cell.group_id = group.id
        cell.style = group.style  # наследуем стиль группы
        cell.datetime = datetime.now(timezone.utc)
        self.db.commit()

    def remove_from_group(self, id_cell):
        """Удаляет ячейку из группы и сбрасывает стиль."""
        cell = self.db.query(CellModel).filter_by(id_cell=id_cell, list_id=self.model.id).first()
        if not cell:
            raise ValueError("cell not found")
        cell.group_id = None
        cell.style = ""  # сбрасываем на дефолт
        cell.datetime = datetime.now(timezone.utc)
        self.db.commit()

    def update_group_style(self, group_name, new_style):
        """Меняет стиль группы и обновляет все ячейки внутри неё."""
        group = self.db.query(GroupModel).filter_by(list_id=self.model.id, name=group_name).first()
        if not group:
            raise ValueError("group not found")
        group.style = new_style
        group.datetime = datetime.now(timezone.utc)
        for cell in group.cells:
            cell.style = new_style
            cell.datetime = datetime.now(timezone.utc)
        self.db.commit()





# ========================== CORE LOGIC ===========================

class SafeFormulaEvaluator:
    """Безопасный вычислитель формул, использующий GLOBAL_NS"""
    def __init__(self, list_wrapper):
        self.list_wrapper = list_wrapper

    def evaluate(self, expr):
        expr = expr.strip()
        if not expr:
            return ""

        # --- Замена диапазонов на np.array([...]) ---
        def replace_range(match):
            start, end = match.group(1), match.group(2)
            values = [self.list_wrapper.get_value_by_name(c.cell.name)
                      for c in self.list_wrapper.read_range(start, end)]
            return f"np.array({values})"

        expr = re.sub(r'([A-Z]+\d+):([A-Z]+\d+)', replace_range, expr)

        # --- Замена ссылок на ячейки ---
        def replace_cell(match):
            name = match.group(0)
            val = self.list_wrapper.get_value_by_name(name)
            return str(val if val not in (None, "") else 0)

        expr = re.sub(r'\b[A-Z]+\d+\b', replace_cell, expr)

        # --- Поддержка Excel-стиля операций ---
        expr = expr.replace("^", "**")  # степень (Excel-style)
        expr = re.sub(r'(\d+(?:\.\d+)?)%', r'(\1/100)', expr)  # проценты 15% → (15/100)

        # --- Вычисление ---
        try:
            result = eval(expr, {"__builtins__": {}}, GLOBAL_NS)
        except Exception as e:
            result = f"#ERROR({e})"

        return result
    




class CellWrapper:
    """Обёртка для одной ячейки"""
    def __init__(self, session, list_wrapper, cell):
        self.session = session
        self.cell = cell
        self.list_wrapper = list_wrapper

    @property
    def data(self):
        return self.cell.data

    @data.setter
    def data(self, value):
        self.cell.data = str(value)
        self.session.commit()
        self.list_wrapper.update_dependents_recursive(self.cell.name)

    @property
    def note(self):
        return self.cell.note

    @note.setter
    def note(self, text):
        self.cell.note = text
        self.session.commit()

    def evaluate(self):
        """Если в ячейке формула, вычислить"""
        expr = str(self.cell.data or "")
        if expr.startswith("="):
            evaluator = SafeFormulaEvaluator(self.list_wrapper)
            return evaluator.evaluate(expr[1:])
        try:
            return float(expr)
        except ValueError:
            return expr





class ListWrapper:
    """Обёртка для листа с рекурсивным обновлением зависимостей"""
    def __init__(self, session, list_model):
        self.session = session
        self.list_model = list_model

    # ---------- CRUD ----------
    def write(self, name, *args):
        """
        sheet.write("A1", "0000.0020.0100.0021", "10")
        или sheet.write("A1", "10")
        """
        # Разбираем аргументы
        if len(args) == 1:
            cell_id = None
            value = args[0]
        elif len(args) == 2:
            cell_id, value = args
        else:
            raise ValueError("Неверное количество аргументов. Используй write(name, value) или write(name, cell_id, value)")

        # Ищем или создаём ячейку
        cell = (
            self.session.query(CellModel)
            .filter_by(list_id=self.list_model.id, name=name)
            .first()
        )

        if not cell:
            cell = CellModel(list_id=self.list_model.id, name=name, cell_id=cell_id, data=str(value))
            self.session.add(cell)
        else:
            # обновляем существующую
            if cell_id:
                cell.cell_id = cell_id
            cell.data = str(value)

        self.session.commit()
        self.update_dependents_recursive(name)
        return CellWrapper(self.session, self, cell)
    


    def read(self, cell_name):
        cell = (
            self.session.query(CellModel)
            .filter_by(list_id=self.list_model.id, name=cell_name)
            .first()
        )
        return CellWrapper(self.session, self, cell) if cell else None
    


    def write_range(self, start, end, value, group=None):
        """Массовая запись диапазона (по номерам ячеек, не ID)"""
        for i in range(int(start), int(end) + 1):
            cell = self.write(str(i), value)
            if group:
                # Если передали объект GroupModel
                if isinstance(group, GroupModel):
                    cell.cell.group = group
                else:
                    # Передали строку — ищем/создаём объект
                    grp = self.session.query(GroupModel).filter_by(
                        list_id=self.list_model.id, name=group
                    ).first()
                    if not grp:
                        grp = GroupModel(list_id=self.list_model.id, name=group)
                        self.session.add(grp)
                        self.session.commit()
                    cell.cell.group = grp
        # Один коммит после всего диапазона
        if group:
            self.session.commit()



    # ---------- GROUP ----------
    def set_group(self, cell_name, group_name):
        # ищем ячейку
        cell = (
            self.session.query(CellModel)
            .filter_by(list_id=self.list_model.id, name=cell_name)
            .first()
        )
        if not cell:
            return

        # ищем или создаём группу
        group = (
            self.session.query(GroupModel)
            .filter_by(list_id=self.list_model.id, name=group_name)
            .first()
        )
        if not group:
            group = GroupModel(list_id=self.list_model.id, name=group_name)
            self.session.add(group)
            self.session.commit()

        # привязываем ячейку к группе
        cell.group_id = group.id

        # применяем стиль группы, если есть
        if group.style:
            cell.style = group.style

        self.session.commit()




    #   sheet.update_group_style("Finance", "background-color: yellow; font-weight: bold;")
    def update_group_style(self, group_name, new_style):    
        group = (
            self.session.query(GroupModel)
            .filter_by(list_id=self.list_model.id, name=group_name)
            .first()
        )
        if not group:
            return f"Группа '{group_name}' не найдена"

        group.style = new_style
        for cell in group.cells:
            cell.style = new_style

        self.session.commit()



    def ungroup(self, cell_name):
        cell = (
            self.session.query(CellModel)
            .filter_by(list_id=self.list_model.id, name=cell_name)
            .first()
        )
        if cell:
            cell.group = None
            cell.style = ""
            self.session.commit()



    # ---------- FORMULA SYSTEM ----------
    def get_value_by_name(self, name):
        cell = (
            self.session.query(CellModel)
            .filter_by(list_id=self.list_model.id, name=name)
            .first()
        )
        if not cell:
            return 0
        wrap = CellWrapper(self.session, self, cell)
        return wrap.evaluate()
    


    def update_dependents_recursive(self, name, visited=None):
        """Рекурсивное обновление зависимостей"""
        if visited is None:
            visited = set()
        if name in visited:
            return  # защита от циклов
        visited.add(name)

        # Находим все ячейки, где есть формулы, ссылающиеся на name
        dependents = (
            self.session.query(CellModel)
            .filter(
                CellModel.list_id == self.list_model.id,
                CellModel.data.like("=%" + name + "%")
            )
            .all()
        )

        for dep in dependents:
            wrap = CellWrapper(self.session, self, dep)
            new_value = wrap.evaluate()

            # сохраняем формулу, но можно хранить вычисленное значение в кеше
            dep.data = dep.data  # формула не меняется
            self.session.commit()

            # рекурсивно пересчитать зависимые от этой ячейки
            self.update_dependents_recursive(dep.name, visited)




    def write_cursor(self, db_session, user_id, cell_name, cell_id, value):
        """
        Записывает данные в ячейку через активный курсор.
        Всегда перезаписывает cell_id на переданный.
        """
        cursor = CursorManager.get_active(user_id)
        if not cursor:
            raise ValueError("Нет активного курсора для пользователя")

        if cell_name not in cursor["cells"]:
            raise PermissionError(f"Ячейка '{cell_name}' не активна в текущем курсоре")

        cell = (
            self.session.query(CellModel)
            .filter_by(list_id=self.list_model.id, name=cell_name)
            .first()
        )

        if not cell:
            # Создаём новую ячейку с указанным cell_id
            cell = CellModel(
                list_id=self.list_model.id,
                name=cell_name,
                cell_id=cell_id,
                data=str(value)
            )
            self.session.add(cell)
        else:
            # ⚠️ Всегда перезаписываем cell_id
            cell.cell_id = cell_id
            cell.data = str(value)

        self.session.commit()

        # Рекурсивный пересчёт зависимых
        lw = ListWrapper(self.session, self.list_model)
        lw.update_dependents_recursive(cell_name)

        return CellWrapper(self.session, self, cell)
  


    @property
    def cells_dict(self):
        """Возвращает словарь всех ячеек list_id: name -> CellWrapper"""
        all_cells = self.session.query(CellModel).filter_by(list_id=self.list_model.id).all()
        return {c.name: CellWrapper(self.session, self, c) for c in all_cells}




    def read_range(self, start, end):
        # Преобразуем "X1" -> ("X", 1)
        def cell_to_index(cell):
            col = ''.join(filter(str.isalpha, cell))
            row = int(''.join(filter(str.isdigit, cell)))
            return col, row

        start_col, start_row = cell_to_index(start)
        end_col, end_row = cell_to_index(end)

        # Сейчас простой вариант: только по строкам
        return [self.read(f"{start_col}{i}") for i in range(start_row, end_row + 1)]








class TableWrapper:
    def __init__(self, session, table_model):
        self.session = session
        self.table_model = table_model

    def create_list(self, name):
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

        return ListWrapper(self.session, lst)
    def lists(self):
        """Возвращает все листы, связанные с этой таблицей."""
        lst_models = (
            self.session.query(ListModel)
            .filter_by(table_id=self.table_model.id)
            .all()
        )
        return [ListWrapper(self.session, lst) for lst in lst_models]

    def get_list_by_id(self, list_id):
        """Возвращает лист по его ID."""
        lst = (
            self.session.query(ListModel)
            .filter_by(id=list_id, table_id=self.table_model.id)
            .first()
        )
        if lst:
            return ListWrapper(self.session, lst)
        return None





class PyTTabs:
    def __init__(self, db_url="sqlite:///pyttabs.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def ctable(self, name, user_id):
        table = (
            self.session.query(TableModel)
            .filter_by(name=name, author_id=user_id)
            .first()
        )
        if not table:
            table = TableModel(name=name, author_id=user_id)
            self.session.add(table)
            self.session.commit()
        return TableWrapper(self.session, table)





class CursorManager:
    """Гибридный менеджер курсора — Redis для скорости, SQLAlchemy для истории."""

    @staticmethod
    def _redis_key(user_id):
        return f"cursor:{user_id}"

    @staticmethod
    def _prec_redis_key(user_id):
        return f"prec_cursor:{user_id}"

    @classmethod
    def set_cursor(cls, session: Session, user_id: int, table_id: int, list_id: int, cells: list[str]):
        """Активирует новый курсор, старый становится prec_cursor."""
        # Сохраняем текущий как prec_cursor
        current = cls.get_active(user_id)
        if current:
            r.set(cls._prec_redis_key(user_id), json.dumps(current))

        # Активируем новый курсор
        return cls.activate(session, user_id, table_id, list_id, cells)

    @classmethod
    def get_prec_cursor(cls, user_id: int):
        raw = r.get(cls._prec_redis_key(user_id))
        return json.loads(raw) if raw else None

    # === Основной метод активации ===
    @classmethod
    def activate(cls, session: Session, user_id: int, table_id: int, list_id: int, cells: list[str]):
        """Активирует новый курсор и сохраняет в Redis + SQLAlchemy."""
        key = cls._redis_key(user_id)
        now = datetime.now(timezone.utc)
        data = {
            "user_id": user_id,
            "table_id": table_id,
            "list_id": list_id,
            "cells": cells,
            "timestamp": now.isoformat()
        }

        # Redis — мгновенное состояние
        r.set(key, json.dumps(data))

        # SQLAlchemy — история и откат
        cursor = CursorModel(
            user_id=user_id,
            table_id=table_id,
            list_id=list_id,
            cells=cells,
            created_at=now
        )
        session.add(cursor)
        session.commit()

        return data

    @classmethod
    def get_active(cls, user_id: int):
        key = cls._redis_key(user_id)
        raw = r.get(key)
        return json.loads(raw) if raw else None

    @classmethod
    def get_previous(cls, session: Session, user_id: int):
        cursors = (
            session.query(CursorModel)
            .filter(CursorModel.user_id == user_id)
            .order_by(CursorModel.id.desc())
            .limit(2)
            .all()
        )
        return cursors[1] if len(cursors) == 2 else None

    @classmethod
    def clear(cls, session: Session, user_id: int):
        r.delete(cls._redis_key(user_id))
        r.delete(cls._prec_redis_key(user_id))
        session.query(CursorModel).filter(CursorModel.user_id == user_id).delete()
        session.commit()




# print_cells(structure)
def print_cells(structure, prefix=""):                                 
    for key in sorted(structure.keys()):
        value = structure[key]
        if isinstance(value, dict) and "data" not in value:
            print_cells(value, prefix + key + ".")
        else:
            print(f"{prefix}{key}.{value['name']} = {value['data']}")

            

