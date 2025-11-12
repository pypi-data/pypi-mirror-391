import hashlib
from .models import UserModel
from sqlalchemy import or_

# --- Хэширование пароля ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hash_: str) -> bool:
    return hash_password(password) == hash_

# --- Регистрация пользователя ---
# --- Регистрация пользователя ---
def register_user(session, username: str, password: str, email: str = None) -> UserModel:
    # Приводим пустую строку email к None
    email = email.strip() if email else None
    if email == "":
        email = None

    # Проверяем уникальность username
    existing_user = session.query(UserModel).filter_by(username=username).first()
    if existing_user:
        raise ValueError(f"Пользователь с именем {username} уже существует.")

    # Проверяем уникальность email, если он указан
    if email:
        existing_email = session.query(UserModel).filter_by(email=email).first()
        if existing_email:
            raise ValueError(f"Пользователь с email {email} уже существует.")

    user = UserModel(
        username=username,
        password_hash=hash_password(password),
        email=email
    )
    session.add(user)
    session.commit()
    return user


# --- Логин пользователя ---
def login_user(session, username: str, password: str) -> int | None:
    user = session.query(UserModel).filter_by(username=username).first()
    if user and verify_password(password, user.password_hash):
        return user.id
    return None




def safe_register_user(session, username, password, email=None):
    """
    Безопасная регистрация: проверяет, существует ли пользователь с таким username или email.
    Если существует — возвращает существующего пользователя и печатает предупреждение.
    Если нет — создаёт нового.
    """
    exists = session.query(UserModel).filter(
        or_(UserModel.username == username, UserModel.email == email)
    ).first()
    if exists:
        print(f"Пользователь с username '{username}' или email '{email}' уже существует")
        user_id = login_user(session, username, password)  # возвращаем user_id
        return exists, user_id
    user = register_user(session, username, password, email)
    user_id = login_user(session, username, password)
    return user, user_id
