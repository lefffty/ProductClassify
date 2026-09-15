from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from accounts.models import Role
from accounts.errors import SignUpErrors, UserErrors
from accounts.constants import UserConsts


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
        error_messages = {
            "email": {
                "unique": SignUpErrors.NON_UNIQUE_EMAIL,
                "required": UserErrors.EMPTY_EMAIL,
            }
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if (
            phone_number
            and User.objects.filter(phone_number__exact=phone_number).exists()
        ):
            raise ValidationError(SignUpErrors.NON_UNIQUE_PHONE_NUMBER)
        else:
            return phone_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].queryset = Role.objects.filter(
            is_self_registerable=True
        )
        self.fields["phone_number"].widget.attrs.update({
            "class": "form-control",
            "id": "id_phone_number",
            "data-phone-mask": "true",
            "inputmode": "tel",
            "autocomplete": "tel",
            "placeholder": "+7 (___) ___-__-__",
            "maxlength": "18",
        })

    def save(self, commit=True):
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


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=UserConsts.EMAIL_MAX_LENGTH,
        help_text="Введите адрес электронной почты",
        label="Адрес электронной почты",
        required=True,
        error_messages={
            "required": UserErrors.EMPTY_EMAIL,
        },
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "autocomplete": "email",
            "placeholder": "you@example.com",
        }),
    )
    password = forms.CharField(
        label="Пароль",
        help_text="Введите пароль",
        max_length=UserConsts.PASSWORD_MAX_LENGTH,
        required=True,
        error_messages={
            "required": UserErrors.EMPTY_PASSWORD
        },
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "autocomplete": "current-password",
        }),
    )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        # сохраняем объект запрос для последующего использования при аутентификации
        self.request = request
        # сохраняем пользователя в форме чтобы потом передать его в функцию login
        self.user = None

    def clean(self):
        # очищаем введенные данные
        cleaned_data = super().clean()

        # получаем email из очищенных данных
        email = cleaned_data.get("email")
        # получаем пароль из очищенных данных
        password = cleaned_data.get("password")

        # если введены оба поля
        if email and password:
            try:
                self.user = User.objects.get(email=email)
            # если пользователь не найден, то поднимаем исключение
            except User.DoesNotExist:
                User().set_password(password)
                raise forms.ValidationError(
                    UserErrors.INVALID_CREDENTIALS
                )

            # если пароль неправильный, то поднимаем исключение
            if not self.user.check_password(password):
                raise forms.ValidationError(
                    UserErrors.INVALID_CREDENTIALS,
                )

            # если пользователь не активен, поднимаем исключение
            if not self.user.is_active:
                raise forms.ValidationError(
                    UserErrors.INACTIVE_USER
                )

        # возвращаем очищенные данные
        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "phone_number",
        )
