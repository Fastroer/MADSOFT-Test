import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from PIL import Image
from db.dependencies import get_session
from db.models import Meme
from db.schemas import MemeBase, MemeInfo
from s3.minio_client import minio_client
from io import BytesIO

router = APIRouter(
    prefix="/memes",
    tags=["Memes"]
)

@router.post("/", response_model=MemeInfo, status_code=status.HTTP_201_CREATED)
async def create_meme(
    title: str,
    description: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new meme.

    This endpoint allows users to upload a new meme with a title, description, and image file.
    The image is verified and stored in a MinIO bucket, and the meme details are saved in the database.

    Args:
        title (str): The title of the meme.
        description (str): The description of the meme.
        file (UploadFile): The image file of the meme.
        session (AsyncSession): The database session.

    Returns:
        MemeInfo: The created meme information.
    """
    bucket = os.getenv("MINIO_BUCKET_NAME", "memes")
    file_name = f"{title}_{file.filename}"
    
    try:
        img = Image.open(file.file)
        img.verify()
        file.file.seek(0)
    except (IOError, SyntaxError):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Uploaded file is not an image"
        )
    
    file_content = await file.read()
    file_size = len(file_content)
    file_stream = BytesIO(file_content)
    
    minio_client.put_object(
        bucket_name=bucket,
        object_name=file_name,
        data=file_stream,
        length=file_size,
        part_size=10*1024*1024,
        content_type=file.content_type
    )
    
    file_url = f"http://{bucket}/{file_name}"

    meme_data = MemeBase(title=title, description=description, image_url=file_url)
    db_meme = Meme(**meme_data.model_dump())
    session.add(db_meme)
    await session.commit()
    await session.refresh(db_meme)
    
    return db_meme

@router.put("/{meme_id}", response_model=MemeInfo)
async def update_meme(
    meme_id: int,
    file: UploadFile = File(...),
    title: str = None,
    description: str = None,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing meme.

    This endpoint allows users to update the details of an existing meme, including the image file.
    The old image is deleted from the MinIO bucket, and the new image is uploaded.

    Args:
        meme_id (int): The ID of the meme to update.
        file (UploadFile): The new image file of the meme.
        title (str, optional): The new title of the meme.
        description (str, optional): The new description of the meme.
        session (AsyncSession): The database session.

    Returns:
        MemeInfo: The updated meme information.
    """
    bucket = os.getenv("MINIO_BUCKET_NAME", "memes")
    result = await session.execute(select(Meme).filter(Meme.id == meme_id))
    db_meme = result.scalar()
    if db_meme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meme not found")

    if db_meme.image_url:
        try:
            old_file_name = db_meme.image_url.split("/")[-1]
            minio_client.remove_object(bucket_name=bucket, object_name=old_file_name)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete old image")

    if file:
        try:
            img = Image.open(file.file)
            img.verify()
            file.file.seek(0)
        except (IOError, SyntaxError):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Uploaded file is not an image"
            )
        
        file_name = f"{title}_{file.filename}"
        file_content = await file.read()
        file_size = len(file_content)
        file_stream = BytesIO(file_content)
        
        minio_client.put_object(
            bucket_name=bucket,
            object_name=file_name,
            data=file_stream,
            length=file_size,
            part_size=10*1024*1024,
            content_type=file.content_type
        )
        
        file_url = f"http://{bucket}/{file_name}"
        db_meme.image_url = file_url

    if title:
        db_meme.title = title
    if description:
        db_meme.description = description

    await session.commit()
    await session.refresh(db_meme)
    
    return db_meme

@router.delete("/{meme_id}", response_model=MemeInfo)
async def delete_meme(
    meme_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an existing meme.

    This endpoint allows users to delete an existing meme. The image file is also removed from the MinIO bucket.

    Args:
        meme_id (int): The ID of the meme to delete.
        session (AsyncSession): The database session.

    Returns:
        MemeInfo: The deleted meme information.
    """
    bucket = os.getenv("MINIO_BUCKET_NAME", "memes")
    result = await session.execute(select(Meme).filter(Meme.id == meme_id))
    db_meme = result.scalar()
    if db_meme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meme not found")

    if db_meme.image_url:
        try:
            file_name = db_meme.image_url.split("/")[-1]
            minio_client.remove_object(bucket_name=bucket, object_name=file_name)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete image from Minio")

    await session.delete(db_meme)
    await session.commit()
    
    return db_meme
