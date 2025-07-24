# ddg_search

A modern, asynchronous Python client for searching images on DuckDuckGo.

## Features
- Async image search using DuckDuckGo's public endpoints
- Extract image URLs from arbitrary web pages
- Download images asynchronously
- Fully type-annotated and tested

## Installation
```bash
pip install ddg_search
```

## Usage

### Basic Image Search
```python
from ddg_search import Client
import asyncio

async def main():
    client = Client()
    async for result in client.asearch("red panda", max_results=5):
        print(result.title, result.image_url)

asyncio.run(main())
```

### Extract Images from a Web Page
```python
from ddg_search import Client
import asyncio

async def main():
    client = Client()
    images = await client.get_images_from_page("https://example.com")
    print(images)

asyncio.run(main())
```

## Testing
- Unit tests use mock data and run quickly.
- Integration tests (in `test_client_prod.py`) use real DuckDuckGo data and may fail if DuckDuckGo changes their API or blocks automated requests.

## Notes
- This project is not affiliated with DuckDuckGo.
- DuckDuckGo may block automated requests or change their endpoints at any time.

## License
MIT
