from abc import ABC, abstractmethod

from foxypack.foxypack_abc.answers import AnswersAnalysis


class FoxyAnalysis(ABC):
    @abstractmethod
    def get_analysis(self, url: str) -> AnswersAnalysis | None:
        pass
