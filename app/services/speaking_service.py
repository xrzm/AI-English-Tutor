import base64
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.speaking_session import SpeakingSession
from app.schemas.speaking import (
    AnalysisRequest,
    AnalysisResponse,
    SpeakingChatRequest,
    SpeakingChatResponse,
    SpeechToTextResponse,
    TextToSpeechRequest,
    TextToSpeechResponse,
)
from app.services.qwen_clients import speech_to_text_from_wav_bytes, text_to_speech_bytes
from app.utils.audio import convert_to_wav
from app.utils.speaking_partner import SpeakingPartner


class SpeakingService:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_session(self, user_id: str, level: str) -> SpeakingSession:
        session = self.db.query(SpeakingSession).filter(SpeakingSession.user_id == user_id).first()
        if session is None:
            session = SpeakingSession(user_id=user_id, level=level, history=[])
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
        return session

    async def speech_to_text(self, file: UploadFile) -> SpeechToTextResponse:
        try:
            content = await file.read()
            wav_path = convert_to_wav(content, filename=file.filename or "audio.webm")
            with open(wav_path, "rb") as audio_file:
                text = speech_to_text_from_wav_bytes(audio_file.read())
            Path(wav_path).unlink(missing_ok=True)
            return SpeechToTextResponse(text=text)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"语音识别失败: {exc}") from exc

    def text_to_speech(self, payload: TextToSpeechRequest) -> TextToSpeechResponse:
        try:
            audio_bytes = text_to_speech_bytes(payload.text)
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            return TextToSpeechResponse(audio=audio_base64)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"文字转语音失败: {exc}") from exc

    def chat(self, payload: SpeakingChatRequest) -> SpeakingChatResponse:
        try:
            session = self._get_or_create_session(payload.user_id, payload.level)
            partner = SpeakingPartner(level=session.level, history=session.history)
            response_text = partner.chat(payload.message)
            session.history = partner.history
            session.level = payload.level
            self.db.add(session)
            self.db.commit()

            # Auto-analyze the user's English input
            analysis = None
            try:
                analysis = partner.analyze_speaking(payload.message)
            except Exception:
                pass  # Analysis is best-effort; don't block the chat response

            return SpeakingChatResponse(
                response=response_text,
                user_id=payload.user_id,
                level=payload.level,
                analysis=analysis,
            )
        except Exception as exc:
            self.db.rollback()

            import traceback
            print("REAL ERROR:")
            traceback.print_exc()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"口语对话失败: {exc}"
            ) from exc


    def analyze(self, payload: AnalysisRequest) -> AnalysisResponse:
        try:
            partner = SpeakingPartner(level="intermediate", history=[])
            analysis = partner.analyze_speaking(payload.text)
            return AnalysisResponse(analysis=analysis)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"口语分析失败: {exc}") from exc

    def reset_conversation(self, user_id: str, level: str | None = None) -> dict:
        session = self.db.query(SpeakingSession).filter(SpeakingSession.user_id == user_id).first()
        if session:
            session.history = []
            if level:
                session.level = level
            self.db.add(session)
            self.db.commit()
        return {"user_id": user_id, "message": "对话已重置"}
