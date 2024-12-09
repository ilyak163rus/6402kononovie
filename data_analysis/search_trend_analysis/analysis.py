'''
Модуль класса для выполнения анализа трендов поисковых запросов
с использованием Google Trends.
'''
import pandas as pd
import numpy as np
from pytrends.request import TrendReq
from scipy.signal import find_peaks
from statsmodels.tsa.stattools import acf
import time
import logging


def log_execution(func):
    '''
    Декоратор для логирования выполнения функции.

    Args:
        func: функция, выполнение которой необходимо логировать.

    Returns:
        wrapper: обертка для функции с логированием начала и окончания выполнения.
    '''
    def wrapper(*args, **kwargs):
        logging.info(f"Выполнение {func.__name__} с аргументами {args}, {kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__} завершена")
        return result
    return wrapper


def timing(func):
    '''
    Декоратор для измерения времени выполнения функции.

    Args:
        func: функция, для которой необходимо измерить время выполнения.

    Returns:
        wrapper: обертка для функции с замером времени выполнения.
    '''
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} выполнена за {end_time - start_time:.4f} секунд")
        return result
    return wrapper


def find_peaks_generator(data: np.ndarray, height: float = None, distance: int = 1):
    '''
    Генератор для нахождения экстремумов в данных.

    Args:
        data: массив данных, в котором нужно найти экстремумы.
        height: минимальная высота пиков (по умолчанию None).
        distance: минимальное расстояние между пиками (по умолчанию 1).

    Yields:
        tuple: индекс пика и его высота (если высота указана).
    '''
    peaks, properties = find_peaks(data, height=height, distance=distance)
    
    if 'peak_heights' in properties:
        for peak in peaks:
            yield peak, properties['peak_heights'][peak]
    else:
        for peak in peaks:
            yield peak, data[peak]


class SearchTrendAnalysis:
    '''
    Класс для выполнения анализа трендов поисковых запросов
    с использованием Google Trends.
    '''

    def __init__(self, keywords: list, timeframe: str = 'today 5-y', region: str = ''):
        '''
        Инициализация объекта анализа поисковых трендов.

        Args:
            keywords: список ключевых слов для анализа.
            timeframe: период времени для анализа (по умолчанию 'today 5-y').
            region: регион для анализа (по умолчанию - пустая строка, что означает глобальный анализ).
        '''
        self.keywords = keywords
        self.timeframe = timeframe
        self.region = region
        self.pytrends = TrendReq()
        self.data = None
        self.results = pd.DataFrame()

    @log_execution
    @timing
    def fetch_data(self):
        '''
        Получение данных трендов поиска с Google Trends.

        Returns:
            None
        '''
        self.pytrends.build_payload(self.keywords, timeframe=self.timeframe, geo=self.region)
        self.data = self.pytrends.interest_over_time()
        if 'isPartial' in self.data.columns:
            self.data = self.data.drop(columns=['isPartial'])

    @log_execution
    @timing
    def moving_average(self, window: int = 3):
        '''
        Вычисление скользящего среднего.

        Args:
            window: размер окна для вычисления среднего (по умолчанию 3).

        Returns:
            None
        '''
        self.results['moving_avg'] = self.data[self.keywords[0]].rolling(window=window).mean()

    @log_execution
    @timing
    def differentiate(self):
        '''
        Вычисление разностей временного ряда.

        Returns:
            None
        '''
        self.results['difference'] = self.data[self.keywords[0]].diff()

    @log_execution
    @timing
    def autocorrelation(self):
        '''
        Вычисление автокорреляции временного ряда.

        Returns:
            None
        '''
        series = self.data[self.keywords[0]].dropna()
        max_lag = 40

        if len(series) > max_lag:
            acf_values = acf(series, nlags=len(series) - 1)
            autocorr_full = pd.Series(np.nan, index=self.results.index)

            autocorr_values_length = min(len(acf_values), max(0, len(autocorr_full) - max_lag))

            if autocorr_values_length > 0:
                autocorr_full.iloc[max_lag:max_lag + autocorr_values_length] = acf_values[:autocorr_values_length]

            self.results['autocorrelation'] = autocorr_full
        else:
            self.results['autocorrelation'] = pd.Series(np.nan, index=self.results.index)

    @log_execution
    @timing
    def find_extrema(self):
        '''
        Нахождение локальных максимумов и минимумов во временном ряде.

        Returns:
            None
        '''
        data_series = self.data[self.keywords[0]].dropna().values
        extrema_gen = find_peaks_generator(data_series, height=None, distance=1)
        
        peaks_column = np.full_like(data_series, np.nan, dtype=np.float64)
        
        for peak, height in extrema_gen:
            peaks_column[peak] = height

        peaks_series = pd.Series(peaks_column, index=self.data.dropna().index)
        self.results['peaks'] = peaks_series.reindex(self.data.index, fill_value=np.nan)

    @log_execution
    @timing
    def export_to_excel(self, filename: str = 'results.xlsx'):
        '''
        Экспортирование результатов анализа в Excel файл.

        Args:
            filename: имя файла для экспорта (по умолчанию 'results.xlsx').

        Returns:
            None
        '''
        self.results.to_excel(filename, index=True)

    @log_execution
    @timing
    def analyze(self):
        '''
        Полный анализ данных, включающий получение данных,
        вычисление скользящего среднего, разностей, экстремумов и автокорреляции.

        Returns:
            None
        '''
        self.fetch_data()
        self.moving_average()
        self.differentiate()
        self.find_extrema()
        self.autocorrelation()
        self.export_to_excel()
