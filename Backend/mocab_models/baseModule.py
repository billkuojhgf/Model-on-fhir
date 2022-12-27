from abc import ABC, abstractmethod


class BaseModelInterface(ABC):
    @abstractmethod
    def predict(self, patient_data_object: dict) -> float:
        pass
