from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    Group,
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.utils import timezone

from accounts.constants import (
    RoleConsts,
    UserConsts,
)
from accounts.errors import UserErrors


class Role(models.Model):
    code = models.SlugField(
        verbose_name="Идентификатор",
        unique=True,
    )
    name = models.CharField(
        verbose_name="Название роли",
        max_length=RoleConsts.NAME_MAX_LENGTH,
        unique=True,
    )
    description = models.TextField(
        verbose_name="Описание роли",
        blank=True,
    )
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="role",
        verbose_name="Группа",
    )
    is_self_registerable = models.BooleanField(
        verbose_name="Является ли роль саморегистрируемой",
        default=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Необходимо указать адрес электронной почты!")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        max_length=UserConsts.EMAIL_MAX_LENGTH,
        null=False,
        blank=False,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=UserConsts.FIRST_NAME_MAX_LENGTH,
        blank=False,
        null=False,
    )
    middle_name = models.CharField(
        verbose_name="Отчество",
        max_length=UserConsts.MIDDLE_NAME_MAX_LENGTH,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=UserConsts.LAST_NAME_MAX_LENGTH,
        blank=False,
        null=False,
    )
    phone_number = models.CharField(
        verbose_name="Номер телефона",
        validators=[
            RegexValidator(
                regex=r"^\+7 \(\d{3}\) \d{3}\-\d{2}-\d{2}$",
                message="Введите номер телефона в формате +7 (ХХХ) ХХХ-ХХ-ХХ",
                code=UserErrors.INVALID_PHONE_NUMBER,
            )
        ],
        max_length=UserConsts.PHONE_NUMBER_MAX_LENGTH,
        null=False,
        blank=False,
        unique=True,
    )
    role = models.ForeignKey(
        Role,
        verbose_name="Роль пользователя",
        on_delete=models.PROTECT,
        null=True,
    )
    date_joined = models.DateTimeField(
        verbose_name="Дата и время регистрации",
        default=timezone.now,
        editable=False,
    )
    is_staff = models.BooleanField(
        verbose_name="Сотрудник",
        default=False,
    )
    is_active = models.BooleanField(
        verbose_name="Активен",
        default=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "phone_number",
    ]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = (
            "last_name",
            "first_name",
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.role_id:
            self.groups.set([self.role.group])

    def __str__(self):
        if not self.middle_name:
            return f"{self.email} - {self.last_name} {self.first_name[0].upper()}."
        return f"{self.email} - {self.last_name} {self.first_name[0].upper()}.{self.middle_name[0].upper()}."
