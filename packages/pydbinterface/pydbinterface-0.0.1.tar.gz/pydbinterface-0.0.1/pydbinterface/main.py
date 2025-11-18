from abc import ABC, abstractmethod
from typing import Any

class DBInterface(ABC):

    @abstractmethod
    def create(self, data: Any) -> Any:
        """Inserta un registro y devuelve el objeto creado."""
        pass
    
    @abstractmethod
    def read(self, where: Any) -> Any:
        """Lee registros con filtros (where puede ser cualquier tipo de condición)."""
        pass

    @abstractmethod
    def update(self, where: Any, data: Any) -> Any:
        """Actualiza registros basándose en el filtro 'where'."""
        pass

    @abstractmethod
    def delete(self, where: Any) -> Any:
        """Elimina registros basándose en el filtro 'where'."""
        pass

    @abstractmethod
    def begin_transaction(self) -> None:
        """Inicia una transacción en la base de datos."""
        pass

    @abstractmethod
    def commit_transaction(self) -> None:
        """Confirma la transacción actual."""
        pass

    @abstractmethod
    def rollback_transaction(self) -> None:
        """Revierte la transacción actual."""
        pass
