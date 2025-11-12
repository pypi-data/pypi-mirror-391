from abc import ABC, abstractmethod

from foxypack.foxypack_abc.answers import AnalysisType


class FoxyAnalysis(ABC):
    @abstractmethod
    def get_analysis(self, url: str) -> AnalysisType | None:
        pass
