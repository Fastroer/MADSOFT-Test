from pydantic import BaseModel

class MemeBase(BaseModel):
    title: str
    image_url: str
    description: str


class MemeInfo(MemeBase):
    id: int
    
    class Config:
        from_attributes = True
