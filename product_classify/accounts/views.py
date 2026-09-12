from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login
from django.shortcuts import redirect, render

from accounts.forms import LoginForm


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
