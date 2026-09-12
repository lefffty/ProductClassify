from enum import StrEnum


class UserErrors(StrEnum):
    INVALID_PHONE_NUMBER = "Неверный формат телефонного номера. Номер телефона должен соответствовать следующему формату: +7 (ХХХ) ХХХ-ХХ-ХХ."
    EMPTY_EMAIL = "Поле для адреса электронной почты необходимо заполнить"
    EMPTY_PASSWORD = "Поле для пароля пользователя необходимо заполнить"
    INVALID_CREDENTIALS = "Неверный адрес электронной почты или пароль"
    INACTIVE_USER = "Учётная запись отключена. Обратитесь к администратору."


class SignUpErrors(StrEnum):
    COMMIT_IS_FALSE = "Используйте save(commit=True) либо переопределите логику."
