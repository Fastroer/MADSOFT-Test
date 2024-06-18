from pydantic import BaseModel, ConfigDict

class MemeBase(BaseModel):
    title: str
    image_url: str
    description: str


class MemeInfo(MemeBase):
    id: int
    
    class ConfigDict:
        from_attributes = True
