<<<<<<< HEAD
from sqlalchemy.orm import Session
from models import Comment, Task
from typing import List

def add_comment(db: Session, task: Task, content: str):
    comment = Comment(task_id=task.id, comment=content)
    db.add(comment)
    db.flush()
    return comment

def get_comments_for_task(db: Session, task_id: int) -> List[Comment]:
    return db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at.desc()).all()
=======
from sqlalchemy.orm import Session
from models import Comment, Task
from typing import List

def add_comment(db: Session, task: Task, content: str):
    comment = Comment(task_id=task.id, comment=content)
    db.add(comment)
    db.flush()
    return comment

def get_comments_for_task(db: Session, task_id: int) -> List[Comment]:
    return db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at.desc()).all()
>>>>>>> 1488e3832cf2a54b8b2965ef1d819b318057be39
