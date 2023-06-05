#!/usr/bin/env python3

def profile_info(profile: dict) -> str:
    """Return user's profile menu."""
    return f"""🛂 Профиль

👤 Имя: {profile["first_name"]}
👥 Фамилия: {profile["last_name"]}
🏙 Город: {profile["city"]}
📧 Почта: {profile["email"]}
📞 Телефон: {profile["phone_number"]}"""
