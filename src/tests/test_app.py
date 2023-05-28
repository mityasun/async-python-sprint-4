import os
import sys

import pytest
from fastapi import status
from httpx import AsyncClient

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)
from core.config import app_settings
from src.main import app


app_url = (f'http://{app_settings.project_host}:'
           f'{app_settings.project_port}/api/v1/')


@pytest.mark.asyncio
async def test():

    async def test_api_status():
        """Test get API version."""

        async with AsyncClient(app=app, base_url=app_url) as client:
            response = await client.get('/')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'version': 'v1'}

    async def test_health_db():
        """Test get database availability status."""

        async with AsyncClient(app=app, base_url=app_url) as client:
            response = await client.get('/ping')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'database_connection': True}

    async def test_create_short_url():
        """Test create short url."""

        async with AsyncClient(app=app, base_url=app_url) as client:
            response = await client.post(
                '/', json={"original_url": "https://google.ru"}
            )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        short_id = data.get("short_id")
        assert short_id is not None
        assert response.json() == {
            "short_id": f"{short_id }",
            "short_url": f"{app_url}{short_id}"
        }

    async def test_bulk_create_short_url():
        """Test bulk create short url."""

        async with AsyncClient(app=app, base_url=app_url) as client:
            response = await client.post(
                'shorten', json=[
                    {"original_url": "http://example.com"},
                    {"original_url": "https://google.com"}
                ]
            )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data) == 2

        for item in data:
            short_id = item.get("short_id")
            assert short_id is not None
            assert item == {
                "short_id": f"{short_id}",
                "short_url": f"{app_url}{short_id}"
            }

    async def test_get_original_url():
        """Test return original url by id."""

        async with AsyncClient(app=app, base_url=app_url) as client:
            response = await client.post(
                '/', json={"original_url": "https://google.ru"}
            )
        data = response.json()
        short_id = data.get("short_id")

        async with AsyncClient(app=app, base_url=app_url) as client:
            response = await client.get(f'{short_id}')
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        data = response.json()
        original_url = data.get("original_url")
        assert original_url is not None
        assert response.json() == {"original_url": f"{original_url}"}

    async def test_get_short_url_status():
        """Test get short url status."""

        async with AsyncClient(app=app, base_url=app_url) as client:
            response = await client.post(
                '/', json={"original_url": "https://google.ru"}
            )
        data = response.json()
        short_id = data.get("short_id")

        async with AsyncClient(app=app, base_url=app_url) as client:
            response = await client.get(f'{short_id}/status')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"usage_count": 0}

    async def test_delete_short_url():
        """Test create short url."""

        async with AsyncClient(app=app, base_url=app_url) as client:
            response = await client.post(
                '/', json={"original_url": "https://google.ru"}
            )
        data = response.json()
        short_id = data.get("short_id")

        async with AsyncClient(app=app, base_url=app_url) as client:
            response = await client.delete(f'{short_id}')
        assert response.status_code == status.HTTP_200_OK
        assert short_id is not None
        assert response.json() == {
            "url_delete": f"Short url {short_id} was deleted"
        }

    await test_api_status()
    await test_health_db()
    await test_create_short_url()
    await test_bulk_create_short_url()
    await test_get_original_url()
    await test_get_short_url_status()
    await test_delete_short_url()
