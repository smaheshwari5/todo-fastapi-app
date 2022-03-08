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


fake_users_db = {
    "maheshwari": {
        "username": "maheshwari",
        "full_name": "sanjana maheshwari",
        "email": "maheshwarisanjana007@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "sanjana": {
        "username": "sanjana",
        "full_name": "sanjana maheshwari",
        "email": "sanjanamaheshwari25@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
}


app = FastAPI()


def fake_hash_password(password: str):
    return "fakehashed" + password

templates = Jinja2Templates(directory='htmldirectory')


ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)


    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}


##########################################################        todo app           ############################################################
@app.get("/")
def root(token:str= Depends(oauth_scheme)):
    print("-------   Todo App Creater  -------")
    return {'the_token':token}




##########################################################        create todo           ############################################################
@app.post("/todo/create", status_code=status.HTTP_201_CREATED)
def create_todo(todo: schemas.ToDo ,token:str= Depends(oauth_scheme)):
    print(token)

    session = Session(bind=engine, expire_on_commit=False)
    tododb = models.ToDo(task = todo.task)
    session.add(tododb)
    session.commit()
    id = tododb.id
    session.close()
    return f"created todo item with id {id}"



##########################################################        get todo          ############################################################
@app.get("/todo/get/{id}")
def read_todo(id: int ,token:str= Depends(oauth_scheme)):

    session = Session(bind=engine, expire_on_commit=False)
    todo = session.query(models.ToDo).get(id)
    session.close()
    if not todo:
        raise HTTPException(status_code=404, detail=f"todo item with id {id} not found")

    return todo



##########################################################        update todo           ############################################################
@app.put("/todo/update/{id}")
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


##########################################################        delete todo          ############################################################
@app.delete("/todo/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
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


##########################################################        list todo           ############################################################
@app.get("/todo/list")
def read_todo_list(token:str= Depends(oauth_scheme)):
    session = Session(bind=engine, expire_on_commit=False)
    todo_list = session.query(models.ToDo).all()
    session.close()

    return todo_list



