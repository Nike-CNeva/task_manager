import shutil
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from models import Bid, Files
from settings import settings

UPLOAD_DIR = settings.UPLOAD_DIR

def save_file(bid: Bid, file: UploadFile, db: Session):
    bid_folder = UPLOAD_DIR / str(bid.id)
    bid_folder.mkdir(parents=True, exist_ok=True)
    file_path = bid_folder / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    bid_file = Files(
        bid_id=bid.id,
        file_path=str(file_path),
        file_name=file.filename
    )
    db.add(bid_file)
    db.flush()
    return bid_file

def get_files_for_task(db: Session, task_id: int):
    return db.query(Files).filter(Files.task_id == task_id).all()

def delete_files(task_id: int, file_id: int, db: Session):
    file = db.query(Files).filter(Files.id == file_id, Files.task_id == task_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Файл не найден")
    file_path = Path(file.file_path)
    if file_path.exists():
        file_path.unlink()
    db.delete(file)
    db.commit()
