from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.homework_record import HomeworkRecord
from app.schemas.homework import HomeworkGradeRequest, HomeworkGradeResponse, OCRResponse
from app.utils.homework_grader import HomeworkGrader
from app.services.qwen_clients import ocr_image_bytes


class HomeworkService:
    def __init__(self, db: Session):
        self.db = db
        self.grader = HomeworkGrader()

    async def ocr_image(self, file: UploadFile) -> OCRResponse:
        try:
            image_data = await file.read()
            text = ocr_image_bytes(image_data, mime_type=file.content_type or "image/jpeg")
            return OCRResponse(text=text)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OCR失败: {exc}") from exc

    def grade_homework(self, payload: HomeworkGradeRequest) -> HomeworkGradeResponse:
        try:
            result = self.grader.grade(
                subject=payload.subject,
                question=payload.question,
                answer=payload.answer,
            )
            record = HomeworkRecord(
                subject=payload.subject,
                question=payload.question,
                answer=payload.answer,
                score=result.score,
                strengths=result.strengths,
                errors=[item.model_dump() for item in result.errors],
                suggestions=result.suggestions,
                corrected_text=result.corrected_text,
            )
            self.db.add(record)
            self.db.commit()
            return HomeworkGradeResponse(
                score=result.score,
                strengths=result.strengths,
                errors=result.errors,
                suggestions=result.suggestions,
                corrected_text=result.corrected_text,
            )
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批改失败: {exc}") from exc
