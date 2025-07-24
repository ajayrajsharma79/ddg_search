import pytest
from ddg_search import Client, ImageResult, VQDTokenError
import copy

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

# Sample data for mocking
FAKE_VQD_HTML = b"<html><script>vqd='some-fake-vqd-token-12345';</script></html>"
FAKE_IMAGE_JSON = {
    "results": [
        {
            "title": "A Red Panda",
            "image": "https://example.com/red_panda.jpg",
            "thumbnail": "https://example.com/red_panda_thumb.jpg",
            "url": "https://example.com/red_panda_page.html",
            "height": 400,
            "width": 600,
            "source": "DuckDuckGo"
        }
    ],
    "next": "next_page_params_here",
}
FAKE_CRAWL_HTML = """
<html>
    <body>
        <img src="/images/relative_path_img.jpg">
        <img src="https://example.com/full_url_img.png">
    </body>
</html>
"""

@pytest.fixture
def mock_httpx_client(mocker):
    """Fixture to mock the httpx.AsyncClient."""
    mock_client = mocker.AsyncMock()

    mock_post_response = mocker.MagicMock()
    mock_post_response.content = FAKE_VQD_HTML
    mock_post_response.raise_for_status.return_value = None

    mock_get_response = mocker.MagicMock()
    # Simulate pagination: first call returns a result, second call returns empty results and no 'next'
    first_json = copy.deepcopy(FAKE_IMAGE_JSON)
    second_json = {"results": [], "next": None}
    mock_get_response.json.side_effect = [first_json, second_json]
    mock_get_response.text = FAKE_CRAWL_HTML
    mock_get_response.raise_for_status.return_value = None

    mock_client.post.return_value = mock_post_response
    mock_client.get.return_value = mock_get_response

    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    return mock_client

async def test_get_vqd_success(mock_httpx_client):
    """Test that _get_vqd successfully extracts the token."""
    client = Client()
    vqd = await client._get_vqd("test")
    assert vqd == "some-fake-vqd-token-12345"
    mock_httpx_client.post.assert_called_once()

async def test_get_vqd_failure(mocker):
    """Test that _get_vqd raises VQDTokenError on failure."""
    mock_client = mocker.AsyncMock()
    mock_response = mocker.MagicMock()
    mock_response.content = b"<html>no token here</html>"
    mock_client.post.return_value = mock_response
    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    client = Client()
    with pytest.raises(VQDTokenError):
        await client._get_vqd("test")

async def test_asearch_yields_results(mock_httpx_client):
    """Test that asearch yields ImageResult objects."""
    client = Client()
    results = [res async for res in client.asearch("red panda", max_results=1)]
    
    assert len(results) == 1
    result = results[0]
    assert isinstance(result, ImageResult)
    assert result.title == "A Red Panda"
    assert str(result.image_url) == "https://example.com/red_panda.jpg"
    
    mock_httpx_client.post.assert_called_once()
    assert mock_httpx_client.get.call_count == 2

async def test_get_images_from_page(mock_httpx_client):
    """Test that get_images_from_page extracts and resolves image URLs."""
    client = Client()
    page_url = "https://example.com/page.html"
    image_urls = await client.get_images_from_page(page_url)
    
    assert len(image_urls) == 2
    assert "https://example.com/images/relative_path_img.jpg" in image_urls
    assert "https://example.com/full_url_img.png" in image_urls
    mock_httpx_client.get.assert_called_once_with(page_url)