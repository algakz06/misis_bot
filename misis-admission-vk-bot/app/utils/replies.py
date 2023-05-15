#!/usr/bin/env python3

"""Reply strings for AIOGram."""


def profile_info(profile: dict) -> str:
    """Return user's profile menu."""
    return f"""🛂 Профиль

👤 Имя: {profile["first_name"]}
👥 Фамилия: {profile["last_name"]}
🏙 Город: {profile["city"]}
📞 Телефон: {profile["phone_number"]}
📧 Почта: {profile["email"]}"""


def not_registered(first_name: str) -> str:
    """Return not registered message."""
    return f"""👋 Привет, {first_name}!

📝 Для начала работы с ботом, пожалуйста, зарегистрируйся! Нажми сюда: /start"""
