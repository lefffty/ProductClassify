from playwright.sync_api import Page, expect

from tests.end2end.components.pages.base import BasePage


class ProductsListPage(BasePage):
    def __init__(self, page: Page):
        self._page = page

    def check_url_is_correct(self, url):
        expect(self._page).to_have_url(url)
