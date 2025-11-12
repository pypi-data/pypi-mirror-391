from datetime import date
from typing_extensions import TypeVar

from pydantic import BaseModel


class AnswersAnalysis(BaseModel):
    answer_id: str
    url: str
    social_platform: str
    type_content: str


AnalysisType = TypeVar("AnalysisType", bound=AnswersAnalysis)


class AnswersStatistics(BaseModel):
    answer_id: str


StatisticsType = TypeVar("StatisticsType", bound=AnswersStatistics)


class AnswersSocialContainer(AnswersStatistics):
    system_id: str
    title: str
    subscribers: int
    creation_date: date | None
    analysis_status: AnswersAnalysis


class AnswersSocialContent(AnswersStatistics):
    system_id: str
    title: str
    views: int
    publish_date: date | None
    analysis_status: AnswersAnalysis
