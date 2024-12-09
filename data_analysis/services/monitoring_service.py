"""
Модуль для запуска сервиса мониторинга данных в реальном времени.

Classes:
    MonitoringService: Сервис для получения и анализа данных Google Trends в параллельных потоках.

Usage:
    service = MonitoringService(keywords=["Python"], region="US")
    service.start()
    time.sleep(300)
    service.stop()
"""

import threading
import time
import logging
from typing import List, Optional
from data_retrieval.data_provider import DataProvider
from data_retrieval.analysis import TrendAnalysis

from pytrends.exceptions import TooManyRequestsError


logger = logging.getLogger("monitoring_service")


class MonitoringService:
    """
    Сервис для отслеживания изменений данных в условно реальном времени.
    Может работать в отдельном потоке, останавливаться, и запускаться
    несколько экземпляров независимо друг от друга.

    Args:
        keywords (List[str]): Список ключевых слов.
        region (str): Регион для анализа.
        timeframe (str): Период, за который будут получаться данные.
        interval (int): Интервал обновления данных в секундах.
        output_file (str): Имя файла для экспорта результатов.
        _stop_event (threading.Event): Событие для остановки потока.
        thread (Optional[threading.Thread]): Поток исполнения сервиса.
    """

    def __init__(self, 
                 keywords: List[str], 
                 region: str = '', 
                 timeframe: str = 'now 1-H', 
                 interval: int = 60, 
                 output_file: str = 'results.xlsx') -> None:
        """
        Инициализирует сервис мониторинга.

        Args:
            keywords (List[str]): Список ключевых слов.
            region (str, optional): Регион для анализа. По умолчанию '' (глобально).
            timeframe (str, optional): Временной диапазон, например 'now 1-H'. По умолчанию 'now 1-H'.
            interval (int, optional): Интервал обновления данных (секунды). По умолчанию 60.
            output_file (str, optional): Имя файла экспорта. По умолчанию 'results.xlsx'.
        """
        self.keywords = keywords
        self.region = region
        self.timeframe = timeframe
        self.interval = interval
        self.output_file = output_file
        self._stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None

    def _run(self) -> None:
        provider = DataProvider(keywords=self.keywords, region=self.region)

        while not self._stop_event.is_set():
            logger.warning(f"Запуск цикла получения и анализа данных для {self.keywords}")
            try:
                data = provider.get_data_for_period(self.timeframe)
            except TooManyRequestsError:
                logger.warning("Превышен лимит запросов к Google Trends. Ожидание перед повтором...")
                time.sleep(300)
                continue

            if not data.empty:
                analysis = TrendAnalysis(data, self.keywords[0])
                output_filename = self.output_file  # Имя файла передаётся сюда
                analysis.full_analysis(output_filename)
            else:
                logger.warning("Полученные данные пусты, пропуск анализа.")

            time.sleep(self.interval)

        logger.warning("Мониторинг сервис остановлен.")


    def start(self) -> None:
        """
        Запустить сервис в отдельном потоке.
        """
        logger.warning(f"Запуск мониторинг сервиса для {self.keywords}")
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """
        Остановить выполнение сервиса и дождаться остановки потока.
        """
        logger.warning(f"Остановка мониторинг сервиса для {self.keywords}")
        self._stop_event.set()
        if self.thread is not None:
            self.thread.join()
        logger.warning("Мониторинг сервис остановлен окончательно.")
