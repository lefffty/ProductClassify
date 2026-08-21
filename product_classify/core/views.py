from django.shortcuts import render
from django.http import HttpRequest

from http import HTTPStatus


def custom_404_handler(request: HttpRequest, exception):
    return render(
        request,
        "pages/404.html",
        status=HTTPStatus.NOT_FOUND
    )


def custom_500_handler(request: HttpRequest):
    return render(
        request,
        "pages/500.html",
        status=HTTPStatus.INTERNAL_SERVER_ERROR
    )
