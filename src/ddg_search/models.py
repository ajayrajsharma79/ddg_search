from pydantic import BaseModel, Field, HttpUrl

class ImageResult(BaseModel):
    """Represents a single image result from a DuckDuckGo search."""
    title: str
    image_url: HttpUrl = Field(alias="image")
    thumbnail_url: HttpUrl = Field(alias="thumbnail")
    source_page_url: HttpUrl = Field(alias="url")
    height: int
    width: int
    source: str