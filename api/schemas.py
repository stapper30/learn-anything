from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    
class UserOut(UserCreate):
    id: int

class Vector(BaseModel):
    id: int
    embedding: list[float]
    user_id: int
    content: str 

    class Config:
        orm_mode = True
