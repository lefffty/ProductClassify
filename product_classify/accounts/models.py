from django.db import models
from django.contrib.auth.models import Group

from accounts.constants import RoleConsts


class Role(models.Model):
    code = models.SlugField(
        verbose_name="Идентификатор",
        unique=True,
    )
    name = models.CharField(
        verbose_name="Название роли",
        max_length=RoleConsts.NAME_MAX_LENGTH
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
        ordering = (
            "name",
        )

    def __str__(self):
        return self.name
