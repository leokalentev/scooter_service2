from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from scooter_module import Scooter
from station_module import RentalStation, Location


class Handler(ABC):
    """Абстрактный обработчик для цепочки обязанностей"""

    _next_handler: Optional['Handler'] = None

    def set_next(self, handler: 'Handler') -> 'Handler':
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request: dict) -> bool:
        pass


class OperatorHandler(Handler):
    """Обработчик для оператора станции"""

    def handle(self, request: dict) -> bool:
        # Одобряет изменения при длительности аренды < 4 часов
        if request['hours'] < 4:
            print(f"Оператор одобрил изменение аренды: {request['rental_id']}")
            return True
        if self._next_handler:
            return self._next_handler.handle(request)
        return False


class ManagerHandler(Handler):
    """Обработчик для менеджера"""

    def handle(self, request: dict) -> bool:
        # Одобряет изменения со стоимостью до 1000 руб.
        scooter = request['scooter']
        cost = scooter.calculate_rental_cost(request['hours'])
        if cost <= 1000:
            print(f"Менеджер одобрил изменение аренды: {request['rental_id']} (стоимость: {cost:.2f} руб.)")
            return True
        if self._next_handler:
            return self._next_handler.handle(request)
        return False


class AdminHandler(Handler):
    """Обработчик для администратора"""

    def handle(self, request: dict) -> bool:
        # Одобряет любые изменения
        print(f"Администратор одобрил изменение аренды: {request['rental_id']}")
        return True


class RentalSystem:
    """Основная система управления арендой"""

    def __init__(self):
        self.stations: Dict[str, RentalStation] = {}
        self.clients: Dict[str, dict] = {}
        self.rentals: Dict[str, dict] = {}
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Настройка цепочки обязанностей"""
        self._change_handler = OperatorHandler()
        self._change_handler.set_next(ManagerHandler()).set_next(AdminHandler())

    def add_station(self, station: RentalStation) -> None:
        """Добавление станции в систему"""
        if station.station_id in self.stations:
            raise ValueError(f"Станция {station.station_id} уже существует")
        self.stations[station.station_id] = station

    def register_client(self, client_id: str, name: str, phone: str) -> None:
        """Регистрация клиента"""
        if client_id in self.clients:
            raise ValueError(f"Клиент {client_id} уже зарегистрирован")
        self.clients[client_id] = {"name": name, "phone": phone}

    def process_rental_change(self, rental_id: str, new_hours: float) -> bool:
        """Обработка запроса на изменение аренды"""
        if rental_id not in self.rentals:
            raise ValueError(f"Аренда {rental_id} не найдена")

        rental = self.rentals[rental_id]
        station_id = rental['station_id']

        if station_id not in self.stations:
            raise ValueError(f"Станция {station_id} не найдена")

        station = self.stations[station_id]
        scooter = None
        for s in station.scooters:
            if s.scooter_id == rental['scooter_id']:
                scooter = s
                break

        if not scooter:
            raise ValueError(f"Самокат {rental['scooter_id']} не найден на станции {station_id}")

        request = {
            'rental_id': rental_id,
            'hours': new_hours,
            'scooter': scooter,
            'client_id': rental['client_id']
        }

        approved = self._change_handler.handle(request)
        if approved:
            rental['hours'] = new_hours
            rental['cost'] = scooter.calculate_rental_cost(new_hours)
            print(f"Аренда {rental_id} успешно изменена: {new_hours} часов, стоимость {rental['cost']:.2f} руб.")
        return approved

    def generate_system_report(self) -> str:
        """Генерация общего отчета по системе"""
        report = "===== ОБЩИЙ ОТЧЕТ СИСТЕМЫ =====\n"
        report += f"Всего станций: {len(self.stations)}\n"
        report += f"Всего клиентов: {len(self.clients)}\n"
        report += f"Активных аренд: {len(self.rentals)}\n\n"

        for station_id, station in self.stations.items():
            report += station.generate_report() + "\n"

        return report

    def add_rental(self, rental_id: str, client_id: str, station_id: str, scooter_id: str, hours: float) -> None:
        """Добавление записи об аренде"""
        if station_id not in self.stations:
            raise ValueError(f"Станция {station_id} не найдена")

        station = self.stations[station_id]
        scooter = None
        for s in station.scooters:
            if s.scooter_id == scooter_id:
                scooter = s
                break

        if not scooter:
            raise ValueError(f"Самокат {scooter_id} не найден на станции {station_id}")

        if not scooter.is_available:
            raise ValueError(f"Самокат {scooter_id} недоступен для аренды")

        cost = station.rent_scooter(scooter_id, hours)
        self.rentals[rental_id] = {
            'client_id': client_id,
            'station_id': station_id,
            'scooter_id': scooter_id,
            'hours': hours,
            'cost': cost
        }