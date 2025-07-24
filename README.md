# ddgimage

A modern, asynchronous Python client for searching images on DuckDuckGo.

## Features
- Async image search using DuckDuckGo's public endpoints
- Extract image URLs from arbitrary web pages
- Download images asynchronously
- Fully type-annotated and tested

## Installation
```bash
pip install ddgimage
```

## Usage

### Basic Image Search
```python
from ddgimage import Client
import asyncio

async def main():
    client = Client()
    async for result in client.asearch("red panda", max_results=5):
        print(result.title, result.image_url)

asyncio.run(main())
```

### Extract Images from a Web Page
```python
from ddgimage import Client
import asyncio

async def main():
    client = Client()
    images = await client.get_images_from_page("https://example.com")
    print(images)

asyncio.run(main())
```
## Notes
- This project is not affiliated with DuckDuckGo.
- DuckDuckGo may block automated requests or change their endpoints at any time.

## License
MIT
