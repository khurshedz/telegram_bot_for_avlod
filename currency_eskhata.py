from config import ESKHATA_PIC_PATH
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class EskhataScreenshot:
    def __init__(
        self,
        visible=True,
        timeout=15,
        out_path="",
        window_size=(890, 750),
    ):
        self.url = "https://eskhata.com/"
        self.tab_text = "Денежные переводы"
        self.timeout = timeout
        self.out_path = Path(out_path)
        self.window_size = window_size

        opts = webdriver.ChromeOptions()
        if not visible:
            opts.add_argument("--headless=new")
        opts.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        opts.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(options=opts)

    def _wait_page_loaded(self):
        WebDriverWait(self.driver, self.timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def _find_tab(self):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[contains(text(), '{self.tab_text}')]")
            )
        )

    def _scroll_to_element(self, element):
        self.driver.execute_script(
            """
            const element = arguments[0];
            const headerOffset = 120;
            const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
            const offsetPosition = elementPosition - headerOffset;
            window.scrollTo({top: offsetPosition, behavior: 'instant'});
            """,
            element,
        )
        WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of(element)
        )

    def _click(self, element):
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(element)
            )
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)

    def _close_popups(self):
        try:
            btn = self.driver.find_element(By.CSS_SELECTOR, ".popup-close, .modal-close")
            btn.click()
        except Exception:
            pass

    def run(self):
        try:
            self.driver.get(self.url)
            self._wait_page_loaded()
            self._close_popups()

            tab = self._find_tab()
            self._scroll_to_element(tab)
            self._click(tab)

            WebDriverWait(self.driver, self.timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            self.out_path.parent.mkdir(parents=True, exist_ok=True)
            self.driver.save_screenshot(str(self.out_path))
            return str(self.out_path.resolve())
        finally:
            self.driver.quit()


if __name__ == "__main__":
    runner = EskhataScreenshot(visible=True,
                               out_path=ESKHATA_PIC_PATH,
                               window_size=(780, 720),
                               )
    print(runner.run())
