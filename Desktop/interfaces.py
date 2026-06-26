from abc import ABC, abstractmethod
from typing import List, Optional
from PyQt6.QtWidgets import QLineEdit, QTableView

class BaseView(ABC):
    """Базовый абстрактный класс для представлений."""
    
    @abstractmethod
    def setup_ui(self):
        """Настройка UI компонентов."""
        pass

    @abstractmethod
    def bind_events(self):
        """Привязка событий."""
        pass

    @abstractmethod
    def refresh_data(self):
        """Обновление данных."""
        pass

class SearchWidget(ABC):
    """Абстрактный виджет поиска."""
    
    @property
    @abstractmethod
    def search_input(self) -> QLineEdit:
        """Поле ввода для поиска."""
        pass

    @abstractmethod
    def get_search_text(self) -> str:
        """Получить текст поиска."""
        pass

    @abstractmethod
    def clear_search(self):
        """Очистить поле поиска."""
        pass

class DataTableWidget(ABC):
    """Абстрактный виджет таблицы данных."""
    
    @property
    @abstractmethod
    def table_view(self) -> QTableView:
        """Представление таблицы."""
        pass

    @abstractmethod
    def set_data(self, data: List[dict]):
        """Установка данных в таблицу."""
        pass

    @abstractmethod
    def clear_data(self):
        """Очистка таблицы."""
        pass

    @abstractmethod
    def get_selected_row(self) -> Optional[dict]:
        """Получить выбранную строку."""
        pass