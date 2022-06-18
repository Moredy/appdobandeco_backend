from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import firebase_admin
from typing import Union
from fastapi import FastAPI
from microservices import FoodService
from fastapi.responses import RedirectResponse

databaseURL = 'https://appdobandeco-default-rtdb.firebaseio.com';

cred_obj = firebase_admin.credentials.Certificate('./firebase_credentials.json')
firebase_admin.initialize_app(cred_obj, {'databaseURL': databaseURL})



'''
Configuração de CORS
'''
origins = ["*"]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

app = FastAPI(middleware=middleware)

app.include_router(FoodService.router)

@app.get("/")
def read_root():
    return RedirectResponse("/redoc")
