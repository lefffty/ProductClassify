from enum import StrEnum


class UserErrors(StrEnum):
    INVALID_PHONE_NUMBER = (
        "Неверный формат телефонного номера. Номер телефона должен соответствовать следующему формату: +7 (ХХХ) ХХХ-ХХ-ХХ."
    )
