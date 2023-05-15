from vkbottle import BaseStateGroup


class User(BaseStateGroup):
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    CITY = "city"
    EMAIL = "email"
    PHONE = "phone"


class UserEditProfile(BaseStateGroup):
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    CITY = "city"
    EMAIL = "email"
    PHONE = "phone"
