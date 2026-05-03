from typing import List, Literal

from pydantic import BaseModel, Field

Level = Literal["beginner", "intermediate", "advanced"]


class TextToSpeechRequest(BaseModel):
    text: str = Field(..., min_length=1)


class TextToSpeechResponse(BaseModel):
    audio: str


class SpeechToTextResponse(BaseModel):
    text: str


class AnalysisResult(BaseModel):
    grammar_errors: List[str]
    suggestions: List[str]
    improved_version: str


class SpeakingChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1)
    level: Level = "intermediate"


class SpeakingChatResponse(BaseModel):
    response: str
    user_id: str
    level: Level
    analysis: AnalysisResult | None = None


class AnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1)


class AnalysisResponse(BaseModel):
    analysis: AnalysisResult
