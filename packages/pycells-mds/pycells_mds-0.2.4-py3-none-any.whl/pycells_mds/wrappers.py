# wrappers/list_wrapper.py

from .session import db
from .models import TableModel, ListModel, CellModel, GroupModel
import numpy as np
import datetime as dt
import re







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








class CellWrapper:
    """
    Обёртка одной ячейки.
    Отвечает за вычисление формул, чтение/запись данных,
    и выполнение логики уровня ячейки.
    """

    formula_pattern = re.compile(r"^=(.+)$")  # формула начинается с "="

    def __init__(self, cell_model: CellModel):
        self.model = cell_model
        self.session = db.session

    # ----------------------------------------------------------
    # ЧТЕНИЕ И ЗАПИСЬ
    # ----------------------------------------------------------

    def read_data(self):
        """Возвращает текст/формулу, записанную в ячейку (cell.data)."""
        return self.model.data or ""

    def write_data(self, value: str):
        """Записывает новое содержимое ячейки."""
        self.model.data = value
        self.session.commit()

    # ----------------------------------------------------------
    # ВЫЧИСЛЕНИЕ
    # ----------------------------------------------------------

    def evaluate(self):
        """
        Вычисляет значение ячейки.
        Если это формула — парсит и считает.
        Если обычный текст — возвращает как есть.
        """
        raw = self.read_data()

        # -----------------------------
        # 1) Нет формулы, обычный текст
        # -----------------------------
        match = self.formula_pattern.match(raw)
        if not match:
            return raw or ""

        expr = match.group(1).strip()

        # -----------------------------
        # 2) ЕСЛИ ЕСТЬ ФОРМУЛА
        # -----------------------------
        return self._evaluate_formula(expr)

    # ----------------------------------------------------------
    # ФОРМУЛЫ (минимальный прототип)
    # ----------------------------------------------------------

    def _evaluate_formula(self, expr: str):
        import string

        # --- вспомогательные функции для диапазонов ---
        def col_to_index(col: str) -> int:
            # A -> 1, Z -> 26, AA -> 27
            col = col.upper()
            idx = 0
            for ch in col:
                if ch in string.ascii_uppercase:
                    idx = idx * 26 + (ord(ch) - ord("A") + 1)
            return idx

        def index_to_col(index: int) -> str:
            # 1 -> A, 27 -> AA
            result = ""
            while index > 0:
                index, rem = divmod(index - 1, 26)
                result = chr(rem + ord("A")) + result
            return result

        def split_cell(cell_name: str):
            m = re.match(r"^([A-Za-z]+)(\d+)$", cell_name)
            if not m:
                raise ValueError(f"Invalid cell name: {cell_name}")
            return m.group(1).upper(), int(m.group(2))

        def expand_range(a: str, b: str):
            # возвращает список имён ячеек от a до b (вкл.)
            col_a, row_a = split_cell(a)
            col_b, row_b = split_cell(b)

            c1 = col_to_index(col_a)
            c2 = col_to_index(col_b)
            r1 = row_a
            r2 = row_b

            cols = range(min(c1, c2), max(c1, c2) + 1)
            rows = range(min(r1, r2), max(r1, r2) + 1)

            cells = []
            for ci in cols:
                for ri in rows:
                    cells.append(f"{index_to_col(ci)}{ri}")
            return cells

        # --- 1) Обработка диапазонов вида A1:A3 ---
        # Найдём все вхождения диапазонов и заменим их на списки значений
        range_pattern = re.compile(r"([A-Za-z]+[0-9]+):([A-Za-z]+[0-9]+)")
        # делаем несколько проходов, чтобы поймать вложенные/несколько диапазонов
        while True:
            m = range_pattern.search(expr)
            if not m:
                break
            a, b = m.group(1), m.group(2)
            names = expand_range(a, b)

            vals = []
            for name in names:
                # находим ячейку, вычисляем её рекурсивно
                cell = (
                    self.session.query(CellModel)
                    .filter_by(table_id=self.model.table_id,
                                list_id=self.model.list_id,
                                name=name)
                    .first()
                )
                if not cell:
                    vals.append(0)
                    continue
                wrap = CellWrapper(cell)
                v = wrap.evaluate()
                # попытка привести к числу, иначе оставляем как строку
                try:
                    nv = float(v)
                except Exception:
                    # если строка — как строка (с кавычками)
                    nv = v
                vals.append(nv)

            # Подставляем Python-лист в выражение:
            # строки должны быть repr'ами, числа — как есть
            py_items = []
            for v in vals:
                if isinstance(v, (int, float)):
                    py_items.append(str(v))
                else:
                    # экранируем кавычки корректно
                    py_items.append(repr(str(v)))
            list_literal = "[" + ",".join(py_items) + "]"

            # заменить первое вхождение диапазона на list_literal
            expr = expr[:m.start()] + list_literal + expr[m.end():]

        # --- 2) Теперь обработаем простые ссылки типа A1, B2 ---
        tokens = re.findall(r"[A-Za-z]+[0-9]+", expr)

        # Чтобы не обрабатывать диапазоны и уже подставленные списки повторно,
        # используем словарь, но делаем замену через regex с границами.
        values = {}

        for token in sorted(set(tokens), key=lambda s: -len(s)):
            # пропускаем случаи, где токен уже внутри литерала списка (например [1,2,A1])
            if re.search(r"\[" + re.escape(token) + r"\]", expr):
                # уже обработан внутри списка
                continue

            cell = (
                self.session.query(CellModel)
                .filter_by(table_id=self.model.table_id,
                            list_id=self.model.list_id,
                            name=token)
                .first()
            )

            if not cell:
                values[token] = 0
                continue

            wrap = CellWrapper(cell)
            val = wrap.evaluate()

            # если это число — приведём к float, иначе оставим строкой
            try:
                numeric_val = float(val)
                values[token] = numeric_val
            except Exception:
                # строковые значения должны быть корректно экранированы при подстановке
                values[token] = repr(str(val))

        # выполняем аккуратную замену токенов (с границами) на их значения
        expr_eval = expr
        for k, v in values.items():
            # если v — число (int/float), вставляем как есть; если строка — v уже repr
            if isinstance(v, (int, float)):
                repl = str(v)
            else:
                repl = v
            expr_eval = re.sub(rf"\b{re.escape(k)}\b", repl, expr_eval)

        # --- 3) Заменяем оператор ^ на ** (Excel-степень) ---
        # но не меняем внутри строк (простой подход — если есть кавычки, оставляем риск)
        expr_eval = expr_eval.replace("^", "**")

        # --- 4) Eval в безопасной среде с GLOBAL_NS ---
        try:
            result = eval(expr_eval, {"__builtins__": {}}, GLOBAL_NS)
        except Exception:
            result = "#ERROR"

        return result







class ListWrapper:
    """
    Логическая обёртка листа.
    Работает с моделями, пересчётом, функциями, чтением/записью ячеек.
    """

    def __init__(self, list_model: ListModel):
        self.model = list_model
        self.session = db.session   # единая session из session.py

    # ------------------------------------------
    # БАЗОВЫЕ ОПЕРАЦИИ LIST
    # ------------------------------------------

    def get_cell(self, name: str) -> CellModel | None:
        """Возвращает ORM CellModel по имени ячейки."""
        return (
            self.session.query(CellModel)
            .filter_by(list_id=self.model.id, name=name)
            .first()
        )

    def read(self, name: str):
        """
        Возвращает текущее значение ячейки.
        Если есть формула — вернёт уже вычисленное value.
        Если value пустое — пустая строка.
        """
        cell = self.get_cell(name)
        if not cell:
            return ""

        return cell.value if cell.value is not None else ""

    def write(self, name: str, value: str):
        cell = self.get_cell(name)

        if not cell:
            cell = CellModel(
                list_id=self.model.id,
                table_id=self.model.table_id,
                name=name,
                data=value,
            )
            self.session.add(cell)
        else:
            cell.data = value

        # === добавляем автоматический пересчёт ===
        wrapper = CellWrapper(cell)
        try:
            cell.value = wrapper.evaluate()
        except:
            cell.value = "#ERROR"

        self.session.commit()
        return cell


    # ------------------------------------------
    # ВЫЧИСЛЕНИЕ
    # ------------------------------------------

    def evaluate_cell(self, name: str):
        """Пересчитать конкретную ячейку."""
        cell = self.get_cell(name)
        if not cell:
            return None

        wrapper = CellWrapper(cell)
        try:
            result = wrapper.evaluate()
            cell.value = result
            self.session.commit()
            return result

        except Exception:
            cell.value = "#ERROR"
            self.session.commit()
            return "#ERROR"

    def recalc_all(self):
        """
        Пересчитать все ячейки листа.
        Полная замена старого recalc_all_safe().
        Логика теперь лежит ТУТ, а не в модели.
        """
        for cell in self.model.cells:
            wrapper = CellWrapper(cell)
            try:
                value = wrapper.evaluate()
                cell.value = value
            except Exception:
                cell.value = "#ERROR"

        self.session.commit()

    # ------------------------------------------
    # СТРАТЕГИЧЕСКИЕ ОПЕРАЦИИ
    # ------------------------------------------

    def get_all_cells(self):
        """Вернуть все ячейки листа (ORM объекты)."""
        return self.model.cells

    def delete_cell(self, name: str):
        """Удалить ячейку по имени."""
        cell = self.get_cell(name)
        if cell:
            self.session.delete(cell)
            self.session.commit()

    def clear(self):
        """Удалить все ячейки листа."""
        for cell in self.model.cells:
            self.session.delete(cell)
        self.session.commit()


    def add_group(self, name: str, cell_names: list[str], style: str = ""):
        """Создаёт группу и добавляет в неё указанные ячейки."""

        # создаём группу
        group = GroupModel(
            list_id=self.model.id,
            name=name,
            style=style,
        )
        db.session.add(group)
        db.session.commit()

        # привязываем ячейки к группе
        cells = (
            db.session.query(CellModel)
            .filter(
                CellModel.list_id == self.model.id,
                CellModel.name.in_(cell_names)
            )
            .all()
        )

        for cell in cells:
            cell.group_id = group.id

        db.session.commit()
        return group
    


    def get_group(self, name: str):
        return (
            db.session.query(GroupModel)
            .filter_by(list_id=self.model.id, name=name)
            .first()
        )
    


    def update_group_style(self, name: str, style: str):
        group = self.get_group(name)
        if not group:
            return None

        group.style = style
        db.session.commit()
        return group
    


    def get_group_cells(self, name: str):
        group = self.get_group(name)
        if not group:
            return []

        return group.cells




    def delete_group(self, name: str):
        group = self.get_group(name)
        if not group:
            return None

        # почистить привязки
        for cell in group.cells:
            cell.group_id = None

        db.delete(group)
        db.session.commit()
        return True
    


    def update_group_style(self, name, style):
        group = self.get_group(name)
        if not group:
            return None

        group.style = style
        db.session.commit()

        for cell in group.cells:
            # если ячейка не имеет собственного style
            if not cell.style:
                cell.style = style

        db.session.commit()
        return group
    


    def get_style(self, name: str) -> str:
        cell = self.get_cell(name)
        return cell.style if cell else ""
    


    def set_style(self, name: str, style: str):
        cell = self.get_cell(name)
        if not cell:
            return None
        cell.style = style
        self.session.commit()
        return cell
    


    def get_note(self, name: str) -> str:
        cell = self.get_cell(name)
        return cell.note if cell else ""
    


    def set_note(self, name: str, note: str):
        cell = self.get_cell(name)
        if not cell:
            return None
        cell.note = note
        self.session.commit()
        return cell
    


    def clear_style(self, name: str):
        cell = self.get_cell(name)
        if cell:
            cell.style = ""
            self.session.commit()
            

    def clear_note(self, name: str):
        cell = self.get_cell(name)
        if cell:
            cell.note = None
            self.session.commit()















class TableWrapper:
    """
    Обёртка таблицы (как Excel workbook: Book → Sheets).
    Управляет листами, активным листом и базовыми операциями.
    """

    def __init__(self, table_model: TableModel):
        self.model = table_model
        self.session = db.session

    # ----------------------------------------------------------
    # ПОЛУЧЕНИЕ ЛИСТОВ
    # ----------------------------------------------------------

    def get_list(self, name: str) -> ListWrapper | None:
        """Получить существующий лист по имени."""
        lst = (
            self.session.query(ListModel)
            .filter_by(table_id=self.model.id, name=name)
            .first()
        )
        return ListWrapper(lst) if lst else None

    def all_lists(self):
        """Вернуть все листы таблицы."""
        return [ListWrapper(lst) for lst in self.model.lists]

    # ----------------------------------------------------------
    # СОЗДАНИЕ ЛИСТА
    # ----------------------------------------------------------

    def create_list(self, name: str, password: str | None = None):
        """Создаёт новый лист в таблице."""
        exists = (
            self.session.query(ListModel)
            .filter_by(table_id=self.model.id, name=name)
            .first()
        )

        if exists:
            return ListWrapper(exists)

        lst = ListModel(
            table_id=self.model.id,
            name=name,
            password=password,
        )

        self.session.add(lst)
        self.session.commit()

        return ListWrapper(lst)

    # ----------------------------------------------------------
    # УДАЛЕНИЕ ЛИСТА
    # ----------------------------------------------------------

    def delete_list(self, name: str):
        """Удаляет лист по имени."""
        lst = (
            self.session.query(ListModel)
            .filter_by(table_id=self.model.id, name=name)
            .first()
        )

        if lst:
            self.session.delete(lst)
            self.session.commit()

    # ----------------------------------------------------------
    # АКТИВНЫЙ ЛИСТ
    # ----------------------------------------------------------

    def set_active_list(self, name: str):
        """Назначает активный лист."""
        lst = (
            self.session.query(ListModel)
            .filter_by(table_id=self.model.id, name=name)
            .first()
        )

        if not lst:
            return None

        self.model.active_list_id = lst.id
        self.session.commit()

        return ListWrapper(lst)

    def get_active_list(self) -> ListWrapper | None:
        """Возвращает активный лист."""
        if not self.model.active_list_id:
            return None

        lst = self.session.query(ListModel).get(self.model.active_list_id)
        return ListWrapper(lst) if lst else None

    # ----------------------------------------------------------
    # УТИЛИТЫ / МЕТАДАННЫЕ
    # ----------------------------------------------------------

    def rename(self, new_name: str):
        """Переименовать таблицу."""
        self.model.name = new_name
        self.session.commit()

    def delete(self):
        """Удалить таблицу со всеми листами."""
        self.session.delete(self.model)
        self.session.commit()



