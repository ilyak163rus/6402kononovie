from realtime_service.service import RealTimeService

if __name__ == "__main__":
    # Запуск нескольких сервисов
    service1 = RealTimeService(["python"], region="", interval=5)
    service2 = RealTimeService(["java"], region="US", interval=7)

    try:
        service1.start()
        service2.start()
        input("Сервисы запущены. Нажмите Enter для остановки.\n")
    finally:
        service1.stop()
        service2.stop()
