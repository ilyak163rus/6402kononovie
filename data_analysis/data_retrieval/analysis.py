"""
Модуль для анализа временных рядов данных Google Trends.

Classes:
    TrendAnalysis: Класс для выполнения анализа данных (скользящее среднее, разности, экстремумы, автокорреляция).

Functions:
    log_execution(func): Декоратор для логирования выполнения функций.
    timing(func): Декоратор для измерения времени выполнения функций.
    find_peaks_generator(data): Генератор для поиска экстремумов.
"""

import time
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from statsmodels.tsa.stattools import acf
import logging
from typing import Callable, Any, Iterator, Tuple
from functools import wraps

logger = logging.getLogger("analysis")


def log_execution(func: Callable) -> Callable:
    """
    Декоратор для логирования выполнения функции.

    Args:
        func (Callable): Функция, выполнение которой необходимо логировать.

    Returns:
        Callable: Обертка для функции с логированием.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger.warning(f"Выполнение {func.__name__} с аргументами {args}, {kwargs}")
        result = func(*args, **kwargs)
        logger.warning(f"{func.__name__} завершена")
        return result
    return wrapper


def timing(func: Callable) -> Callable:
    """
    Декоратор для измерения времени выполнения функции.

    Args:
        func (Callable): Функция, время выполнения которой необходимо измерить.

    Returns:
        Callable: Обертка для функции с замером времени.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.warning(f"{func.__name__} выполнена за {end_time - start_time:.4f} секунд")
        return result
    return wrapper


def find_peaks_generator(data: np.ndarray, height: float = None, distance: int = 1) -> Iterator[Tuple[int, float]]:
    """
    Генератор для нахождения экстремумов в данных.

    Args:
        data (np.ndarray): Массив числовых данных.
        height (float, optional): Минимальная высота пиков. По умолчанию None.
        distance (int, optional): Минимальное расстояние между пиками. По умолчанию 1.

    Yields:
        Iterator[Tuple[int, float]]: Индекс пика и его высота.
    """
    peaks, properties = find_peaks(data, height=height, distance=distance)
    if 'peak_heights' in properties:
        for peak in peaks:
            yield peak, properties['peak_heights'][peak]
    else:
        for peak in peaks:
            yield peak, data[peak]


class TrendAnalysis:
    """
    Класс для выполнения анализа данных поисковых трендов.

    Атрибуты:
        data (pd.DataFrame): Данные трендов.
        keyword (str): Ключевое слово, для которого выполняется анализ.
        results (pd.DataFrame): Результаты анализа.
    """

    def __init__(self, data: pd.DataFrame, keyword: str) -> None:
        """
        Инициализирует объект анализа трендов.

        Args:
            data (pd.DataFrame): Данные трендов (столбец с интересом по времени).
            keyword (str): Ключевое слово для анализа.
        """
        self.data = data
        self.keyword = keyword
        self.results = pd.DataFrame(index=data.index)

    @log_execution
    @timing
    def moving_average(self, window: int = 3) -> None:
        """
        Рассчитать скользящее среднее по указанному окну.

        Args:
            window (int, optional): Размер окна. По умолчанию 3.
        """
        self.results['moving_avg'] = self.data[self.keyword].rolling(window=window).mean()

    @log_execution
    @timing
    def differentiate(self) -> None:
        """
        Вычислить разности временного ряда.
        """
        self.results['difference'] = self.data[self.keyword].diff()

    @log_execution
    @timing
    def find_extrema(self) -> None:
        """
        Найти локальные максимумы (пики) во временном ряде.
        """
        data_series = self.data[self.keyword].dropna().values
        extrema_gen = find_peaks_generator(data_series, height=None, distance=1)
        peaks_column = np.full_like(data_series, np.nan, dtype=np.float64)
        for peak, height in extrema_gen:
            peaks_column[peak] = height
        peaks_series = pd.Series(peaks_column, index=self.data.dropna().index)
        self.results['peaks'] = peaks_series.reindex(self.data.index, fill_value=np.nan)

    @log_execution
    @timing
    def autocorrelation(self) -> None:
        """
        Вычислить автокорреляцию временного ряда.
        """
        series = self.data[self.keyword].dropna()
        max_lag = 7
        if len(series) > max_lag:
            acf_values = acf(series, nlags=len(series)-1)
            autocorr_full = pd.Series(np.nan, index=self.results.index)
            autocorr_values_length = min(len(acf_values), max(0, len(autocorr_full) - max_lag))
            if autocorr_values_length > 0:
                autocorr_full.iloc[max_lag:max_lag+autocorr_values_length] = acf_values[:autocorr_values_length]
            self.results['autocorrelation'] = autocorr_full
        else:
            self.results['autocorrelation'] = pd.Series(np.nan, index=self.results.index)

    @log_execution
    @timing
    def export_to_excel(self, filename: str = 'results.xlsx') -> None:
        """
        Экспортировать результаты анализа в Excel-файл.

        Args:
            filename (str, optional): Имя файла. По умолчанию 'results.xlsx'.
        """
        self.results.to_excel(filename, index=True)

    @log_execution
    @timing
    def full_analysis(self, output_filename) -> None:
        """
        Выполнить полный анализ данных: скользящее среднее, разности, экстремумы, автокорреляция и экспорт.
        """
        self.moving_average()
        self.differentiate()
        self.find_extrema()
        self.autocorrelation()
        self.export_to_excel(output_filename)
