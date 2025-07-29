from sqlalchemy import ARRAY, Column, Float, ForeignKey, Integer, String, Boolean, Uuid, func, DateTime
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
class Vector(Base):
    __tablename__ = "vectors"

    id = Column(Uuid, primary_key=True, server_default=func.uuid_generate_v4())
    embedding = Column(ARRAY(Float), nullable=False)  # Store as JSON or similar format
    fk_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    fk_course = Column(Uuid, ForeignKey("courses.id"), nullable=False)
    
class Concept(Base):
    __tablename__ = "concepts"
    
    id = Column(Uuid, primary_key=True, server_default=func.uuid_generate_v4())
    title = Column(String, nullable=False)
    examples = Column(ARRAY(String), nullable=True)
    explanation = Column(String, nullable=False)
    fk_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    fk_course = Column(Uuid, ForeignKey("courses.id"), nullable=False)
    
class Course(Base):
    __tablename__ = "courses"

    id = Column(Uuid, primary_key=True, server_default=func.uuid_generate_v4())
    title = Column(String, nullable=False)
    fk_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String)

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Uuid, primary_key=True, server_default=func.uuid_generate_v4())
    text = Column(String, nullable=False)
    fk_concept = Column(Uuid, ForeignKey("concepts.id"), nullable=False)
    question = Column(String, nullable=False)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    
class UserPydantic(BaseModel):
    id: int
    name: str | None = None
    username: str
    is_active: bool = True
    is_superuser: bool = False
    created: str
