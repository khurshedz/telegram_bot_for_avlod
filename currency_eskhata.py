import sys
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EskhataScreenshot:
    def __init__(self, visible=True, timeout=10, slowmo=0.1, out_path="eskhata_transfers.png", window_size=(1400, 2200)):
        self.url = "https://eskhata.com/"
        self.tab_text = "Денежные переводы"
        self.timeout = timeout
        self.slowmo = slowmo
        self.out_path = Path(out_path)
        self.window_size = window_size
        opts = webdriver.ChromeOptions()
        if not visible:
            opts.add_argument("--headless=new")
        opts.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        self.driver = webdriver.Chrome(options=opts)

    def log(self, msg):
        print(msg, flush=True)

    def _find_transfers_tab(self):
        try:
            return self.driver.find_element(By.XPATH, f"//*[contains(text(), '{self.tab_text}')]")
        except Exception:
            return None

    def run(self):
        try:
            self.log("→ Открываю сайт")
            self.driver.get(self.url)
            time.sleep(2)  # Ждём 2 секунды, не дожидаясь полной загрузки

            self.log(f"→ Ищу вкладку: {self.tab_text}")
            tab = self._find_transfers_tab()
            if not tab:
                raise RuntimeError("Не нашёл вкладку по тексту")

            self.log("→ Прокручиваю к вкладке")
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tab)
            time.sleep(self.slowmo)

            self.log("→ Кликаю вкладку")
            tab.click()
            time.sleep(self.slowmo)

            self.log(f"→ Делаю скриншот: {self.out_path}")
            self.driver.save_screenshot(str(self.out_path))

            self.log(f"✔ Готово: {self.out_path.resolve()}")
            return str(self.out_path.resolve())
        finally:
            self.log("→ Закрываю браузер")
            self.driver.quit()

if __name__ == "__main__":
    runner = EskhataScreenshot(visible=True, timeout=10, slowmo=0.1, out_path="eskhata_transfers.png", window_size=(1400, 2200))
    runner.run()
