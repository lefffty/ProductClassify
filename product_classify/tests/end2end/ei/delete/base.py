from django.urls import reverse

from tests.end2end.base import EndToEndTest
from tests.end2end.components.pages.ei.delete import EiDeletePage

from ei.models import Ei


class EiDeleteBaseEndToEndTest(EndToEndTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ei = Ei.objects.first()
        cls.url = cls.server_url + reverse("ei:delete", args=[cls.ei.pk])
        cls.page.goto(cls.url)
        cls.delete_page = EiDeletePage(cls.page)
