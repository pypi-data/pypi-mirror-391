from __future__ import annotations
from abc import ABC, abstractmethod
from typing_extensions import Generic

from foxypack.foxypack_abc.answers import AnalysisType, StatisticsType
from foxypack.exceptions import DenialSychronService, DenialAsynchronousService


class FoxyStat(ABC, Generic[AnalysisType]):
    @abstractmethod
    def get_stat(self, answers_analysis: AnalysisType) -> StatisticsType | None:
        raise DenialSychronService(FoxyStat)

    @abstractmethod
    async def get_stat_async(
        self, answers_analysis: AnalysisType
    ) -> StatisticsType | None:
        raise DenialAsynchronousService(FoxyStat)
