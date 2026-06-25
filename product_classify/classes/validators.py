from django.core.exceptions import ValidationError


def positive_validate(value):
    if value < 0.0:
        raise ValidationError("""Границы диапазона значений параметра класса
            должны быть положительными!""")
