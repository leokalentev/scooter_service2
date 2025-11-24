from scooter_module import ScooterFactory
from station_module import RentalStation, Location
from system_module import RentalSystem


def main():
    # Инициализация системы
    system = RentalSystem()

    # Создание станций
    location1 = Location("ул. Ленина, 10", 55.7558, 37.6173)
    station1 = RentalStation("ST001", location1, capacity=5)
    system.add_station(station1)

    location2 = Location("пр. Мира, 25", 55.7512, 37.6180)
    station2 = RentalStation("ST002", location2, capacity=3)
    system.add_station(station2)

    # Создание самокатов через фабрику
    factory = ScooterFactory()

    scooter1 = factory.create_scooter(
        "city", "SC001", "Xiaomi Mi Electric Scooter Pro", 95.0, 150, max_speed=25.0
    )
    scooter2 = factory.create_scooter(
        "off_road", "SC002", "Segway Dirt eS2", 80.0, 200, tire_type="Knobby"
    )
    scooter3 = factory.create_scooter(
        "foldable", "SC003", "Ninebot ES2", 100.0, 120, weight=12.5
    )

    # Добавление самокатов на станции
    station1.add_scooter(scooter1)
    station1.add_scooter(scooter2)
    station2.add_scooter(scooter3)

    # Регистрация клиентов
    system.register_client("CL001", "Иван Петров", "+79991234567")
    system.register_client("CL002", "Мария Сидорова", "+79997654321")

    # Создание аренды
    system.add_rental("RT001", "CL001", "ST001", "SC001", 2.5)
    system.add_rental("RT002", "CL002", "ST002", "SC003", 1.0)

    # Изменение аренды (цепочка обязанностей)
    print("\n=== ИЗМЕНЕНИЕ АРЕНДЫ ===")
    system.process_rental_change("RT001", 5.0)  # Требует одобрения менеджера

    # Генерация отчетов
    print("\n=== ОТЧЕТ ПО СТАНЦИИ ST001 ===")
    print(station1.generate_report())

    print("\n=== ОБЩИЙ ОТЧЕТ СИСТЕМЫ ===")
    print(system.generate_system_report())


if __name__ == "__main__":
    main()