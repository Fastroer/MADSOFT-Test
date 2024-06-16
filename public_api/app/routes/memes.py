from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.dependencies import get_session
from db.models import Meme
from db.schemas import MemeInfo

router = APIRouter(
    prefix="",
    tags=["Memes"]
)

@router.get("/memes", response_model=List[MemeInfo])
async def read_memes(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session)
):
    """
    Возвращает список мемов.

    Parameters:
    - skip (int, optional): Количество мемов для пропуска (по умолчанию 0).
    - limit (int, optional): Максимальное количество мемов для возврата (по умолчанию 10).

    Returns:
    - List[MemeInfo]: Список мемов с указанным смещением и лимитом.

    Raises:
    - HTTPException(404): Если не найдено ни одного мема.
    """
    result = await session.execute(select(Meme).offset(skip).limit(limit))
    memes = result.scalars().all()
    if not memes:
        raise HTTPException(status_code=404, detail="No memes found")
    return memes

@router.get("/memes/{meme_id}", response_model=MemeInfo)
async def read_meme(
    meme_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Возвращает данные одного мема по его идентификатору.

    Parameters:
    - meme_id (int): Идентификатор мема для получения данных.

    Returns:
    - MemeInfo: Данные мема с указанным идентификатором.

    Raises:
    - HTTPException(404): Если мем с указанным идентификатором не найден.
    """
    result = await session.execute(select(Meme).filter(Meme.id == meme_id))
    meme = result.scalar()
    if meme is None:
        raise HTTPException(status_code=404, detail="Meme not found")
    return meme
