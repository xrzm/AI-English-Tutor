from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.common import ApiResponse
from app.schemas.homework import HomeworkGradeRequest, HomeworkGradeResponse, OCRResponse
from app.services.homework_service import HomeworkService

router = APIRouter()


@router.post("/ocr", response_model=ApiResponse[OCRResponse])
async def ocr_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ApiResponse[OCRResponse]:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持图片文件")

    service = HomeworkService(db)
    result = await service.ocr_image(file)
    return ApiResponse.success_response(data=result)


@router.post("/grade", response_model=ApiResponse[HomeworkGradeResponse])
def grade_homework(
    payload: HomeworkGradeRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[HomeworkGradeResponse]:
    service = HomeworkService(db)
    result = service.grade_homework(payload)
    return ApiResponse.success_response(data=result)
