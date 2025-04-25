from pydantic import BaseModel

class Website(BaseModel):
    page_name: str
    summary: str