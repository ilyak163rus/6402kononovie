"""
Главный модуль запуска сервиса мониторинга данных Google Trends.

Этот модуль:
- Создаёт два потока для анализа ключевых слов "Python" и "Java".
- Управляет их запуском и корректным завершением.
- Логирует действия и события выполнения.

Classes:
    None

Functions:
    main(): Основная функция для запуска сервисов мониторинга.

Usage:
    Запуск программы: python main.py
"""
import logging.config
import os
import time
from services.monitoring_service import MonitoringService

def main():
    """
    Главная функция для запуска двух потоков мониторинга данных.

    - Один поток анализирует ключевое слово "Python".
    - Второй поток анализирует ключевое слово "Java".

    Потоки работают параллельно и сохраняют результаты в отдельные файлы Excel.

    Raises:
        KeyboardInterrupt: Прерывание выполнения пользователем.
    """
    # Путь к конфигурации логирования
    config_path = os.path.join(os.path.dirname(__file__), 'configs', 'logging.conf')
    logging.config.fileConfig(config_path)

    # Логгер для главного модуля
    logger = logging.getLogger("main")

    # Создаём два сервиса мониторинга
    logger.warning("Создание сервиса мониторинга для ключевого слова 'Python'")
    service_python = MonitoringService(
        keywords=["Python"], 
        region="US", 
        timeframe="now 1-H", 
        interval=60, 
        output_file="results_python.xlsx"
    )

    logger.warning("Создание сервиса мониторинга для ключевого слова 'Java'")
    service_java = MonitoringService(
        keywords=["Java"], 
        region="US", 
        timeframe="now 1-H", 
        interval=60, 
        output_file="results_java.xlsx"
    )

    # Запускаем оба сервиса
    logger.warning("Запуск сервиса мониторинга для 'Python'")
    service_python.start()
    
    logger.warning("Запуск сервиса мониторинга для 'Java'")
    service_java.start()

    try:
        # Даем потокам работать некоторое время (например, 5 минут)
        time.sleep(300)
    except KeyboardInterrupt:
        logger.warning("Получен сигнал прерывания. Остановка всех сервисов...")
    finally:
        # Останавливаем оба сервиса корректно
        logger.warning("Остановка сервиса для 'Python'")
        service_python.stop()
        
        logger.warning("Остановка сервиса для 'Java'")
        service_java.stop()

    logger.warning("Все сервисы завершены.")

if __name__ == "__main__":
    main()
