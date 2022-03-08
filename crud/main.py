from ast import For
import email
from email import message
from importlib.machinery import FrozenImporter
from re import U, template
from fastapi import BackgroundTasks, FastAPI, Security, status, HTTPException, Depends, Request, Body, File, UploadFile, Form
from pydantic import BaseModel, EmailStr
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import Base, engine
from sqlalchemy.orm import Session
import models
import schemas
import secrets
import time
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from fastapi_jwt_auth import AuthJWT



Base.metadata.create_all(engine)

app = FastAPI()

templates = Jinja2Templates(directory='htmldirectory')


class Settings(BaseModel):
    authjwt_secret_key:str = '90eb11fd1ecbde3b265222216d12c8646ba56bcf2c285235541df67cc3cfce75'


@AuthJWT.load_config
def get_config():
    return Settings()


class User(BaseModel):
    username:str
    email:str
    password:str

class UserInDB(User):
    hashed_password: str


    class Config:
        schema_extra={
            "example":{
                "username":"sanjana",
                "email":"sanjana@gmail.com",
                "password": "sanjana"
            }
        }

class UserLogin(BaseModel):
    username:str
    password:str

    class Config:
        schema_extra={
            "example":{
                "username":"sanjana",
                "password": "sanjana"
            }
        }
users = []

@app.post("/signup", status_code=201)
def create_user(user:User):
    new_user={
        "username":user.username,
        "email":user.email,
        "password": user.password
    }

    users.append(new_user)
    return new_user


@app.get('/users', response_model=List[User])
def get_users():
    return users


@app.post('/login')
def login(user:UserLogin, Authorize:AuthJWT= Depends()):
    for u in users:
        if (u["username"]==user.username) and (u["password"]==user.password):
            access_token = Authorize.create_access_token(subject=user.username)
            refresh_token = Authorize.create_refresh_token(subject=user.username)

            return {"access_token": access_token, "refresh_token": refresh_token}

        raise HTTPException(status_code='401', detail="Invalid username or password ")




Security=HTTPBasic()


ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

def fake_hash_password(password: str):
    return "fakehashed" + password


@app.post('/token')
async def token(form_data:OAuth2PasswordRequestForm=Depends()):
    return {"access_token": form_data.username +'token'}



@app.get("/")
def root(token:str= Depends(oauth_scheme)):
    print("-------   Todo App Creater  -------")
    return {'the_token':token}


@app.post("/todo-create", status_code=status.HTTP_201_CREATED)
def create_todo(todo: schemas.ToDo ,token:str= Depends(oauth_scheme)):
    print(token)

    session = Session(bind=engine, expire_on_commit=False)
    tododb = models.ToDo(task = todo.task)
    session.add(tododb)
    session.commit()
    id = tododb.id
    session.close()
    return f"created todo item with id {id}"



@app.get("/todo-get-task/{id}")
def read_todo(id: int ,token:str= Depends(oauth_scheme)):

    session = Session(bind=engine, expire_on_commit=False)
    todo = session.query(models.ToDo).get(id)
    session.close()
    if not todo:
        raise HTTPException(status_code=404, detail=f"todo item with id {id} not found")

    return todo


@app.put("/todo-update/{id}")
def update_todo(id: int, task: str ,token:str= Depends(oauth_scheme)):

    session = Session(bind=engine, expire_on_commit=False)

    todo = session.query(models.ToDo).get(id)
    if todo:
        todo.task = task
        session.commit()

    session.close()
    if not todo:
        raise HTTPException(status_code=404, detail=f"todo item with id {id} not found")

    return todo

@app.delete("/todo-delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(id: int ,token:str= Depends(oauth_scheme)):

    session = Session(bind=engine, expire_on_commit=False)
    todo = session.query(models.ToDo).get(id)

    if todo:
        session.delete(todo)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"todo item with id {id} not found")

    return None

@app.get("/todo-all-list")
def read_todo_list(token:str= Depends(oauth_scheme)):
    session = Session(bind=engine, expire_on_commit=False)
    todo_list = session.query(models.ToDo).all()
    session.close()

    return todo_list



