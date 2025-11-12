from __future__ import annotations
from abc import ABC, abstractmethod


from foxypack.foxypack_abc.answers import AnswersStatistics, AnswersAnalysis
from foxypack.exceptions import DenialSychronService, DenialAsynchronousService


class FoxyStat(ABC):
    @abstractmethod
    def get_stat(self, answers_analysis: AnswersAnalysis) -> AnswersStatistics | None:
        raise DenialSychronService(self.__class__)

    @abstractmethod
    async def get_stat_async(
        self, answers_analysis: AnswersAnalysis
    ) -> AnswersStatistics | None:
        raise DenialAsynchronousService(self.__class__)
