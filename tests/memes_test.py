from httpx import AsyncClient
import pytest
from sqlalchemy import insert
from tests.conftest import async_session_maker, Meme

@pytest.mark.asyncio
async def test_read_memes_empty_db(ac_public: AsyncClient):
    """
    Test reading memes from an empty database.

    This test verifies that when the database is empty, a GET request to the '/memes' 
    endpoint returns an empty list. It checks that the response status is 200 and 
    the returned list of memes is empty.

    Parameters:
    - ac_public (AsyncClient): The HTTP client for sending requests to the public API.
    """
    response = await ac_public.get("/memes")
    assert response.status_code == 200
    memes = response.json()
    assert memes == []

@pytest.mark.asyncio
async def test_read_memes(ac_public: AsyncClient):
    """
    Test reading memes from the database.

    This test verifies that memes can be read from the database by first inserting a 
    meme into the database and then making a GET request to the '/memes' endpoint. 
    It checks that the response status is 200 and the returned list of memes contains 
    the inserted meme. It also verifies that the details of the meme can be retrieved 
    by making a GET request to the '/memes/{meme_id}' endpoint.

    Parameters:
    - ac_public (AsyncClient): The HTTP client for sending requests to the public API.
    """
    async with async_session_maker() as session:
        stmt = insert(Meme).values(
            title="Sigma", 
            image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTPj8oOyY30ZpWZQpPN24ptW_JwUQHCisn-wA&s", 
            description="Real sigma"
        )
        await session.execute(stmt)
        await session.commit()
        
    response = await ac_public.get("/memes")
    assert response.status_code == 200
    memes = response.json()
    assert isinstance(memes, list)
    assert len(memes) == 1
     
    meme = memes[0]
    assert "id" in meme
    assert "title" in meme
    assert "image_url" in meme
    assert "description" in meme

    meme_id = meme["id"]
    response = await ac_public.get(f"/memes/{meme_id}")
    assert response.status_code == 200
    meme_detail = response.json()
    
    assert meme_detail["id"] == meme_id
    assert meme_detail["title"] == meme["title"]
    assert meme_detail["image_url"] == meme["image_url"]
    assert meme_detail["description"] == meme["description"]
