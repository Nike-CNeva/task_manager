from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from services import file_service
from database import get_db
from typing import List

router = APIRouter()

@router.post("/tasks/{task_id}/upload")
async def upload_task_file(task_id: int, file: UploadFile = File(...), file_type: str = "default", db: Session = Depends(get_db)):
    try:
        # Используем сервис для сохранения файла
        saved_file = await file_service.save_file(task_id, file, file_type, db)
        return {"filename": saved_file.filename, "task_id": task_id, "file_type": file_type}  # Ответ в виде обычного словаря
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/tasks/{task_id}/")
def list_task_files(task_id: int, db: Session = Depends(get_db)):
    try:
        # Получаем список файлов для задачи
        files = file_service.get_files_for_task(db, task_id)
        return [{"filename": file.filename, "file_type": file.file_type} for file in files]  # Ответ в виде списка словарей
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/tasks/{task_id}/{file_id}/delete")
def delete_task_file(task_id: int, file_id: int, db: Session = Depends(get_db)):
    return file_service.delete_files(task_id, file_id, db)
