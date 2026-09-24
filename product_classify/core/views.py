from django.shortcuts import render
from django.http import HttpRequest

from http import HTTPStatus

from classes.constants import EnumsIds, ProductsConsts
from classes.models import ClassStruct


def get_context_data() -> dict:
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=ProductsConsts.FASTENER_ID
    )
    context = {}
    context["string_enums_id"] = EnumsIds.STRING
    context["image_enums_id"] = EnumsIds.IMAGE
    context["int_enums_id"] = EnumsIds.INT
    context["double_enums_id"] = EnumsIds.DOUBLE
    context["fastener_classes"] = fastener_classes
    return context


def custom_403_handler(request: HttpRequest, exception):
    context = get_context_data()
    return render(request, "pages/403.html", status=HTTPStatus.FORBIDDEN, context=context)


def custom_404_handler(request: HttpRequest, exception):
    context = get_context_data()
    return render(request, "pages/404.html", status=HTTPStatus.NOT_FOUND, context=context)


def custom_500_handler(request: HttpRequest):
    context = get_context_data()
    return render(request, "pages/500.html", status=HTTPStatus.INTERNAL_SERVER_ERROR, context=context)
