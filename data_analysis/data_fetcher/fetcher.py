import pandas as pd
from pytrends.request import TrendReq
import logging.config
import os
from datetime import datetime

# Настройка логирования
logging_config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "logging.conf")
logging.config.fileConfig(logging_config_path)
logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Модуль для получения данных из Google Trends.
    """
    def __init__(self, keywords: list[str], region: str = ''):
        """
        Инициализация fetcher для получения данных.

        Args:
            keywords (list[str]): Список ключевых слов для запроса.
            region (str): Регион анализа.
        """
        self.keywords = keywords
        self.region = region
        self.pytrends = TrendReq()
        self.data = pd.DataFrame()

    def fetch_historical_data(self, timeframe: str) -> pd.DataFrame:
        """
        Получает данные за определенный временной промежуток.

        Args:
            timeframe (str): Временной диапазон запроса (например, 'today 1-m').

        Returns:
            pd.DataFrame: Данные о трендах.
        """
        try:
            self.pytrends.build_payload(self.keywords, timeframe=timeframe, geo=self.region)
            data = self.pytrends.interest_over_time()
            logger.info("Данные успешно получены.")
            return data.drop(columns=["isPartial"], errors="ignore")
        except Exception as e:
            logger.warning(f"Ошибка при получении данных: {e}")
            return pd.DataFrame()

    def fetch_current_data(self) -> pd.DataFrame:
        """
        Получает текущие данные по запросу.

        Returns:
            pd.DataFrame: Текущие данные.
        """
        return self.fetch_historical_data(timeframe="now 1-d")
