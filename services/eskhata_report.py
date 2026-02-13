import logging

from config import ESKHATA_PIC_PATH
from currency_eskhata import EskhataScreenshot


class EskhataReportService:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def build(self) -> tuple[str, str]:
        runner = EskhataScreenshot(
            visible=False,
            out_path=str(ESKHATA_PIC_PATH),
            window_size=(780, 720),
        )
        result_path = runner.run()
        self.logger.info(
            "Eskhata screenshot generated",
            extra={"event": "eskhata_screenshot_generated", "path": result_path},
        )
        return str(ESKHATA_PIC_PATH), "Курс по эсхата"
