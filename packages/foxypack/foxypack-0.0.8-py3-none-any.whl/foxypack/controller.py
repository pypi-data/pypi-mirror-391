from foxypack.foxypack_abc.foxyanalysis import FoxyAnalysis
from foxypack.foxypack_abc.foxystat import FoxyStat

from typing_extensions import Self

from foxypack.foxypack_abc.answers import AnswersAnalysis, AnswersStatistics


class FoxyPack:
    queue_foxy_analysis: list[FoxyAnalysis]
    queue_foxy_stat: list[FoxyStat[AnswersAnalysis]]

    def __init__(
        self,
        queue_foxy_analysis: list[FoxyAnalysis] | None = None,
        queue_foxy_stat: list[FoxyStat[AnswersAnalysis]] | None = None,
    ) -> None:
        self.queue_foxy_analysis = queue_foxy_analysis or []
        self.queue_foxy_stat = queue_foxy_stat or []

    def with_foxy_analysis(self, foxy_analysis: FoxyAnalysis) -> "Self":
        self.queue_foxy_analysis.append(foxy_analysis)
        return self

    def with_foxy_stat(self, foxy_stat: FoxyStat[AnswersAnalysis]) -> "Self":
        self.queue_foxy_stat.append(foxy_stat)
        return self

    def get_analysis(self, url: str) -> AnswersAnalysis | None:
        for foxy_analysis in self.queue_foxy_analysis:
            try:
                result_analysis = foxy_analysis.get_analysis(url=url)
            except Exception:
                continue
            if result_analysis is not None:
                return result_analysis
        return None

    def get_statistics(self, url: str) -> AnswersStatistics | None:
        answers_analysis = self.get_analysis(url)
        if answers_analysis is None:
            return None
        for foxy_stat in self.queue_foxy_stat:
            try:
                result_analysis = foxy_stat.get_stat(answers_analysis=answers_analysis)
            except Exception:
                continue
            if result_analysis is not None:
                return result_analysis
        return None

    async def get_statistics_async(self, url: str) -> AnswersStatistics | None:
        answers_analysis = self.get_analysis(url)
        if answers_analysis is None:
            return None
        for foxy_stat in self.queue_foxy_stat:
            try:
                result_analysis = await foxy_stat.get_stat_async(
                    answers_analysis=answers_analysis
                )
            except Exception:
                continue
            if result_analysis is not None:
                return result_analysis
        return None
