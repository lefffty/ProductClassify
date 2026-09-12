from enum import StrEnum


class UserErrors(StrEnum):
    INVALID_PHONE_NUMBER = "Неверный формат телефонного номера. Номер телефона должен соответствовать следующему формату: +7 (ХХХ) ХХХ-ХХ-ХХ."


class SignUpErrors(StrEnum):
    COMMIT_IS_FALSE = "Используйте save(commit=True) либо переопределите логику."
