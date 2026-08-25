import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from playwright.sync_api import sync_playwright


class EndToEndTest(StaticLiveServerTestCase):
    fixtures = [
        "ei.json",
        "classes.json",
    ]

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.server_url = cls.live_server_url
        cls.p = sync_playwright().start()
        cls.browser = cls.p.chromium.launch(headless=False)
        cls.page = cls.browser.new_page()

    @classmethod
    def tearDownClass(cls):
        cls.page.close()
        cls.browser.close()
        cls.p.stop()
