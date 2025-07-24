import os
import httpx
import aiofiles
import re
from urllib.parse import urljoin
from typing import AsyncGenerator, Optional
from bs4 import BeautifulSoup

from.exceptions import VQDTokenError, ParsingError, NetworkError
from.models import ImageResult

class Client:
    """An asynchronous client for searching images on DuckDuckGo."""

    def __init__(
        self,
        headers: Optional[dict] = None,
        proxies: Optional[dict] = None,
        timeout: int = 10,
    ):
        """
        Initializes the client.

        Args:
            headers (Optional[dict]): Custom headers to use for requests.
            proxies (Optional[dict]): Proxies to use for requests.
            timeout (int): Request timeout in seconds.
        """
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://duckduckgo.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        if headers:
            default_headers.update(headers)

        if proxies is not None:
            self._http_client = httpx.AsyncClient(
                headers=default_headers, proxies=proxies, timeout=timeout, http2=True
            )
        else:
            self._http_client = httpx.AsyncClient(
                headers=default_headers, timeout=timeout, http2=True
            )

    async def _get_vqd(self, keywords: str) -> str:
        """
        Performs the initial request to DuckDuckGo to get the VQD token.

        Args:
            keywords (str): The search keywords.

        Returns:
            str: The extracted VQD token.

        Raises:
            VQDTokenError: If the VQD token cannot be found in the response.
            NetworkError: If a network-related error occurs.
        """
        try:
            response = await self._http_client.post(
                "https://duckduckgo.com/", data={"q": keywords}
            )
            response.raise_for_status()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error while fetching VQD token: {e}") from e

        # Use regex to extract vqd token from the response content
        try:
            text = response.text if hasattr(response, 'text') else response.content.decode(errors='ignore')
            match = re.search(r"vqd=['\"]([a-zA-Z0-9-]+)['\"]", text)
            if match:
                return match.group(1)
            raise VQDTokenError("Failed to extract VQD token from the response.")
        except Exception as e:
            raise VQDTokenError("Failed to extract VQD token from the response.") from e

    async def asearch(
        self,
        keywords: str,
        max_results: Optional[int] = None,
        region: str = "wt-wt",
        safesearch: str = "moderate",
        timelimit: Optional[str] = None,
        size: Optional[str] = None,
        color: Optional[str] = None,
        type_image: Optional[str] = None,
        layout: Optional[str] = None,
        license_image: Optional[str] = None,
    ) -> AsyncGenerator:
        """
        Asynchronously searches for images and yields results.

        Args:
            keywords (str): The search keywords.
            max_results (Optional[int]): The maximum number of results to yield. Defaults to None (all results).
            region (str): The region to search in (e.g., "us-en"). Defaults to "wt-wt" (no region).
            safesearch (str): Safesearch level ("on", "moderate", "off"). Defaults to "moderate".
            timelimit (Optional[str]): Time limit for results ("Day", "Week", "Month", "Year").
            size (Optional[str]): Image size ("Small", "Medium", "Large", "Wallpaper").
            color (Optional[str]): Image color filter.
            type_image (Optional[str]): Image type ("photo", "clipart", "gif", "transparent", "line").
            layout (Optional[str]): Image layout ("Square", "Tall", "Wide").
            license_image (Optional[str]): Image license type.

        Yields:
            ImageResult: An object representing a single image result.
        """
        vqd = await self._get_vqd(keywords)
        results_yielded = 0
        offset = 0

        # Map user-friendly safesearch terms to API values
        safesearch_map = {"on": "1", "moderate": "-1", "off": "-2"}
        p_value = safesearch_map.get(safesearch.lower(), "-1")

        # Build the filter string for the 'f' parameter
        filters = [
            f"time:{timelimit}" if timelimit else "",
            f"size:{size}" if size else "",
            f"color:{color}" if color else "",
            f"type:{type_image}" if type_image else "",
            f"layout:{layout}" if layout else "",
            f"license:{license_image}" if license_image else "",
        ]
        f_value = ",".join(filter(None, filters))

        while True:
            params = {
                "l": region,
                "o": "json",
                "q": keywords,
                "s": str(offset),
                "p": p_value,
                "f": f_value,
                "vqd": vqd,
            }
            try:
                response = await self._http_client.get(
                    "https://duckduckgo.com/i.js", params=params
                )
                response.raise_for_status()
            except httpx.RequestError as e:
                raise NetworkError(f"Network error during search request: {e}") from e

            try:
                data = response.json()
            except Exception as e:
                raise ParsingError(f"Failed to parse JSON response: {e}") from e

            results = data.get("results",)
            if not results:
                break

            for res in results:
                if max_results is not None and results_yielded >= max_results:
                    return
                try:
                    yield ImageResult.model_validate(res)
                    results_yielded += 1
                except Exception:
                    # Skip invalid results
                    continue
            
            if "next" not in data:
                break
            
            offset += len(results)

    async def get_images_from_page(self, url: str) -> list[str]:
        """
        Fetches a webpage and extracts all absolute image URLs.

        Args:
            url (str): The URL of the webpage to crawl.

        Returns:
            list[str]: A list of absolute URLs to images found on the page.
        
        Raises:
            NetworkError: If a network-related error occurs.
            ParsingError: If the page content cannot be parsed as HTML.
        """
        try:
            response = await self._http_client.get(url)
            response.raise_for_status()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error while fetching page: {e}") from e

        try:
            soup = BeautifulSoup(response.text, "lxml")
            img_tags = soup.find_all("img")
            image_urls = [img.get("src") for img in img_tags if img.get("src")]
            
            # Resolve relative URLs to absolute URLs
            absolute_image_urls = [urljoin(url, img_url) for img_url in image_urls]
            return absolute_image_urls
        except Exception as e:
            raise ParsingError(f"Failed to parse HTML from {url}: {e}") from e

    async def download(self, url: str, output_dir: str, filename: Optional[str] = None):
        """
        Downloads a file from a URL and saves it to a specified directory.

        Args:
            url (str): The URL of the file to download.
            output_dir (str): The directory where the file will be saved.
            filename (Optional[str]): The desired filename. If None, it's inferred from the URL.
        
        Raises:
            NetworkError: If a network-related error occurs during download.
        """
        if not filename:
            filename = url.split("/")[-1].split("?")
            if not filename:
                filename = "downloaded_image"

        output_path = os.path.join(output_dir, filename)
        os.makedirs(output_dir, exist_ok=True)

        try:
            async with self._http_client.stream("GET", url) as response:
                response.raise_for_status()
                async with aiofiles.open(output_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        await f.write(chunk)
        except httpx.RequestError as e:
            raise NetworkError(f"Failed to download {url}: {e}") from e