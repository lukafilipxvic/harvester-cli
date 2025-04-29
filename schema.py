from pydantic import BaseModel

class Website(BaseModel):
    page_name: str
    summary: str

class YouTubeVideo(BaseModel):
    video_title: str
    channel: str
    views: int

class Product(BaseModel):
    name: str
    unit: str
    price: float