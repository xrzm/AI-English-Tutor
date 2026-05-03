from typing import Optional

import traceback

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.common import ApiResponse
from app.schemas.speaking import (
    AnalysisRequest,
    AnalysisResponse,
    SpeakingChatRequest,
    SpeakingChatResponse,
    SpeechToTextResponse,
    TextToSpeechRequest,
    TextToSpeechResponse,
)
from app.services.speaking_service import SpeakingService

router = APIRouter()


@router.post("/speech-to-text", response_model=ApiResponse[SpeechToTextResponse])
async def speech_to_text(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ApiResponse[SpeechToTextResponse]:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未上传音频文件")
    service = SpeakingService(db)
    result = await service.speech_to_text(file)
    return ApiResponse.success_response(data=result)


@router.post("/text-to-speech", response_model=ApiResponse[TextToSpeechResponse])
def text_to_speech(
    payload: TextToSpeechRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[TextToSpeechResponse]:
    service = SpeakingService(db)
    result = service.text_to_speech(payload)
    return ApiResponse.success_response(data=result)


@router.post("/chat", response_model=ApiResponse[SpeakingChatResponse])
def speaking_chat(
    payload: SpeakingChatRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[SpeakingChatResponse]:
    service = SpeakingService(db)
    result = service.chat(payload)
    return ApiResponse.success_response(data=result)


@router.post("/analyze", response_model=ApiResponse[AnalysisResponse])
def analyze_speaking(
    payload: AnalysisRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[AnalysisResponse]:
    service = SpeakingService(db)
    result = service.analyze(payload)
    return ApiResponse.success_response(data=result)


@router.post("/reset/{user_id}", response_model=ApiResponse[dict])
def reset_conversation(
    user_id: str,
    level: Optional[str] = Body(default=None),
    db: Session = Depends(get_db),
) -> ApiResponse[dict]:
    service = SpeakingService(db)
    result = service.reset_conversation(user_id=user_id, level=level)
    return ApiResponse.success_response(data=result)
