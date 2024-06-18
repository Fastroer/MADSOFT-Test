import os
import io
from httpx import AsyncClient
import pytest
from db.models import Meme
from .conftest import async_session_maker

@pytest.mark.asyncio
async def test_create_meme(ac_private: AsyncClient):
    """
    Test the creation of a meme.

    This test verifies that a meme can be successfully created by making a POST request
    to the '/memes/' endpoint. It checks that the response status is 201 and that the
    created meme has the correct title and description. It also verifies that the meme
    is correctly stored in the database.

    Parameters:
    - ac_private (AsyncClient): The HTTP client for sending requests to the private API.
    """
    title = "Funny Meme"
    description = "A very funny meme"
    file_path = "images/test.png"
    
    with open(file_path, "rb") as file:
        file_content = file.read()
    
    response = await ac_private.post(
        "/memes/",
        params={"title": title, "description": description},
        files={"file": ("test.png", io.BytesIO(file_content), "image/png")},
        headers={"Authorization": os.getenv("AUTH_TOKEN")}
    )

    assert response.status_code == 201
    
    created_meme = response.json()
    assert created_meme["title"] == title
    assert created_meme["description"] == description
    assert "id" in created_meme
    
    async with async_session_maker() as session:
        db_meme = await session.get(Meme, created_meme["id"])
        assert db_meme is not None
        assert db_meme.title == title
        assert db_meme.description == description

@pytest.mark.asyncio
async def test_update_meme(ac_private: AsyncClient):
    """
    Test the updating of a meme.

    This test verifies that a meme can be successfully updated by first creating a meme
    and then making a PUT request to the '/memes/{meme_id}' endpoint. It checks that the
    response status is 200 and that the updated meme has the correct new title and description.
    It also verifies that the updated meme is correctly stored in the database.

    Parameters:
    - ac_private (AsyncClient): The HTTP client for sending requests to the private API.
    """
    title = "Funny Meme"
    description = "A very funny meme"
    file_path = "images/test.png"
    
    with open(file_path, "rb") as file:
        file_content = file.read()
    
    create_response = await ac_private.post(
        "/memes/",
        params={"title": title, "description": description},
        files={"file": ("test.png", io.BytesIO(file_content), "image/png")},
        headers={"Authorization": os.getenv("AUTH_TOKEN")}
    )

    assert create_response.status_code == 201
    created_meme = create_response.json()
    meme_id = created_meme["id"]

    new_title = "Updated Meme"
    new_description = "An updated meme"
    new_file_path = "images/update_mem.jpg"
    
    with open(new_file_path, "rb") as new_file:
        new_file_content = new_file.read()

    update_response = await ac_private.put(
        f"/memes/{meme_id}",
        params={"title": new_title, "description": new_description},
        files={"file": ("update_mem.jpg", io.BytesIO(new_file_content), "image/jpg")},
        headers={"Authorization": os.getenv("AUTH_TOKEN")}
    )

    assert update_response.status_code == 200
    
    updated_meme = update_response.json()
    assert updated_meme["title"] == new_title
    assert updated_meme["description"] == new_description
    
    async with async_session_maker() as session:
        db_meme = await session.get(Meme, updated_meme["id"])
        assert db_meme is not None
        assert db_meme.title == new_title
        assert db_meme.description == new_description

@pytest.mark.asyncio
async def test_delete_meme(ac_private: AsyncClient):
    """
    Test the deletion of a meme.

    This test verifies that a meme can be successfully deleted by first creating a meme
    and then making a DELETE request to the '/memes/{meme_id}' endpoint. It checks that the
    response status is 200 and that the deleted meme has the correct ID. It also verifies
    that the meme is no longer present in the database after deletion.

    Parameters:
    - ac_private (AsyncClient): The HTTP client for sending requests to the private API.
    """
    title = "Funny Meme"
    description = "A very funny meme"
    file_path = "images/test.png"
    
    with open(file_path, "rb") as file:
        file_content = file.read()
    
    create_response = await ac_private.post(
        "/memes/",
        params={"title": title, "description": description},
        files={"file": ("test.png", io.BytesIO(file_content), "image/png")},
        headers={"Authorization": os.getenv("AUTH_TOKEN")}
    )

    assert create_response.status_code == 201
    created_meme = create_response.json()
    meme_id = created_meme["id"]

    delete_response = await ac_private.delete(
        f"/memes/{meme_id}",
        headers={"Authorization": os.getenv("AUTH_TOKEN")}
    )

    assert delete_response.status_code == 200
    
    deleted_meme = delete_response.json()
    assert deleted_meme["id"] == meme_id
    
    async with async_session_maker() as session:
        db_meme = await session.get(Meme, meme_id)
        assert db_meme is None
