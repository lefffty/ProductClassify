from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.conf import settings
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme

from accounts.forms import LoginForm, SignUpForm


def login_view(request: HttpRequest) -> HttpResponse:
    # если пользователь уже вошел в систему,
    # то перенаправляем его на главную страницу
    if request.user.is_authenticated:
        return redirect("classes:index")
    # инициализируем форму
    form = LoginForm(request.POST or None, request=request)
    # если форма валидна и это POST запрос
    if request.method == "POST" and form.is_valid():
        # осуществляем вход пользователя в систему
        login(request, form.user)
        # перенаправляем пользователя на главную страницу
        return redirect("classes:index")
    # рендерим шаблон страница входа в систему
    return render(
        request,
        "accounts/login.html",
        context={
            "form": form,
        }
    )


@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    # если пользователь не аутентифицирован, перенаправляем его на страницу входа в систему
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)
    # осуществляем выход пользователя из системы
    logout(request)
    # определяем url страницы, на которую надо перенаправить пользователя
    next_url = request.POST.get("next")
    # метод url_has_allowed_host_and_scheme предназначен для защиты от открытой переадресации пользователя
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts=request.get_host(),
        require_https=request.is_secure(),
    ):
        # если url прошел проверку, то перенаправляем пользователя на указанную страницу
        return redirect(next_url)
    # иначе перенаправляем пользователя на главную страницу приложения
    return redirect("classes:index")


def signup_view(request: HttpRequest) -> HttpResponse:
    # если пользователь уже вошел в систему, перенаправляем его на главную страницу
    if request.user.is_authenticated:
        return redirect("classes:index")
    # создаем форму
    form = SignUpForm(request.POST or None)
    # проверяем, что метод запроса POST и форма валидна
    if request.method == "POST" and form.is_valid():
        # если форма валидна, то сохраняем пользователя
        user = form.save()
        # и осуществляем вход пользователя в систему
        login(request, user)
        # перенаправляем зарегистрированного пользователя на главную страницу
        return redirect("classes:index")
    return render(
        request,
        "accounts/signup.html",
        context={
            "form": form
        }
    )
