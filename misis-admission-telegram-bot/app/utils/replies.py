#!/usr/bin/env python3

"""Reply strings for AIOGram."""


def profile_info(profile: dict) -> str:
    """Return user's profile menu."""
    return f"""🛂 Профиль

👤 Имя: {profile["first_name"]}
👥 Фамилия: {profile["last_name"]}
🏙 Город: {profile["city"]}
📧 Почта: {profile["email"]}
📞 Телефон: {profile["phone_number"]}"""


def not_registered(first_name: str) -> str:
    """Return not registered message."""
    return f"""👋 Привет, {first_name}!

📝 Для начала работы с ботом, пожалуйста, зарегистрируйся! Нажми сюда: /start"""


def profile_edit_first_name(first_name: str, last_name: str) -> str:
    return f"""🛂 Изменение имени

Текущее имя: {first_name}
Фамилия: {last_name}

Отправь новое имя"""


def profile_edit_last_name(first_name: str, last_name: str) -> str:
    return f"""🛂 Изменение фамилии

Имя: {first_name}
Текущая фамилия: {last_name}

Отправь новую фамилию"""


def profile_edit_city(city: str) -> str:
    return f"""🛂 Изменение города
    
Текущий город: {city}

Отправь новый город"""


def profile_edit_email(email: str) -> str:
    return f"""🛂 Изменение почты

Текущий email: {email}

Формат: example@exampledomain.com
Отправь новый адрес электронной почты"""


def profile_edit_phone(phone: int) -> str:
    return f"""🛂 Изменение номера телефона

Текущий номер: {phone}

Формат: 79991230101
Отправь новый номер телефона"""


def invalid_city_try_again() -> str:
    return """🏙 Неверный город

Попробуй еще раз!"""


def invalid_email_try_again() -> str:
    return """📧 Неверный email

Попробуй еще раз!"""


def invalid_phone_try_again() -> str:
    return """📞 Неверный номер телефона

Попробуй еще раз!"""
