import pytest
from ddgimage import Client, ImageResult

pytestmark = pytest.mark.asyncio

async def test_asearch_real_data():
    client = Client()
    results = [res async for res in client.asearch("cat", max_results=1)]
    assert len(results) == 1
    result = results[0]
    assert isinstance(result, ImageResult)
    assert result.title
    assert result.image_url.scheme in ("http", "https")
    assert result.thumbnail_url.scheme in ("http", "https")
    assert result.source_page_url.scheme in ("http", "https")
    assert result.height > 0
    assert result.width > 0
    assert result.source
