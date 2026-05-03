from typing import List

from pydantic import BaseModel, Field


class HomeworkErrorItem(BaseModel):
    location: str = Field(default="未指定")
    correction: str


class HomeworkGradeRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=100)
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)


class HomeworkGradeResponse(BaseModel):
    score: int
    strengths: List[str]
    errors: List[HomeworkErrorItem]
    suggestions: str
    corrected_text: str


class OCRResponse(BaseModel):
    text: str
