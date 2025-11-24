from abc import ABC, ABCMeta, abstractmethod
from typing import Dict, Type, Any, Optional


class ScooterMeta(ABCMeta):
    """Метакласс для автоматической регистрации подклассов Scooter"""
    _registry: Dict[str, Type['Scooter']] = {}

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        new_cls = super().__new__(cls, name, bases, attrs)
        if name != "Scooter":  # Исключаем базовый класс
            # Регистрируем с удобными именами
            if name == "CityScooter":
                cls._registry["city"] = new_cls
            elif name == "OffRoadScooter":
                cls._registry["off_road"] = new_cls
            elif name == "FoldableScooter":
                cls._registry["foldable"] = new_cls
            else:
                cls._registry[name.lower()] = new_cls
        return new_cls

    @classmethod
    def get_class(cls, scooter_type: str) -> Optional[Type['Scooter']]:
        return cls._registry.get(scooter_type.lower())


class Scooter(ABC, metaclass=ScooterMeta):
    """Абстрактный базовый класс для всех электросамокатов"""

    def __init__(self, scooter_id: str, model: str, battery_level: float, hourly_rate: float):
        self._scooter_id = scooter_id
        self._model = model
        self._battery_level = battery_level
        self._hourly_rate = hourly_rate
        self._is_available = True

    # Геттеры и сеттеры с валидацией
    @property
    def scooter_id(self) -> str:
        return self._scooter_id

    @property
    def model(self) -> str:
        return self._model

    @property
    def battery_level(self) -> float:
        return self._battery_level

    @battery_level.setter
    def battery_level(self, value: float) -> None:
        if not (0 <= value <= 100):
            raise ValueError("Уровень заряда должен быть в диапазоне 0-100%")
        self._battery_level = value

    @property
    def hourly_rate(self) -> float:
        return self._hourly_rate

    @property
    def is_available(self) -> bool:
        return self._is_available

    @is_available.setter
    def is_available(self, value: bool) -> None:
        self._is_available = value

    @abstractmethod
    def calculate_rental_cost(self, hours: float) -> float:
        """Расчет стоимости аренды"""
        pass

    def __str__(self) -> str:
        return f"Самокат: {self.model}, Заряд: {self.battery_level}%"

    def __lt__(self, other: 'Scooter') -> bool:
        return self.hourly_rate < other.hourly_rate

    def __gt__(self, other: 'Scooter') -> bool:
        return self.hourly_rate > other.hourly_rate


class CityScooter(Scooter):
    """Городской самокат"""

    def __init__(self, scooter_id: str, model: str, battery_level: float, hourly_rate: float, max_speed: float):
        super().__init__(scooter_id, model, battery_level, hourly_rate)
        self._max_speed = max_speed

    @property
    def max_speed(self) -> float:
        return self._max_speed

    def calculate_rental_cost(self, hours: float) -> float:
        base_cost = self.hourly_rate * hours
        # Скидка 10% за аренду более 3 часов
        return base_cost * 0.9 if hours > 3 else base_cost

    def __str__(self) -> str:
        return f"Городской самокат: {self.model}, Макс. скорость: {self.max_speed} км/ч"


class OffRoadScooter(Scooter):
    """Внедорожный самокат"""

    def __init__(self, scooter_id: str, model: str, battery_level: float, hourly_rate: float, tire_type: str):
        super().__init__(scooter_id, model, battery_level, hourly_rate)
        self._tire_type = tire_type

    @property
    def tire_type(self) -> str:
        return self._tire_type

    def calculate_rental_cost(self, hours: float) -> float:
        base_cost = self.hourly_rate * hours
        # Надбавка 15% за внедорожные условия
        return base_cost * 1.15

    def __str__(self) -> str:
        return f"Внедорожный самокат: {self.model}, Тип шин: {self.tire_type}"


class FoldableScooter(Scooter):
    """Складной самокат"""

    def __init__(self, scooter_id: str, model: str, battery_level: float, hourly_rate: float, weight: float):
        super().__init__(scooter_id, model, battery_level, hourly_rate)
        self._weight = weight

    @property
    def weight(self) -> float:
        return self._weight

    def calculate_rental_cost(self, hours: float) -> float:
        base_cost = self.hourly_rate * hours
        # Скидка 5% за легкий вес
        return base_cost * 0.95

    def __str__(self) -> str:
        return f"Складной самокат: {self.model}, Вес: {self.weight} кг"


class ScooterFactory:
    """Фабрика для создания самокатов"""

    @staticmethod
    def create_scooter(
            scooter_type: str,
            scooter_id: str,
            model: str,
            battery_level: float,
            hourly_rate: float,
            **kwargs: Any
    ) -> Scooter:
        scooter_class = ScooterMeta.get_class(scooter_type)
        if not scooter_class:
            raise ValueError(f"Неизвестный тип самоката: {scooter_type}. Доступные типы: city, off_road, foldable")

        # Валидация обязательных параметров для каждого типа
        required_params = {
            'city': ['max_speed'],
            'off_road': ['tire_type'],
            'foldable': ['weight']
        }

        for param in required_params.get(scooter_type.lower(), []):
            if param not in kwargs:
                raise ValueError(f"Отсутствует обязательный параметр {param} для типа {scooter_type}")

        return scooter_class(scooter_id, model, battery_level, hourly_rate, **kwargs)