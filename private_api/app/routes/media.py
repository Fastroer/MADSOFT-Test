from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from PIL import Image
from db.dependencies import get_session
from db.models import Meme
from db.schemas import MemeBase
from s3.minio_client import minio_client
from app.dependencies import get_api_key

router = APIRouter(
    prefix="",
    tags=["Memes"],
    dependencies=[Depends(get_api_key)]
)

@router.post("/memes", response_model=MemeBase, status_code=status.HTTP_201_CREATED)
async def create_meme(
    title: str,
    description: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Создает новый мем с загруженным изображением.

    Parameters:
    - title (str): Заголовок мема.
    - description (str): Описание мема.
    - file (UploadFile): Загружаемое изображение.

    Returns:
    - MemeBase: Данные созданного мема.

    Raises:
    - HTTPException(415): Если загруженный файл не является изображением.
    """
    file_name = f"{title}_{file.filename}"
    
    try:
        img = Image.open(file.file)
        img.verify()
    except (IOError, SyntaxError):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Uploaded file is not an image"
        )
    
    minio_client.put_object(
        bucket_name="memes",
        object_name=file_name,
        data=file.file,
        length=-1,
        part_size=10*1024*1024,
        content_type=file.content_type
    )
    
    file_url = f"http://minio:9000/memes/{file_name}"

    meme_data = MemeBase(title=title, description=description, image_url=file_url)
    db_meme = Meme(**meme_data.dict())
    session.add(db_meme)
    await session.commit()
    await session.refresh(db_meme)
    
    return db_meme

@router.put("/memes/{meme_id}", response_model=MemeBase)
async def update_meme(
    meme_id: int,
    file: UploadFile = File(...),
    title: str = None,
    description: str = None,
    session: AsyncSession = Depends(get_session)
):
    """
    Обновляет существующий мем с новым изображением и/или данными.

    Parameters:
    - meme_id (int): Идентификатор мема для обновления.
    - file (UploadFile): Новое изображение для загрузки (опционально).
    - title (str, optional): Новый заголовок мема.
    - description (str, optional): Новое описание мема.

    Returns:
    - MemeBase: Обновленные данные мема.

    Raises:
    - HTTPException(404): Если мем не найден.
    - HTTPException(415): Если загруженный файл не является изображением.
    """
    result = await session.execute(select(Meme).filter(Meme.id == meme_id))
    db_meme = result.scalar()
    if db_meme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meme not found")

    if db_meme.image_url:
        try:
            old_file_name = db_meme.image_url.split("/")[-1]
            minio_client.remove_object(bucket_name="memes", object_name=old_file_name)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete old image")

    if file:
        try:
            img = Image.open(file.file)
            img.verify()
        except (IOError, SyntaxError):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Uploaded file is not an image"
            )
        
        file_name = f"{title}_{file.filename}"
        
        minio_client.put_object(
            bucket_name="memes",
            object_name=file_name,
            data=file.file,
            length=-1,
            part_size=10*1024*1024,
            content_type=file.content_type
        )
        
        file_url = f"http://minio:9000/memes/{file_name}"
        db_meme.image_url = file_url

    if title:
        db_meme.title = title
    if description:
        db_meme.description = description

    await session.commit()
    await session.refresh(db_meme)
    
    return db_meme

@router.delete("/memes/{meme_id}", response_model=MemeBase)
async def delete_meme(
    meme_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Удаляет мем по его идентификатору.

    Parameters:
    - meme_id (int): Идентификатор мема для удаления.

    Returns:
    - MemeBase: Удаленные данные мема.

    Raises:
    - HTTPException(404): Если мем не найден.
    """
    result = await session.execute(select(Meme).filter(Meme.id == meme_id))
    db_meme = result.scalar()
    if db_meme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meme not found")
    
    session.delete(db_meme)
    await session.commit()
    
    return db_meme
