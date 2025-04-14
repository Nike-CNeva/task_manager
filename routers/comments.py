from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services import comment_service
from database import get_db
from typing import List

router = APIRouter()

@router.post("/tasks/{task_id}/", response_model=dict)
def add_task_comment(task_id: int, user_id: int, content: str, db: Session = Depends(get_db)):
    comment_service.add_comment(db, task_id, user_id, content)
    return {"message": "Комментарий добавлен"}

@router.get("/tasks/{task_id}/")
def list_task_comments(task_id: int, db: Session = Depends(get_db)):
    try:
        # Получаем комментарии для задачи
        comments = comment_service.get_comments_for_task(db, task_id)
        
        # Возвращаем список комментариев в виде обычных словарей
        return [{"user": comment.user, "content": comment.content, "created_at": comment.created_at} for comment in comments]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))