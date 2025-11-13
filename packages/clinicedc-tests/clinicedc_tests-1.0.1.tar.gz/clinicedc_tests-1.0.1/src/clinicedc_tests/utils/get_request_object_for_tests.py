from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sites.models import Site
from django.http import HttpRequest

if TYPE_CHECKING:
    from django.contrib.auth.models import User

__all__ = ["get_request_object_for_tests"]


def get_request_object_for_tests(user: User) -> HttpRequest:
    request = HttpRequest()
    request.session = "session"
    messages = FallbackStorage(request)
    request._messages = messages
    request.user = user
    request.site = Site.objects.get(id=settings.SITE_ID)
    return request
