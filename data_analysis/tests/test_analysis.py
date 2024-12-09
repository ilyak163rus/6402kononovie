import unittest
import pandas as pd
import numpy as np
from search_trend_analysis.analysis import SearchTrendAnalysis

class TestSearchTrendAnalysis(unittest.TestCase):
    '''
    Класс для тестирования методов класса SearchTrendAnalysis.
    '''

    def setUp(self):
        '''
        Инициализация перед каждым тестом.
        Создает тестовые данные и экземпляр класса SearchTrendAnalysis.
        '''
        self.test_data = pd.DataFrame({
            'Python': [1, 2, 3, 5, 6, 7, 6, 5, 4, 3, 2, 1] * 22
        })
        self.analysis = SearchTrendAnalysis(keywords=['Python'])
        self.analysis.data = self.test_data

    def test_moving_average(self):
        '''
        Тест метода скользящего среднего.
        
        Проверяет:
            - Корректность количества строк в результате.
            - Правильность вычисления скользящего среднего.
        '''
        self.analysis.moving_average(window=3)
        expected_ma = self.test_data['Python'].rolling(window=3).mean()
        expected_ma.name = 'moving_avg'

        self.assertEqual(len(self.analysis.results['moving_avg']), len(self.test_data))
        pd.testing.assert_series_equal(self.analysis.results['moving_avg'], expected_ma)

    def test_differentiation(self):
        '''
        Тест метода дифференцирования.
        
        Проверяет:
            - Корректность количества строк в результате.
            - Правильность вычисления разностей временного ряда.
        '''
        self.analysis.differentiate()
        expected_diff = self.test_data['Python'].diff()
        expected_diff.name = 'difference'

        self.assertEqual(len(self.analysis.results['difference']), len(self.test_data))
        pd.testing.assert_series_equal(self.analysis.results['difference'], expected_diff)

    def test_autocorrelation(self):
        '''
        Тест метода автокорреляции.
        
        Проверяет:
            - Наличие столбца автокорреляции.
            - Наличие значений автокорреляции после 40-го шага.
        '''
        self.analysis.autocorrelation()

        self.assertIn('autocorrelation', self.analysis.results.columns)
        autocorr_values = self.analysis.results['autocorrelation'].iloc[40:]
        self.assertTrue(autocorr_values.notnull().all())

    def test_find_extrema(self):
        '''
        Тест метода нахождения экстремумов.
        
        Проверяет:
            - Наличие столбца с пиками.
            - Корректность заполнения столбца экстремумов.
        '''
        self.analysis.find_extrema()

        self.assertIn('peaks', self.analysis.results.columns)
        self.assertTrue(self.analysis.results['peaks'].isnull().sum() < len(self.analysis.results))

    def test_export_to_excel(self):
        '''
        Тест метода экспорта результатов в Excel.
        
        Проверяет:
            - Создание файла с результатами.
            - Удаление созданного файла после проверки.
        '''
        filename = 'test_results.xlsx'
        self.analysis.export_to_excel(filename=filename)

        import os
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)

if __name__ == '__main__':
    unittest.main()
