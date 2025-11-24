from abc import ABC, abstractmethod
from typing import List, Optional
from scooter_module import Scooter


class Location:
    """Класс для хранения информации о местоположении"""

    def __init__(self, address: str, latitude: float, longitude: float):
        self._address = address
        self._latitude = latitude
        self._longitude = longitude

    @property
    def address(self) -> str:
        return self._address

    @property
    def coordinates(self) -> tuple[float, float]:
        return (self._latitude, self._longitude)

    def __str__(self) -> str:
        return f"{self.address} ({self._latitude}, {self._longitude})"


class Rentable(ABC):
    """Интерфейс для аренды"""

    @abstractmethod
    def rent_scooter(self, scooter_id: str, hours: float) -> float:
        pass


class Reportable(ABC):
    """Интерфейс для генерации отчетов"""

    @abstractmethod
    def generate_report(self) -> str:
        pass


class LoggingMixin:
    """Миксин для логирования действий"""

    def log_action(self, action: str) -> None:
        print(f"[LOG] {action}")


class NotificationMixin:
    """Миксин для отправки уведомлений"""

    def send_notification(self, message: str) -> None:
        print(f"[УВЕДОМЛЕНИЕ] {message}")


class RentalStation(LoggingMixin, NotificationMixin, Rentable, Reportable):
    """Класс станции аренды с композицией и агрегацией"""

    def __init__(self, station_id: str, location: Location, capacity: int):
        self._station_id = station_id
        self._location = location  # Композиция
        self._capacity = capacity
        self._scooters: List[Scooter] = []  # Агрегация

    @property
    def station_id(self) -> str:
        return self._station_id

    @property
    def location(self) -> Location:
        return self._location

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def scooters(self) -> List[Scooter]:
        return self._scooters

    def add_scooter(self, scooter: Scooter) -> None:
        """Добавление самоката на станцию"""
        if len(self._scooters) >= self._capacity:
            raise ValueError(f"Станция {self.station_id} переполнена (вместимость: {self.capacity})")
        if any(s.scooter_id == scooter.scooter_id for s in self._scooters):
            raise ValueError(f"Самокат {scooter.scooter_id} уже на станции")

        self._scooters.append(scooter)
        self.log_action(f"Самокат {scooter.model} добавлен на станцию {self.station_id}")
        self.send_notification(f"Самокат {scooter.model} готов к аренде на станции {self.station_id}")

    def remove_scooter(self, scooter_id: str) -> Scooter:
        """Удаление самоката со станции"""
        for scooter in self._scooters:
            if scooter.scooter_id == scooter_id:
                self._scooters.remove(scooter)
                self.log_action(f"Самокат {scooter.model} удален со станции {self.station_id}")
                return scooter
        raise ValueError(f"Самокат {scooter_id} не найден на станции")

    def get_available_scooters(self) -> List[Scooter]:
        """Получение списка доступных самокатов"""
        return [s for s in self._scooters if s.is_available]

    def rent_scooter(self, scooter_id: str, hours: float) -> float:
        """Аренда самоката"""
        for scooter in self._scooters:
            if scooter.scooter_id == scooter_id:
                if not scooter.is_available:
                    raise ValueError(f"Самокат {scooter_id} недоступен для аренды")
                scooter.is_available = False
                cost = scooter.calculate_rental_cost(hours)
                self.log_action(f"Аренда самоката {scooter.model} на {hours} часов. Стоимость: {cost:.2f}")
                self.send_notification(f"Аренда подтверждена! Самокат: {scooter.model}, Стоимость: {cost:.2f} руб.")
                return cost
        raise ValueError(f"Самокат {scooter_id} не найден на станции")

    def generate_report(self) -> str:
        """Генерация отчета по станции"""
        report = (
            f"===== ОТЧЕТ ПО СТАНЦИИ {self.station_id} =====\n"
            f"Адрес: {self.location}\n"
            f"Вместимость: {self.capacity}\n"
            f"Доступно самокатов: {len(self.get_available_scooters())}/{len(self.scooters)}\n"
            f"Доступные модели:\n"
        )
        for scooter in self.get_available_scooters():
            report += f"- {scooter}\n"
        return report