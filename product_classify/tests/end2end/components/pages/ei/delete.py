from playwright.sync_api import Page, expect

from tests.end2end.components.pages.base import BasePage


class EiDeletePage(BasePage):
    def __init__(self, page: Page):
        self._page = page

        self.delete_alert = page.locator("#ei-delete-alert")
        self.delete_warning = page.locator("#ei-delete-warning")
        self.delete_hint = page.locator("#ei-delete-hint")
        self.delete_info = page.locator("#ei-delete-info")
        self.delete_id = page.locator("#ei-delete-id")
        self.delete_name = page.locator("#ei-delete-name")
        self.delete_short = page.locator("#ei-delete-short")
        self.delete_code = page.locator("#ei-delete-code")
        self.delete_factor = page.locator("#ei-delete-factor")
        self.delete_parent = page.locator("#ei-delete-parent")

    def check_url_is_correct(self, url):
        expect(self._page).to_have_url(url)
