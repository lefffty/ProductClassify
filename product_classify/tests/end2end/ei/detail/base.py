from django.urls import reverse

from ei.models import Ei

from tests.end2end.base import EndToEndTest


class EiParentDetailBaseEndToEndTest(EndToEndTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ei = Ei.objects.first()
        cls.ei_id = cls.ei.pk
        cls.url = cls.server_url + reverse("ei:detail", args=[cls.ei_id])
        cls.page.goto(cls.url)

        from tests.end2end.components.pages.ei.detail import EiDetailPage
        cls.detail_page = EiDetailPage(cls.page)


class EiChildDetailBaseEndToEndTest(EndToEndTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ei = Ei.objects.get(pk=2)
        cls.ei_id = cls.ei.pk
        cls.url = cls.server_url + reverse("ei:detail", args=[cls.ei_id])
        cls.page.goto(cls.url)

        from tests.end2end.components.pages.ei.detail import EiDetailPage
        cls.detail_page = EiDetailPage(cls.page)
