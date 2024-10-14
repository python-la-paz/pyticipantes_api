from pydantic import BaseModel


class FileBlob(BaseModel):
    name: str
    url: str
    content_type: str