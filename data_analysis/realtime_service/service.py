import threading
import time
from data_fetcher.fetcher import DataFetcher
import logging.config
import os

# Настройка логирования
logging_config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "logging.conf")
logging.config.fileConfig(logging_config_path)
logger = logging.getLogger(__name__)

class RealTimeService:
    """
    Сервис для отслеживания данных в условно реальном времени.
    """
    def __init__(self, keywords: list[str], region: str = '', interval: int = 10):
        """
        Инициализация сервиса.

        Args:
            keywords (list[str]): Ключевые слова для отслеживания.
            region (str): Регион для анализа.
            interval (int): Интервал в секундах между обновлениями.
        """
        self.fetcher = DataFetcher(keywords, region)
        self.interval = interval
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run_service)

    def start(self) -> None:
        """
        Запускает сервис в отдельном потоке.
        """
        logger.warning("Запуск сервиса отслеживания данных.")
        self.thread.start()

    def stop(self) -> None:
        """
        Останавливает сервис.
        """
        logger.warning("Остановка сервиса отслеживания данных.")
        self._stop_event.set()
        self.thread.join()

    def _run_service(self) -> None:
        """
        Логика работы сервиса.
        """
        while not self._stop_event.is_set():
            logger.info("Получение текущих данных...")
            data = self.fetcher.fetch_current_data()
            logger.info(f"Текущие данные:\n{data}")
            time.sleep(self.interval)
