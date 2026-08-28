from django.urls import reverse

from tests.end2end.base import EndToEndTest
from tests.end2end.components.pages.ei.edit import EiEditPage

from ei.models import Ei


class EiEditEndToEndTest(EndToEndTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ei = Ei.objects.first()
        ei_pk = ei.pk
        cls.url = cls.server_url + reverse("ei:edit", args=[ei_pk])
        cls.page.goto(cls.url)
        cls.edit_page = EiEditPage(cls.page)
