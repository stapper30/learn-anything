from datetime import datetime, timedelta, timezone
import os
from typing import Annotated

import jwt
from fastapi import Depends, Response, Request, File, UploadFile
from sqlalchemy import Uuid, func
from api.database import get_db
from api import database, file_utilities
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api import models, schemas
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 3  # 1 day
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_user(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    user = result.scalar_one_or_none()
    return user

async def create_and_insert_vectors(
    db: AsyncSession,
    text: str,
    user_id,  # Assuming user ID 8 for demonstration
):
    chunks = file_utilities.chunk_text(text, max_tokens=600)
    chunk_embeddings = file_utilities.embed(chunks)
    
    # print("Chunks:", chunks)
    # print("Chunk Embeddings:", chunk_embeddings)
    
    for embedded_chunk in chunk_embeddings:    
        print("Embedded Chunk:", embedded_chunk)
        db.add(models.Vector(
            embedding=list(embedded_chunk),
            fk_user=user_id,  
            content=chunks[chunk_embeddings.index(embedded_chunk)]
        ))
        await db.commit()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# class User(BaseModel):
#     username: str
#     email: str | None = None
#     full_name: str | None = None
#     disabled: bool | None = None

# class UserInDB(User):
#     hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_vectors(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Vector).where(models.Vector.fk_user == user_id))
    vectors = result.scalars().all()
    return vectors

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = await get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    if current_user.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.on_event("startup")
async def startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.post("/token/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={"sub": user.username + "_refresh"}, expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,         # use False on localhost (no HTTPS)
        samesite="lax",       # "lax" is safest for cross-origin GETs/POSTs
        path="/",
        max_age=60 * 60 * 24 * 7,
    )
    
    print("Access Token:", access_token)
    print("Refresh Token:", refresh_token)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "name": user.name,
        "user_id": user.id,
    }
    
@app.post("/token/refresh")
async def refresh_access_token(
    request: Request,
):
    try:
        print(request.cookies)
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            print("1")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            print("2")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {"access_token": new_access_token, "token_type": "bearer"}

@app.get("/users/me/")
async def read_users_me(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
):
    return current_user

@app.post("/create_course/")
async def upload_file(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    # file: UploadFile = File(...),
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    form = await request.form()
    file = form.get('file')
    
    title = form.get('title')
    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required"
        )
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded"
        )
    print(type(file))
    # if not isinstance(file, UploadFile):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Invalid file type"
    #     )
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded"
        )
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    random_suffix = datetime.now().strftime("%Y%m%d%H%M%S")
    # Save to disk or process as needed
    with open(fr"C:\Users\stapp\Documents\Code\PythonCode\learn_anything\api\uploads\{str(file.filename) + random_suffix}", "wb") as f:
        f.write(await file.read())
    
    db.add(models.Course(
        title=title,
        fk_user=current_user.id,  # Use the current user's ID
        filename=str(file.filename) + random_suffix,
    ))
    await db.commit()
    
    text=file_utilities.extract_text_from_pdf(
        pdf_path=fr"C:\Users\stapp\Documents\Code\PythonCode\learn_anything\api\uploads\{str(file.filename) + random_suffix}",
    )
    
    
    res = await db.execute(select(models.Course).where(models.Course.fk_user == current_user.id, models.Course.title == title))
    
    course = res.scalar_one_or_none()
    
    print("Course:", course)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    chunks = file_utilities.chunk_text(text, max_tokens=5000)
    for chunk in chunks:
        concepts = file_utilities.summarise_chunk(chunk)
        for concept in concepts['concepts']:
            print("Concept:", concept)
            db.add(models.Concept(
                title=concept['title'],
                examples=concept['examples'],
                explanation=concept['explanation'],
                fk_user=current_user.id, 
                fk_course=course.id,  # Use the current course's ID
                )
            ) # Use the current user's ID
    await db.commit()
    
    
    # await create_and_insert_vectors(
    #     db=db,
    #     text=text,
    #     user_id=current_user.id,  # Use the current user's ID
    # )
    
    return {Response().status_code: status.HTTP_200_OK, "message": "File uploaded and processed successfully"}

@app.delete("/courses/{course_id}/")
async def delete_course(
    course_id,  # Assuming course_id is an integer
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    print("Current User ID:", current_user.id)
    print("Deleting course with ID:", course_id)
    
    # Cast course_id to UUID
    try:
        course_uuid = UUID(course_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course ID format"
        )
    
    result = await db.execute(select(models.Course).where(models.Course.id == course_uuid, models.Course.fk_user == current_user.id))
    course = result.scalar_one_or_none()
    
    print("Deleting Course:", course)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you do not have permission to delete it"
        )
    
    await db.delete(course)
    await db.commit()
    
    return {"message": "Course deleted successfully"}

@app.get("/courses/{course_id}/")
async def get_course(
    course_id,  # Assuming course_id is a UUID string
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    
    result = await db.execute(select(models.Course).where(models.Course.id == course_id, models.Course.fk_user == current_user.id))
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you do not have permission to access it"
        )
    
    return course

@app.get("/concepts/{course_id}/")
async def get_concepts(
    course_id: str,  # Assuming course_id is a UUID string
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    print("Current User ID:", current_user.id)
    print("Fetching concepts for user:", current_user.username)
    
    # Check if any concepts exist at all
    total_concepts = await db.execute(select(func.count(models.Concept.id)))
    print("Total concepts in database:", total_concepts.scalar())
    
    # Check the actual query
    query = select(models.Concept).where(models.Concept.fk_user == current_user.id, models.Concept.fk_course == course_id)
    print("SQL Query:", str(query))
    
    result = await db.execute(query)
    concepts = result.scalars().all()
    print("Concepts found for user:", len(concepts))
    return concepts

@app.get("/courses/")
async def get_courses(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.Course).where(models.Course.fk_user == current_user.id))
    courses = result.scalars().all()
    return courses

@app.post("/ask/")
async def ask_question(
    request: dict,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    question = request.get("question")
    context = request.get("context")
    
    print("Question:", question)
    print("Context:", context)
    
    previous_answers = await db.execute(select(models.Answer).where(models.Answer.fk_concept == request.get("concept_id") and models.Answer.fk_concept.in_(select(models.Concept.id).where(models.Concept.fk_user == current_user.id))))
    previous_answers = previous_answers.scalars().all()
    
    texts = "Previous Answers:\n"
    for answer in previous_answers:
        texts += f"Question: {answer.question}\nAnswer: {answer.text}\n\n"
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is required"
        )
        
    if not context:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Context is required"
        )
    
    answerText = file_utilities.ask_gpt(
        question=question,
        context=context + "\n\n" + texts,
    )
    
    answer = models.Answer(
        text=answerText,
        fk_concept=request.get("concept_id"),  # Assuming concept_id is passed in the request
        question=question,
    )
    
    db.add(answer)
    await db.commit()
        
    return {answer}

@app.get("/answers/{concept_id}/")
async def get_answers(
    concept_id: str,  # Assuming concept_id is a UUID string
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.Answer).where(models.Answer.fk_concept == concept_id))
    answers = result.scalars().all()
    return answers

@app.delete("/answers/{answer_id}/")
async def delete_answer(
    answer_id,  # Assuming answer_id is an integer
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.Answer).where(models.Answer.id == answer_id, models.Answer.fk_concept.in_(select(models.Concept.id).where(models.Concept.fk_user == current_user.id))))
    answer = result.scalar_one_or_none()
    
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found or you do not have permission to delete it"
        )
    
    await db.delete(answer)
    await db.commit()
    
    return {"message": "Answer deleted successfully"}

@app.delete("/concepts/{concept_id}/")
async def delete_concept(
    concept_id,  # Assuming concept_id is an integer
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.Concept).where(models.Concept.id == concept_id, models.Concept.fk_user == current_user.id))
    concept = result.scalar_one_or_none()
    
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Concept not found or you do not have permission to delete it"
        )
    
    await db.delete(concept)
    await db.commit()
    
    return {"message": "Concept deleted successfully"}

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

@app.get("/testing/")
async def test_endpoint():
    return {"message": "This is a test endpoint"}

@app.post("/users/register/")
async def register_user(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    existing_user = await get_user(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
            )
        
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.email,
        hashed_password=hashed_password,
        name=user.name,
        is_active=True,
        is_superuser=False
    )
    db.add(new_user)
    await db.commit()


# @app.get("/questions/")
# async def get_questions(
#     user: Annotated[models.User, Depends(get_current_active_user)],
#     db: AsyncSession = Depends(get_db),
# ):

    