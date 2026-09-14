from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpRequest
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from functools import wraps


def roles_required(*role_names, raise_exception=True):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request: HttpRequest, *args, **kwargs):
            user = request.user
            if user.groups.filter(role__code__in=role_names).exists():
                return view(request, *args, **kwargs)
            if raise_exception:
                raise PermissionDenied
            return redirect(settings.LOGIN_URL)
        return wrapper
    return decorator
