from ast import For
import email
from email import message
from importlib.machinery import FrozenImporter
from re import template
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

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax:float = 10.5


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Optional[str] = None

class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None



items = {
    "food": {"name": "Food", "price": 5000.2},
    "dress": {"name": "Dress", "description": "Best Quality", "price": 6200, "tax": 20.2},
    "toy": {"name": "Toy", "description": "These special toys for childrens", "price": 5000.200, "tax": 5.5, },
}




@app.get("/items/{item_id}/name", response_model=Item, response_model_include = ["name", "description"],)
async def read_item_name(item_id: str):
    return items[item_id]


@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude=["tax"])
async def read_item_public_data(item_id: str):
    return items[item_id]


@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    return item


@app.post("/user/", response_model=UserIn)
async def create_user(user: UserIn):
    return user


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    return user