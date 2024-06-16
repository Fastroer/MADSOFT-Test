from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String 

Base = declarative_base()

class Meme(Base):
    __tablename__ = "memes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    image_url = Column(String)
    description = Column(String)
