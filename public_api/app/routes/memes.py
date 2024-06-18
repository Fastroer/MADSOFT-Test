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
    Retrieve a list of memes.

    This endpoint allows users to fetch a paginated list of memes from the database.

    Parameters:
    - skip (int, optional): The number of memes to skip (default is 0).
    - limit (int, optional): The maximum number of memes to return (default is 10).
    - session (AsyncSession): The database session (provided by dependency injection).

    Returns:
    - List[MemeInfo]: A list of memes with the specified offset and limit.

    Raises:
    - HTTPException(404): If no memes are found.
    """
    result = await session.execute(select(Meme).offset(skip).limit(limit))
    memes = result.scalars().all()
    return memes

@router.get("/memes/{meme_id}", response_model=MemeInfo)
async def read_meme(
    meme_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a meme by its ID.

    This endpoint allows users to fetch the details of a specific meme by its unique identifier.

    Parameters:
    - meme_id (int): The ID of the meme to retrieve.
    - session (AsyncSession): The database session (provided by dependency injection).

    Returns:
    - MemeInfo: The details of the meme with the specified ID.

    Raises:
    - HTTPException(404): If a meme with the specified ID is not found.
    """
    result = await session.execute(select(Meme).filter(Meme.id == meme_id))
    meme = result.scalar()
    if meme is None:
        raise HTTPException(status_code=404, detail="Meme not found")
    return meme
