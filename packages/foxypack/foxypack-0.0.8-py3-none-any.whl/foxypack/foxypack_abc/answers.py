from datetime import date

from pydantic import BaseModel


class AnswersAnalysis(BaseModel):
    answer_id: str
    url: str
    social_platform: str
    type_content: str


class AnswersStatistics(BaseModel):
    answer_id: str


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
