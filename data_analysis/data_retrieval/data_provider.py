"""
Модуль для получения данных Google Trends.

Classes:
    DataProvider: Класс для загрузки данных о поисковых трендах по ключевым словам.

Usage:
    provider = DataProvider(keywords=["Python"], region="US")
    data = provider.get_data_for_period(timeframe="today 5-y")
"""
import logging
from pytrends.request import TrendReq
import pandas as pd
from typing import List

logger = logging.getLogger("data_retrieval")


class DataProvider:
    """
    Класс для получения данных из Google Trends по ключевым словам.

    Attributes:
        keywords (List[str]): Список ключевых слов.
        region (str): Регион для анализа (например, 'US').
        pytrends (TrendReq): Объект для работы с Google Trends API.
    """

    def __init__(self, keywords: List[str], region: str = '') -> None:
        """
        Инициализация провайдера данных.

        Args:
            keywords (List[str]): Список ключевых слов для анализа.
            region (str, optional): Регион поиска. По умолчанию '' (глобальный поиск).
        """
        self.keywords = keywords
        self.region = region
        self.pytrends = TrendReq()

    def get_data_for_period(self, timeframe: str = 'today 5-y') -> pd.DataFrame:
        """
        Получает данные за указанный период времени.

        Args:
            timeframe (str, optional): Период времени для анализа. По умолчанию 'today 5-y'.

        Returns:
            pd.DataFrame: Данные о трендах поиска.
        """
        logger.warning(f"Получение данных для {self.keywords} за период {timeframe}")
        self.pytrends.build_payload(self.keywords, timeframe=timeframe, geo=self.region)
        data = self.pytrends.interest_over_time()
        if 'isPartial' in data.columns:
            data = data.drop(columns=['isPartial'])
        return data

    def get_data_current(self) -> pd.DataFrame:
        """
        Получает текущие данные за последний час.

        Returns:
            pd.DataFrame: Данные о трендах за текущий момент.
        """
        logger.warning(f"Получение текущих данных для {self.keywords}")
        self.pytrends.build_payload(self.keywords, timeframe='now 1-H', geo=self.region)
        data = self.pytrends.interest_over_time()
        if 'isPartial' in data.columns:
            data = data.drop(columns=['isPartial'])
        return data
