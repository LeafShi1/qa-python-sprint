
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=250)
        yield browser
        browser.close()

def test_login_success(browser):
    page = browser.new_page()
    page.goto("https://e-cology.beyondsoft.com/wui/index.html?v=1767694603085#/?_key=lb4c1i")
    page.fill("#loginid", "shiyuanyuan")
    page.fill("#userpassword", "General1289!")
    page.click("button#submit")
    assert page.inner_text("title") == "Beyondsoft E-cology"
