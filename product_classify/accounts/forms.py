from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from accounts.models import Role
from accounts.errors import SignUpErrors


User = get_user_model()


class SignUpForm(UserCreationForm):
    role = forms.ModelChoiceField(
        queryset=Role.objects.none(),
        label="Роль",
        empty_label="Выберите роль",
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "phone_number",
            "role",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].queryset = Role.objects.filter(
            is_self_registerable=True
        )

    def save(self, commit=False):
        user = super().save(commit=False)
        role = self.cleaned_data["role"]
        if commit:
            user.save()
            user.groups.add(role.group)
        else:
            raise NotImplementedError(
                SignUpErrors.COMMIT_IS_FALSE
            )
        return user
